from abc import ABC, abstractmethod
from aivc.srt.common import SRTRsp

class BaseSRT(ABC):
    
    @abstractmethod
    async def recognize(self, audio_path: str, message_id:str="") -> SRTRsp:
        pass
