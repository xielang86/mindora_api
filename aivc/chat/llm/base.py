from abc import ABC, abstractmethod
from aivc.chat.llm.common import PricingInfo, LLMRsp
from typing import List, Dict, Any

class BaseLLM(ABC):
    @abstractmethod
    def req(self, messages: List[Dict[str, Any]]) -> LLMRsp:
        pass

    @abstractmethod
    def req_stream(self, messages: List[Dict[str, Any]]):
        pass

    @abstractmethod
    async def async_req(self, messages: List[Dict[str, Any]]) -> LLMRsp:
        pass

    @abstractmethod
    async def async_req_stream(self, messages: List[Dict[str, Any]]):
        pass

    @abstractmethod
    def get_api_key(self) -> str:
        pass

    @abstractmethod
    def context_size(self) -> int:
        pass

    @abstractmethod
    def pricing(self) -> PricingInfo:
        pass

    @abstractmethod
    def get_price(self, input_tokens: int, output_tokens: int) -> float:
        pass

    @abstractmethod
    def select_model_by_length(self, length: int, model_name: str) -> str:
        pass