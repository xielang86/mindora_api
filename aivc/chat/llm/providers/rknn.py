from aivc.chat.llm.base import BaseLLM
from aivc.chat.llm.common import PricingInfo, ModelInfo, LLMRsp
from typing import List, Dict, Any
import time
import asyncio
import json
import requests
import aiohttp
from aivc.config.config import L, settings
import traceback

class RKNLLM(BaseLLM):
    PROVIDER = "rknn"
    
    QWEN_25_15B = "Qwen2.5-1.5B"
    
    MODELS = {
        QWEN_25_15B: ModelInfo(
            name=QWEN_25_15B,
            context_size=4096-500,
            pricing=PricingInfo(
                input=0,
                output=0
            )
        )
    }

    def __init__(self, name: str, timeout=6):
        if name not in self.MODELS:
            raise ValueError(f"Model {name} not supported")
        self._name = name
        self._timeout = timeout
        
        # RKNN服务器配置
        self.server_url = getattr(settings, 'RKNN_SERVER_URL', 'http://192.168.0.221:9010/rkllm_chat')
        
        # 创建requests会话
        self.session = requests.Session()
        self.session.keep_alive = False
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        
        L.info(f"Initialized RKNN LLM with server URL: {self.server_url}")

    def _truncate_content(self, content: str, max_length: int = 80) -> str:
        """截取内容，如果超过指定长度则从前后各截取一半"""
        if len(content) <= max_length:
            return content
        
        half_length = max_length // 2
        return content[:half_length] + content[-half_length:]

    def _process_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理消息列表，截取过长的content"""
        processed_messages = []
        for msg in messages:
            new_msg = msg.copy()
            if "content" in new_msg and isinstance(new_msg["content"], str):
                new_msg["content"] = self._truncate_content(new_msg["content"])
            processed_messages.append(new_msg)
        return processed_messages

    def _prepare_request_data(self, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        """准备发送给RKNN服务器的请求数据"""
        processed_messages = self._process_messages(messages)
        
        return {
            "model": self._name,
            "messages": processed_messages,
            "stream": stream
        }

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            'Content-Type': 'application/json',
            'Authorization': 'not_required'
        }

    def req(self, messages: List[Dict[str, Any]]) -> LLMRsp:
        start_time = time.time()
        
        try:
            data = self._prepare_request_data(messages, stream=False)
            headers = self._get_headers()
            
            response = self.session.post(
                self.server_url, 
                json=data, 
                headers=headers, 
                timeout=self._timeout,
                verify=False
            )
            
            if response.status_code != 200:
                raise Exception(f"RKNN server error: {response.status_code} - {response.text}")
            
            response_data = response.json()
            content = response_data["choices"][-1]["message"]["content"]
            
            # 简单估算token数量
            input_tokens = self._estimate_tokens(messages)
            output_tokens = self._estimate_tokens([{"role": "assistant", "content": content}])
            
            result = LLMRsp(
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                price=self.get_price(input_tokens, output_tokens),
                cost=round(time.time()-start_time, 3)
            )
            L.debug(f"{self.PROVIDER} response:{result.content} model:{self._name}")
            return result
            
        except Exception as e:
            L.error(f"RKNN request failed: {str(e)}")
            raise Exception(f"RKNN request failed: {str(e)}")

    def req_stream(self, messages: List[Dict[str, Any]]):
        try:
            data = self._prepare_request_data(messages, stream=True)
            headers = self._get_headers()
            
            response = self.session.post(
                self.server_url, 
                json=data, 
                headers=headers, 
                stream=True,
                timeout=self._timeout,
                verify=False
            )
            
            if response.status_code != 200:
                raise Exception(f"RKNN server error: {response.status_code} - {response.text}")
            
            for line in response.iter_lines():
                if line:
                    try:
                        line_data = json.loads(line.decode('utf-8'))
                        if line_data["choices"][-1]["finish_reason"] == "stop":
                            break
                        chunk = line_data["choices"][-1]["delta"]["content"]
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        continue
            
        except Exception as e:
            L.error(f"RKNN stream request failed: {str(e)}")
            raise Exception(f"RKNN stream request failed: {str(e)}")

    async def async_req(self, messages: List[Dict[str, Any]]) -> LLMRsp:
        start_time = time.time()
        
        try:
            data = self._prepare_request_data(messages, stream=False)
            headers = self._get_headers()
            
            # 非流式请求使用较长的总超时时间
            total_timeout = self._timeout * 20  # 单次token超时 * 20作为总超时
            timeout = aiohttp.ClientTimeout(total=total_timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.server_url,
                    json=data,
                    headers=headers,
                    ssl=False
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"RKNN server error: {response.status} - {error_text}")
                    
                    response_data = await response.json()
                    content = response_data["choices"][-1]["message"]["content"]
            
            # 简单估算token数量
            input_tokens = self._estimate_tokens(messages)
            output_tokens = self._estimate_tokens([{"role": "assistant", "content": content}])
            
            result = LLMRsp(
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                price=self.get_price(input_tokens, output_tokens),
                cost=round(time.time()-start_time, 3)
            )
            L.debug(f"{self.PROVIDER} async response:{result.content} model:{self._name}")
            return result
                    
        except Exception as e:
            L.error(f"RKNN async request failed: {str(e)}")
            raise Exception(f"RKNN async request failed: {str(e)}")

    async def async_req_stream(self, messages: List[Dict[str, Any]]):
        L.debug(f"RKNN async stream request with token timeout {self._timeout}s")
        
        try:
            data = self._prepare_request_data(messages, stream=True)
            headers = self._get_headers()
            
            # 设置较长的总超时时间，避免长对话被过早中断
            total_timeout = self._timeout * 50  # 单次token超时 * 50作为总超时
            timeout = aiohttp.ClientTimeout(total=total_timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.server_url,
                    json=data,
                    headers=headers,
                    ssl=False
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        L.error(f"RKNN server error: {response.status} - {error_text}")
                        yield settings.QA_NO_RESULT_RSP
                        return
                    
                    start_time = time.time()
                    last_output_time = start_time
                    chunk_count = 0
                    
                    async for line in response.content:
                        try:
                            current_time = time.time()
                            
                            # 只检查单次token输出间隔超时
                            if chunk_count > 0 and current_time - last_output_time > self._timeout:
                                L.warning(f"RKNN stream inference token timeout after {self._timeout}s")
                                break
                            
                            if line:
                                try:
                                    line_str = line.decode('utf-8').strip()
                                    if not line_str:
                                        continue
                                        
                                    line_data = json.loads(line_str)
                                    if line_data["choices"][-1]["finish_reason"] == "stop":
                                        break
                                    
                                    chunk = line_data["choices"][-1]["delta"]["content"]
                                    if chunk:
                                        last_output_time = current_time
                                        chunk_count += 1
                                        yield chunk
                                        # 让出控制权给事件循环
                                        await asyncio.sleep(0)
                                        
                                except json.JSONDecodeError:
                                    continue
                                    
                        except asyncio.TimeoutError:
                            L.error(f"RKNN stream token timeout after {self._timeout}s")
                            yield settings.QA_NO_RESULT_RSP
                            break
                        except Exception as e:
                            L.error(f"RKNN stream chunk error: {str(e)} stack:{traceback.format_exc()}")
                            yield settings.QA_NO_RESULT_RSP
                            break
                    
        except Exception as e:
            L.error(f"RKNN async stream request failed: {str(e)} stack:{traceback.format_exc()}")

    def get_api_key(self) -> str:
        return "rknn"  # RKNN不需要API密钥
    
    def context_size(self) -> int:
        return self.MODELS[self._name].context_size
    
    def pricing(self) -> PricingInfo:
        return self.MODELS[self._name].pricing
    
    def get_price(self, input_tokens: int, output_tokens: int) -> float:
        pricing = self.pricing()
        return pricing.input * input_tokens + pricing.output * output_tokens

    def select_model_by_length(self, length: int, model_name: str) -> str:
        # RKNN目前只有一个模型，直接返回
        return model_name

    def _estimate_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """简单估算token数量"""
        total_text = ""
        for msg in messages:
            if msg.get("content"):
                total_text += str(msg["content"])
        # 粗略估算：中文字符数 * 0.7
        return int(len(total_text) * 0.7)
