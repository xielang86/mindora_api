import os
from aivc.chat.llm.base import BaseLLM
from aivc.chat.llm.common import PricingInfo, ModelInfo, LLMRsp
from openai import OpenAI,AsyncOpenAI
from typing import List, Dict, Any
import time
from aivc.config.config import L, settings
import requests
import json

class MoonShotLLM(BaseLLM):
    base_url = "https://api.moonshot.cn/v1"
    PROVIDER = "moonshot"
    API_KEY_ENV = "MOONSHOT_KEY"

    V1_8K = "moonshot-v1-8k"
    V1_32K = "moonshot-v1-32k"
    V1_128K = "moonshot-v1-128k"

    MODELS = {
        V1_8K: ModelInfo(
            name=V1_8K,
            context_size=8000,
            pricing=PricingInfo(
                input=12/settings.M,
                output=12/settings.M
            )
        ),
        V1_32K: ModelInfo(
            name=V1_32K,
            context_size=32000,
            pricing=PricingInfo(
                input=24/settings.M,
                output=24/settings.M
            )
        ),
        V1_128K: ModelInfo(
            name=V1_128K,
            context_size=128000-2000,
            pricing=PricingInfo(
                input=60/settings.M,
                output=60/settings.M
            )
        )
        }

    def __init__(self, name: str, timeout=60):
        if name not in self.MODELS:
            raise ValueError(f"Model {name} not supported")
        self._name = name
        self._timeout = timeout

        self._client = OpenAI(
            api_key = self.get_api_key(),
            base_url=self.base_url,
            timeout=self._timeout
        )

        self._async_client = AsyncOpenAI(
            api_key = self.get_api_key(),
            base_url=self.base_url,
            timeout=self._timeout
        )

    def req(self, messages: List[Dict[str, Any]]) -> LLMRsp:
        start_time = time.time()
        response = self._client.chat.completions.create(
            model=self._name,
            messages=messages)

        input_tokens=response.usage.prompt_tokens
        output_tokens=response.usage.completion_tokens
        result = LLMRsp(
            content=response.choices[0].message.content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            price=self.get_price(input_tokens, output_tokens),
            cost=round(time.time()-start_time, 3)
        )
        L.debug(f"{self.PROVIDER} response:{result.content}  model:{self._name}")
        return result

    def req_stream(self, messages: List[Dict[str, Any]]):
        stream = self._client.chat.completions.create(
            model=self._name,
            messages=messages,
            stream=True)

        result = ""
        for chunk in stream:
            chunk_content = chunk.choices[0].delta.content
            yield chunk_content
            if isinstance(chunk_content, str):
                result += chunk_content
        L.debug(f"{self.PROVIDER} response:{result}  model:{self._name}")

    async def async_req(self, messages: List[Dict[str, Any]]) -> LLMRsp:
        start_time = time.time()
        response = await self._async_client.chat.completions.create(
            model=self._name,
            messages=messages)
        
        input_tokens=response.usage.prompt_tokens
        output_tokens=response.usage.completion_tokens
        result = LLMRsp(
            content=response.choices[0].message.content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            price=self.get_price(input_tokens, output_tokens),
            cost=round(time.time()-start_time, 3)
        )
        L.debug(f"{self.PROVIDER} async response:{result.content}  model:{self._name}")
        return result

    async def async_req_stream(self, messages: List[Dict[str, Any]]):
        stream = await self._async_client.chat.completions.create(
            model=self._name,
            messages=messages,
            stream=True)

        result = ""
        model_extra = {}
        async for chunk in stream:
            chunk_content = chunk.choices[0].delta.content
            yield chunk_content
            if isinstance(chunk_content, str):
                result += chunk_content
            if chunk_content is None:
                model_extra = chunk.choices[0].model_extra
        L.debug(f"{self.PROVIDER} async response:{result}  model:{self._name} model_extra:{json.dumps(model_extra)}")

    def get_api_key(self) -> str:
        return os.getenv(self.API_KEY_ENV)
    
    def context_size(self) -> int:
        return self.MODELS[self._name].context_size
    
    def pricing(self) -> PricingInfo:
        return self.MODELS[self._name].pricing
    
    def get_price(self, 
                input_tokens:int, 
                output_tokens:int) -> float:
        pricing = self.pricing()
        return pricing.input * input_tokens + pricing.output * output_tokens

    def select_model_by_length(self, length: int, model_name: str) -> str:
        model_context_size = self.MODELS[model_name].context_size
        if length <= model_context_size:
            return model_name
        else:
            if length <= self.MODELS[self.V1_32K].context_size:
                return self.V1_32K
            else:
                return self.V1_128K

    def get_token_count_by_api(self, text: str) -> int:
        url = "https://api.moonshot.cn/v1/tokenizers/estimate-token-count"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_api_key()}"
        }
        data = {
            "model": "moonshot-v1-8k",
            "messages": [
                {
                    "role": "user",
                    "content": text
                }
            ]
        }

        response = requests.post(url, json=data, headers=headers)
        # 检查 HTTP 响应状态码
        if response.status_code != 200:
            raise Exception(f"API call failed with status {response.status_code}: {response.text}")

        response_data = response.json()
        total_tokens = response_data.get("data", {}).get("total_tokens")

        if total_tokens is None:
            raise ValueError("Total tokens not found in the response")

        return total_tokens
