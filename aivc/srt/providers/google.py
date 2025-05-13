import os
from aivc.srt.base import BaseSRT
from aivc.srt.common import SRTRsp
import time
from google.cloud import speech
from aivc.config.config import L

class GoogleSRT(BaseSRT):
    PROVIDER = "google"

    CREDENTIALS_ENV_KEY = "GOOGLE_APPLICATION_CREDENTIALS"

    def __init__(self):
        credentials_path = self.get_credentials_path()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        self.client = speech.SpeechClient()

    def get_credentials_path(self) -> str:
        """
        获取 Google Cloud 的凭证路径
        """
        credentials_path = os.getenv(self.CREDENTIALS_ENV_KEY)
        if not credentials_path:
            raise EnvironmentError(f"{self.CREDENTIALS_ENV_KEY} environment variable is not set.")
        return credentials_path

    async def recognize(self, audio_path: str, message_id: str = "") -> SRTRsp:
        start_time = time.perf_counter()
        L.debug(f"Google Speech-to-Text 开始识别，message_id: {message_id}, audio_path: {audio_path}")

        try:
            # 读取音频文件
            with open(audio_path, "rb") as audio_file:
                content = audio_file.read()
            L.debug(f"Google Speech-to-Text 音频文件读取完成，message_id: {message_id}")

            # 配置识别请求
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                # language_code="zh-CN",  # en-US
                language_code="en-US",
            )
            L.debug(f"Google Speech-to-Text 配置完成，message_id: {message_id}")

            # 调用 Google Speech-to-Text API
            response = self.client.recognize(config=config, audio=audio)
            L.debug(f"Google Speech-to-Text API 调用成功，message_id: {message_id}")

            # 提取识别结果
            recognized_text = ""
            for result in response.results:
                recognized_text += result.alternatives[0].transcript
            L.debug(f"Google Speech-to-Text 识别结果: {recognized_text}, message_id: {message_id}")

            cost = int((time.perf_counter() - start_time) * 1000)
            return SRTRsp(
                code=0,
                message="Success",
                text=recognized_text,
                text_length=len(recognized_text),
                cost=cost,
                price=0.02 * len(recognized_text)  # 假设每字符价格为0.02
            )
        except Exception as e:
            L.error(f"Google Speech-to-Text 识别失败，message_id: {message_id}, error: {e}")
            cost = int((time.perf_counter() - start_time) * 1000)
            return SRTRsp(
                code=-1,
                message=str(e),
                text="",
                text_length=0,
                cost=cost,
                price=0.0
            )
