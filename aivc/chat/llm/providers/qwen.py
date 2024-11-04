import os
from aivc.chat.llm.base import BaseLLM
from aivc.chat.llm.common import PricingInfo, ModelInfo, LLMRsp
from openai import OpenAI,AsyncOpenAI
from typing import List, Dict, Any
import time
from aivc.config.config import L,settings

class QWenLLM(BaseLLM):
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    PROVIDER = "ali"
    API_KEY_ENV = "QWEN_KEY"

    QWEN_TURBO = "qwen-turbo"
    QWEN_PLUS  = "qwen-plus"
    QWEN_MAX = "qwen-max"
    QWEN_MAX_LC = "qwen-max-longcontext"
    QWEN_LONG = "qwen-long"

    MODELS = {
        QWEN_LONG: ModelInfo(
            name=QWEN_LONG,
            context_size=32000-4000,
            pricing=PricingInfo(
                input=0.5/settings.M,
                output=2/settings.M
            )
        ),
        QWEN_TURBO: ModelInfo(
            name=QWEN_TURBO,
            context_size=8000-2000,
            pricing=PricingInfo(
                input=2/settings.M,
                output=6/settings.M
            )
        ),
        QWEN_PLUS: ModelInfo(
            name=QWEN_PLUS,
            context_size=32000-2000,
            pricing=PricingInfo(
                input=4/settings.M,
                output=12/settings.M
            )
        ),
        QWEN_MAX: ModelInfo(
            name=QWEN_MAX,
            context_size=8000-2000,
            pricing=PricingInfo(
                input=40/settings.M,
                output=120/settings.M
            )
        ),
        QWEN_MAX_LC: ModelInfo(
            name=QWEN_MAX_LC,
            context_size=32000-4000,
            pricing=PricingInfo(
                input=40/settings.M,
                output=120/settings.M
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
        async for chunk in stream:
            chunk_content = chunk.choices[0].delta.content
            yield chunk_content
            if isinstance(chunk_content, str):
                result += chunk_content
        L.debug(f"{self.PROVIDER} async response:{result}  model:{self._name}")

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
        model_context_length = self.MODELS[model_name].context_size
        if length <= model_context_length:
            return model_name
        else:
            if model_name == self.QWEN_TURBO:
                return self.QWEN_PLUS
            elif model_name == self.QWEN_MAX:
                return self.QWEN_MAX_LC
        return model_name