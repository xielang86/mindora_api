import os
from aivc.srt.base import BaseSRT
from aivc.srt.common import SRTRsp
import time
import azure.cognitiveservices.speech as speechsdk
from aivc.config.config import L

class MicrosoftSRT(BaseSRT):
    PROVIDER = "microsoft"

    AZURE_API_KEY_ENV = "AZURE_API_KEY"
    AZURE_REGION_ENV = "AZURE_REGION"

    def __init__(self):
        self.subscription_key = self.get_subscription_key()
        self.region = self.get_region()

    def get_subscription_key(self) -> str:
        """
        获取 Microsoft Azure 的订阅密钥
        """
        subscription_key = os.getenv(self.AZURE_API_KEY_ENV)
        if not subscription_key:
            raise EnvironmentError(f"{self.AZURE_API_KEY_ENV} environment variable is not set.")
        return subscription_key

    def get_region(self) -> str:
        """
        获取 Microsoft Azure 的区域
        """
        region = os.getenv(self.AZURE_REGION_ENV)
        if not region:
            raise EnvironmentError(f"{self.AZURE_REGION_ENV} environment variable is not set.")
        return region

    async def recognize(self, audio_path: str, message_id: str = "") -> SRTRsp:
        start_time = time.perf_counter()
        L.debug(f"Microsoft Speech-to-Text 开始识别，message_id: {message_id}, audio_path: {audio_path}")

        try:
            # 配置语音识别
            speech_config = speechsdk.SpeechConfig(
                subscription=self.subscription_key, 
                region=self.region,
                speech_recognition_language="zh-CN"
            )
            audio_config = speechsdk.audio.AudioConfig(
                filename=audio_path, 
            )
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, 
                audio_config=audio_config
            )
            L.debug(f"Microsoft Speech-to-Text 识别器初始化完成，message_id: {message_id}")

            # 调用识别 API
            result = speech_recognizer.recognize_once_async().get()
            L.debug(f"Microsoft Speech-to-Text API 调用成功，message_id: {message_id}")

            if result and result.text:
                recognized_text = result.text
                L.debug(f"Microsoft Speech-to-Text 识别结果: {recognized_text}, message_id: {message_id}")
                cost = int((time.perf_counter() - start_time) * 1000)
                return SRTRsp(
                    code=0,
                    message="Success",
                    text=recognized_text,
                    text_length=len(recognized_text),
                    cost=cost,
                    price=0.03 * len(recognized_text)  # 假设每字符价格为0.03
                )
            else:
                L.error(f"Microsoft Speech-to-Text 识别失败，message_id: {message_id}, reason: {result.reason}")
                return SRTRsp(
                    code=-1,
                    message=f"Recognition failed: {result.reason}",
                    text="",
                    text_length=0,
                    cost=int((time.perf_counter() - start_time) * 1000),
                    price=0.0
                )
        except Exception as e:
            L.error(f"Microsoft Speech-to-Text 识别过程中出错，message_id: {message_id}, error: {e}")
            cost = int((time.perf_counter() - start_time) * 1000)
            return SRTRsp(
                code=-1,
                message=str(e),
                text="",
                text_length=0,
                cost=cost,
                price=0.0
            )
