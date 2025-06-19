from enum import Enum
from aivc.srt.providers.xunfei import XunFeiSRT
from aivc.srt.providers.doubao import DoubaoSRT
from aivc.srt.providers.google import GoogleSRT
from aivc.srt.providers.microsoft import MicrosoftSRT
from aivc.srt.providers.rknn import RknnSRT
from typing import Type
from aivc.srt.base import BaseSRT

class SRTType(Enum):
    XUNFEI = XunFeiSRT
    DOUBAO = DoubaoSRT
    GOOGLE = GoogleSRT
    MICROSOFT = MicrosoftSRT
    RKNN = RknnSRT

    @classmethod
    def from_str(cls, value: str) -> 'SRTType':
        for member in cls:
            if member.value == value:
                return member
        return None
    

class SRTManager:
    @staticmethod
    def get_default_provider() -> str:
        return XunFeiSRT.PROVIDER

    SRT_CLASSES: dict[SRTType, Type[BaseSRT]] = {
        SRTType.XUNFEI: XunFeiSRT,
        SRTType.DOUBAO: DoubaoSRT,
        SRTType.GOOGLE: GoogleSRT,
        SRTType.MICROSOFT: MicrosoftSRT,
        SRTType.RKNN: RknnSRT,
    }

    @staticmethod
    def create_srt(srt_type: SRTType = SRTType.XUNFEI) -> BaseSRT:
        srt_class = SRTManager.SRT_CLASSES[srt_type]
        return srt_class()