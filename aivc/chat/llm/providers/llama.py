from aivc.chat.llm.base import BaseLLM
from aivc.chat.llm.common import PricingInfo, ModelInfo, LLMRsp
from typing import List, Dict, Any
import time
import requests
import json
import aiohttp
from aivc.config.config import L, settings

class LlamaLLM(BaseLLM):
    PROVIDER = "llama"
    base_url = "http://192.168.0.221:18080"
    # required but ignored for local server
    API_KEY = "llama"

    # Llama模型定义
    QWEN2_5_1_5B_Q4 = "qwen2_5_1_5b_q4"
    LLAMA3_8B = "llama3_8b"
    QWEN2_5_3B = "qwen2_5_3b"

    MODELS = {
        QWEN2_5_1_5B_Q4: ModelInfo(
            name=QWEN2_5_1_5B_Q4,
            context_size=32000-2000,
            pricing=PricingInfo(
                input=0,
                output=0
            ),
            local_path="./qwen2_5_1_5b_q4.gguf"
        ),
        LLAMA3_8B: ModelInfo(
            name=LLAMA3_8B,
            context_size=8000-2000,
            pricing=PricingInfo(
                input=0,
                output=0
            ),
            local_path="./llama3_8b.gguf"
        ),
        QWEN2_5_3B: ModelInfo(
            name=QWEN2_5_3B,
            context_size=32000-2000,
            pricing=PricingInfo(
                input=0,
                output=0
            ),
            local_path="./qwen2_5_3b.gguf"
        )
    }

    def __init__(self, name: str, timeout=60):
        if name not in self.MODELS:
            raise ValueError(f"Model {name} not supported")
        self._name = name
        self._timeout = timeout
        self.api_url = f'{self.base_url}/completion'

    def _messages_to_prompt(self, messages: List[Dict[str, Any]]) -> str:
        """将OpenAI格式的messages转换为llama.cpp格式的prompt"""
        prompt = ""
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "system":
                prompt += f"<|im_start|>system\n{content}<|im_end|>\n"
            elif role == "user":
                prompt += f"<|im_start|>user\n{content}<|im_end|>\n"
            elif role == "assistant":
                prompt += f"<|im_start|>assistant\n{content}<|im_end|>\n"
        
        # 添加assistant开始标记
        prompt += "<|im_start|>assistant\n"
        return prompt

    def req(self, messages: List[Dict[str, Any]]) -> LLMRsp:
        start_time = time.time()
        prompt = self._messages_to_prompt(messages)
        
        payload = {
            'prompt': prompt,
            'stream': False,
            'n_keep': 128,
            'cache_prompt': True,
            'seed': 1234567,
            'temperature': 0.7,
            'top_p': 0.8,
            'max_tokens': 2048
        }

        try:
            response = requests.post(
                url=self.api_url, 
                json=payload, 
                timeout=self._timeout
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get('content', '')
            
            # llama.cpp不返回token数，估算
            input_tokens = len(prompt) // 4  # 粗略估算
            output_tokens = len(content) // 4  # 粗略估算
            
            result = LLMRsp(
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                price=self.get_price(input_tokens, output_tokens),
                cost=round(time.time()-start_time, 3)
            )
            L.debug(f"{self.PROVIDER} response:{result.content}  model:{self._name}")
            return result
            
        except Exception as e:
            L.error(f"Request failed: {e}")
            raise

    def req_stream(self, messages: List[Dict[str, Any]]):
        prompt = self._messages_to_prompt(messages)
        
        payload = {
            'prompt': prompt,
            'stream': True,
            'n_keep': 128,
            'cache_prompt': True,
            'seed': 1234567,
            'temperature': 0.7,
            'top_p': 0.8,
            'max_tokens': 2048
        }

        try:
            with requests.post(url=self.api_url, json=payload, stream=True, timeout=self._timeout) as r:
                r.raise_for_status()
                result = ""
                for line in r.iter_lines():
                    if not line:
                        continue
                    
                    line = line.decode('utf-8').strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line.removeprefix('data: '))
                        content = data.get('content', '')
                        stop = data.get('stop', False)
                        
                        if content:
                            yield content
                            result += content
                        
                        if stop:
                            break
                    except json.JSONDecodeError:
                        continue
                        
                L.debug(f"{self.PROVIDER} stream response:{result}  model:{self._name}")
                
        except Exception as e:
            L.error(f"Stream request failed: {e}")
            raise

    async def async_req(self, messages: List[Dict[str, Any]]) -> LLMRsp:
        start_time = time.time()
        prompt = self._messages_to_prompt(messages)
        
        payload = {
            'prompt': prompt,
            'stream': False,
            'n_keep': 128,
            'cache_prompt': True,
            'seed': 1234567,
            'temperature': 0.7,
            'top_p': 0.8,
            'max_tokens': 2048
        }

        try:
            timeout = aiohttp.ClientTimeout(total=self._timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.api_url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    content = data.get('content', '')
                    
                    # llama.cpp不返回token数，估算
                    input_tokens = len(prompt) // 4  # 粗略估算
                    output_tokens = len(content) // 4  # 粗略估算
                    
                    result = LLMRsp(
                        content=content,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        price=self.get_price(input_tokens, output_tokens),
                        cost=round(time.time()-start_time, 3)
                    )
                    L.debug(f"{self.PROVIDER} async response:{result.content}  model:{self._name}")
                    return result
                    
        except Exception as e:
            L.error(f"Async request failed: {e}")
            raise

    async def async_req_stream(self, messages: List[Dict[str, Any]]):
        prompt = self._messages_to_prompt(messages)
        
        payload = {
            'prompt': prompt,
            'stream': True,
            'n_keep': 128,
            'cache_prompt': True,
            'seed': 1234567,
            'temperature': 0.7,
            'top_p': 0.8,
            'max_tokens': 2048
        }

        try:
            timeout = aiohttp.ClientTimeout(total=self._timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.api_url, json=payload) as response:
                    response.raise_for_status()
                    result = ""
                    
                    async for line in response.content:
                        if not line:
                            continue
                            
                        line = line.decode('utf-8').strip()
                        if not line:
                            continue

                        try:
                            data = json.loads(line.removeprefix('data: '))
                            content = data.get('content', '')
                            stop = data.get('stop', False)
                            
                            if content:
                                yield content
                                result += content
                            
                            if stop:
                                break
                        except json.JSONDecodeError:
                            continue
                            
                    L.debug(f"{self.PROVIDER} async stream response:{result}  model:{self._name}")
                    
        except Exception as e:
            L.error(f"Async stream request failed: {e}")
            raise

    def get_api_key(self) -> str:
        return self.API_KEY
    
    def context_size(self) -> int:
        return self.MODELS[self._name].context_size
    
    def pricing(self) -> PricingInfo:
        return self.MODELS[self._name].pricing
    
    def get_price(self, input_tokens: int, output_tokens: int) -> float:
        pricing = self.pricing()
        return pricing.input * input_tokens + pricing.output * output_tokens

    def select_model_by_length(self, length: int, model_name: str) -> str:
        model_context_size = self.MODELS[model_name].context_size
        if length <= model_context_size:
            return model_name
        else:
            # 如果当前模型上下文不够，尝试切换到更大的模型
            if model_name == self.QWEN2_5_1_5B_Q4:
                return self.QWEN2_5_3B
            elif model_name == self.LLAMA3_8B:
                return self.QWEN2_5_3B
        return model_name
