import os
from aivc.chat.llm.base import BaseLLM
from aivc.chat.llm.common import PricingInfo, ModelInfo, LLMRsp
import httpx
from typing import List, Dict, Any
import requests
from datetime import datetime, timedelta
from typing import Tuple
import json
from aivc.config.config import L,settings

class AccessToken:
    def __init__(self, token: str, expire_time: datetime):
        self.token = token
        self.expire_time = expire_time

baidu_access_token = AccessToken(token="", expire_time=None)
class WenxinLLM(BaseLLM):
    base_url_prefix = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/"
    PROVIDER = "baidu"
    API_KEY_ENV = "WENXIN_KEY"
    SECRET_KEY_ENV = "WENXIN_SECRET"

    ERNIE35 = "ERNIE-3.5-8K"
    ERNIE4  = "ERNIE-4.0-8K"
    ERNIE_SPEED_8K = "ERNIE-Speed-8K"
    ERNIE_SPEED_128K = "ERNIE-Speed-128K"
    ERNIE_TINY = "ERNIE-Tiny-8K"

    MODELS = {
        ERNIE35: ModelInfo(
            name=ERNIE35,
            context_size=8000-3000,
            base_url_suffix="completions",
            pricing=PricingInfo(
                input=12/settings.M,
                output=12/settings.M
            )
        ),
        ERNIE4: ModelInfo(
            name=ERNIE4,
            context_size=8000-3000,
            base_url_suffix="completions_pro",
            pricing=PricingInfo(
                input=120/settings.M,
                output=120/settings.M
            )
        ),
        ERNIE_SPEED_8K: ModelInfo(
            name=ERNIE_SPEED_8K,
            context_size=8000-2000,
            base_url_suffix="ernie_speed",
            pricing=PricingInfo(
                input=4/settings.M,
                output=8/settings.M
            )
        ),
        ERNIE_SPEED_128K: ModelInfo(
            name=ERNIE_SPEED_128K,
            context_size=128000-2000,
            base_url_suffix="ernie-speed-128k",
            pricing=PricingInfo(
                input=4/settings.M,
                output=8/settings.M
            )
        ),
        ERNIE_TINY: ModelInfo(
            name=ERNIE_TINY,
            context_size=8000-2000,
            base_url_suffix="ernie-tiny-8k",
            pricing=PricingInfo(
                input=1/settings.M,
                output=1/settings.M
            )
        )}

    def __init__(self, name: str, timeout=60):
        if name not in self.MODELS:
            raise ValueError(f"Model {name} not supported")
        self._name = name
        self._timeout = timeout
        self._token = self.get_access_token()

    def req(self, messages: List[Dict[str, Any]]) -> LLMRsp:
        url = f"{self.base_url_prefix}{self.MODELS[self._name].base_url_suffix}?access_token={self._token}"
        payload = {
            "messages": messages
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        L.debug(f"weinxin req:{json.dumps(payload, ensure_ascii=False)} model:{self._name}")
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload), timeout=self._timeout)
        data = response.json()
        if "error_code" in data:
            raise ValueError(data["error_msg"])
        input_tokens = data["usage"]["prompt_tokens"]
        output_tokens = data["usage"]["completion_tokens"]
        result = LLMRsp(
            content=data["result"],
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            price=self.get_price(input_tokens, output_tokens),
            cost=response.elapsed.total_seconds()
        )
        L.debug(f"weinxin response:{result.content}  model:{self._name}")
        return result

    def req_stream(self, messages: List[Dict[str, Any]]):
        url = f"{self.base_url_prefix}{self.MODELS[self._name].base_url_suffix}?access_token={self._token}"
        payload = {
            "messages": messages,
            "stream": True
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        L.debug(f"weinxin req_stream:{json.dumps(payload, ensure_ascii=False)}  model:{self._name}")
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload), stream=True, timeout=self._timeout)
        result_str = ""
        for chunk in response.iter_lines():
            chunk_str = chunk.decode("utf-8")
            prefix_str = "data: "
            if prefix_str not in chunk_str:
                continue
            chunk_str_clean_data = chunk_str.replace(prefix_str, "")
            chunk_response = json.loads(chunk_str_clean_data).get("result")
            result_str += chunk_response
            yield chunk_response
        L.debug(f"weinxin req_stream response:{result_str}  model:{self._name}")
        yield None

    async def async_req(self, messages: List[Dict[str, Any]]) -> LLMRsp:
        url = f"{self.base_url_prefix}{self.MODELS[self._name].base_url_suffix}?access_token={self._token}"
        payload = {
            "messages": messages
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }        
        async with httpx.AsyncClient() as client:
            L.debug(f"weinxin async_req:{json.dumps(payload, ensure_ascii=False)}  model:{self._name}")
            response = await client.post(url, headers=headers, data=json.dumps(payload), timeout=self._timeout)
            data = response.json()
            if "error_code" in data:
                raise ValueError(data["error_msg"])
            input_tokens = data["usage"]["prompt_tokens"]
            output_tokens = data["usage"]["completion_tokens"]
            result = LLMRsp(
                content=data["result"],
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                price=self.get_price(input_tokens, output_tokens),
                cost=response.elapsed.total_seconds()
            )
            L.debug(f"weinxin async_req response:{result.content}  model:{self._name}")
            return result

    async def async_req_stream(self, messages: List[Dict[str, Any]]):
        url = f"{self.base_url_prefix}{self.MODELS[self._name].base_url_suffix}?access_token={self._token}"
        payload = {
            "messages": messages,
            "stream": True
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        async with httpx.AsyncClient() as client:
            L.debug(f"weinxin async_req_stream:{json.dumps(payload,ensure_ascii=False)} model:{self._name}")
            async with client.stream("POST", url, headers=headers, data=json.dumps(payload), timeout=self._timeout) as response:
                result_str = ""
                async for chunk in response.aiter_lines():
                    chunk_str = chunk
                    prefix_str = "data: "
                    if prefix_str not in chunk_str:
                        continue
                    chunk_str_clean_data = chunk_str.replace(prefix_str, "")
                    chunk_response = json.loads(chunk_str_clean_data).get("result")
                    result_str += chunk_response
                    yield chunk_response
            L.debug(f"weinxin async_req_stream response:{result_str} model:{self._name}")
            yield None

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

    @staticmethod
    def get_access_token() -> str:
        if baidu_access_token.expire_time and baidu_access_token.expire_time > datetime.now():
            baidu_access_token.token

        api_key = os.getenv(WenxinLLM.API_KEY_ENV)
        secret_key = os.getenv(WenxinLLM.SECRET_KEY_ENV)
        error_msg, access_token = WenxinLLM._get_access_token(api_key, secret_key)
        if error_msg:
            raise ValueError(error_msg)
        baidu_access_token.token = access_token
        baidu_access_token.expire_time = datetime.now() + timedelta(days=20)
        return access_token

    @staticmethod
    def _get_access_token(api_key: str, secret_key: str) -> Tuple[str, str]:
        try:
            response = requests.post(
                url=f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}',
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
            )
        except Exception as e:
            return f'Failed to get access token from Baidu: {e}', ""

        resp = response.json()
        if not resp:
            return 'Failed to get access token from Baidu', ""
        if 'error' in resp:           
            return resp["error_description"], ""
        return "",resp['access_token']

    def select_model_by_length(self, length: int, model_name: str) -> str:
        model_context_length = self.MODELS[model_name].context_size
        if length <= model_context_length:
            return model_name
        else:
            if model_name in [self.ERNIE_SPEED_8K, self.ERNIE_TINY]:
                return self.ERNIE_SPEED_128K
        return model_name
