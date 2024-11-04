from abc import ABC, abstractmethod
from aivc.tts.common import TTSRsp

class BaseTTS(ABC):
    
    @abstractmethod
    async def tts(self, text: str) -> TTSRsp:
        pass
