import os
import time
from enum import Enum
import aiofiles
from aivc.config.config import settings, L
from aivc.tts.common import TTSRsp
from aivc.tts.base import BaseTTS
from aivc.utils.id import get_filename
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

class ElevenLabsVoice(Enum):
    ShannyKids = "qlnUbSLa6XkXV9pK52QP"    # Shanny - Kids American Storyteller
    SparklesForKids = "tapn1QwocNXk3viVSowa"      # Sparkles for Kids
    # https://api.elevenlabs.io/v1/voices
    Matilda = "XrExE9yKIg1WjnnlVkGX"      # Matilda
    Sarah = "EXAVITQu4vr4xnSDxMaL"      # Sarah
    

class ElevenLabsTTS(BaseTTS):
    PROVIDER = "elevenlabs"
    API_KEY_ENV_KEY = "ELEVENLABS_API_KEY"
    
    def __init__(self, trace_sn: str = None):
        super().__init__(trace_sn)
        self.api_key = self.get_api_key()
        self.voice_id = ElevenLabsVoice.Matilda.value
        self.client = ElevenLabs(api_key=self.api_key)
        
        self.voice_settings = VoiceSettings(
            stability=0.75,
            similarity_boost=0.75,
            use_speaker_boost=True
        )
        
        os.makedirs(settings.OUTPUT_ROOT_PATH, exist_ok=True)

    def get_api_key(self) -> str:
        api_key = os.getenv(self.API_KEY_ENV_KEY)
        if not api_key:
            raise ValueError(f"Environment variable {self.API_KEY_ENV_KEY} is not set.")
        return api_key
    
    def get_output_format(self, audio_format: str) -> str:
        if audio_format == "mp3":
            return "mp3_22050_32"
        return "pcm_16000"

    async def tts(self, text: str, audio_format: str = "mp3", compression_rate: int = 10, speed_ratio:float = 1.0) -> TTSRsp:
        try:
            start_time = time.perf_counter()
            L.debug(f"elevenlabs tts req: text={text} trace_sn:{self.trace_sn}")

            # 使用 SDK 生成音频
            # https://elevenlabs.io/docs/developer-guides/models
            audio_stream = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_flash_v2_5",
                voice_settings=self.voice_settings,
                output_format=self.get_output_format(audio_format)
            )

            # 收集音频数据
            audio_data = b""
            for chunk in audio_stream:
                audio_data += chunk
            
            end_time = time.perf_counter()
            
            output_path = os.path.join(
                settings.OUTPUT_ROOT_PATH, 
                get_filename(trace_sn=self.trace_sn, ext=audio_format)
            )

            try:
                async with aiofiles.open(output_path, "wb") as f:
                    await f.write(audio_data)
                    L.info(f"音频数据已保存到 {output_path} text: {text} trace_sn:{self.trace_sn}")
            except Exception as e:
                L.error(f"保存音频数据时出错: {e} text: {text} trace_sn:{self.trace_sn}")
                return TTSRsp(
                    code=-1,
                    message=str(e),
                    input_size=len(text),
                    output_length=0,
                    price=0.0,
                    cost=int((end_time - start_time) * 1000)
                )

            rsp = TTSRsp(
                code=0,
                message="Success",
                text=text,
                audio_data=audio_data,
                audio_format=audio_format,
                channels=1,
                sample_rate=44100,
                audio_path=output_path,
                input_size=float(len(text)),
                output_length=len(audio_data),
                price=0.0,
                cost=int((end_time - start_time) * 1000)
            )
            return rsp

        except Exception as e:
            L.error(f"ElevenLabs TTS error: {str(e)} trace_sn:{self.trace_sn}")
            return TTSRsp(
                code=-1,
                message=f"Error occurred: {str(e)}"
            )
