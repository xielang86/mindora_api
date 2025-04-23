from enum import Enum
from aivc.srt.providers.xunfei import XunFeiSRT
from aivc.srt.providers.doubao import DoubaoSRT
from typing import Type
from aivc.srt.base import BaseSRT

class SRTType(Enum):
    XUNFEI = XunFeiSRT
    DOUBAO = DoubaoSRT

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
    }

    @staticmethod
    def create_srt(srt_type: SRTType = SRTType.XUNFEI) -> BaseSRT:
        srt_class = SRTManager.SRT_CLASSES[srt_type]
        return srt_class()