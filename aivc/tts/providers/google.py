import os
import time
import uuid
import json
import aiofiles
from google.cloud import texttospeech
from aivc.tts.base import BaseTTS
from aivc.tts.common import TTSRsp
from aivc.config.config import settings, L
from aivc.utils.id import get_filename
from enum import Enum

class GoogleVoice(Enum):
    """
    Google Cloud Text-to-Speech voices.
    Actual voice names should be added based on Google's documentation.
    Example: en-US-Wavenet-D
    """
    EN_US_STANDARD_A = "en-US-Standard-A"
    EN_US_WAVENET_F = "en-US-Wavenet-F" #声音愉悦且平静
    EN_US_NEURAL2_C = "en-US-Neural2-C" #最先进、最自然、非常接近真人的声音
    ZH_CN_STANDARD_A = "cmn-CN-Standard-A" # 普通话 (中国大陆)
    ZH_CN_WAVENET_A = "cmn-CN-Wavenet-A"   # 普通话 (中国大陆) Wavenet

    def __str__(self):
        return self.value
    
class GoogleTTS(BaseTTS):
    PROVIDER = "google"
    CREDENTIALS_ENV_KEY = "GOOGLE_APPLICATION_CREDENTIALS"

    def __init__(self, trace_sn: str = None):
        super().__init__(trace_sn)
        try:
            credentials_path = self.get_credentials_path()
            os.environ[self.CREDENTIALS_ENV_KEY] = credentials_path
            self.client = texttospeech.TextToSpeechAsyncClient()
            L.info(f"Using Google application credentials from: {credentials_path}. Trace SN: {self.trace_sn}")
        except Exception as e:
            L.error(f"Failed to initialize Google TextToSpeechAsyncClient: {e} trace_sn:{self.trace_sn}")
            raise ValueError(f"Google TTS client initialization failed: {e}")
        
        os.makedirs(settings.OUTPUT_ROOT_PATH, exist_ok=True)
        L.info(f"GoogleTTS provider initialized. Trace SN: {self.trace_sn}")

    def get_credentials_path(self) -> str:
        """
        获取 Google Cloud 的凭证路径
        """
        credentials_path = os.getenv(self.CREDENTIALS_ENV_KEY)
        if not credentials_path:
            raise EnvironmentError(f"{self.CREDENTIALS_ENV_KEY} environment variable is not set.")
        return credentials_path

    def _map_audio_format(self, audio_format_str: str) -> texttospeech.AudioEncoding:
        if (audio_format_str.lower() == "mp3"):
            return texttospeech.AudioEncoding.MP3
        elif (audio_format_str.lower() == "wav"):
            return texttospeech.AudioEncoding.LINEAR16
        elif (audio_format_str.lower() == "ogg_opus"):
            return texttospeech.AudioEncoding.OGG_OPUS
        else:
            L.warning(f"Unsupported audio format '{audio_format_str}' for Google TTS, defaulting to MP3. Trace SN: {self.trace_sn}")
            return texttospeech.AudioEncoding.MP3

    async def tts(self, text: str, audio_format:str, compression_rate:int, speed_ratio:float = 1.0, voice_name: str = None) -> TTSRsp:
        start_time = time.perf_counter()
        req_id = str(uuid.uuid4())
        
        if not text:
            return TTSRsp(code=-1, message="Input text cannot be empty.")

        selected_voice_name = voice_name if voice_name else GoogleVoice.EN_US_NEURAL2_C.value

        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=selected_voice_name.split('-', 1)[0] + '-' + selected_voice_name.split('-')[1], # e.g., "en-US"
            name=selected_voice_name
        )
        
        audio_encoding = self._map_audio_format(audio_format)
        
        audio_config_params = {
            "audio_encoding": audio_encoding,
            "speaking_rate": speed_ratio,
        }
        if audio_encoding == texttospeech.AudioEncoding.LINEAR16:
             audio_config_params["sample_rate_hertz"] = 16000 # Common rate for WAV

        audio_config = texttospeech.AudioConfig(**audio_config_params)

        request_payload = {
            "input": {"text": text},
            "voice": {"language_code": voice_params.language_code, "name": voice_params.name},
            "audio_config": {"audio_encoding": str(audio_encoding), "speaking_rate": speed_ratio}
        }
        L.info(f"GoogleTTS request: {json.dumps(request_payload, ensure_ascii=False)}, req_id: {req_id}, trace_sn:{self.trace_sn}")

        try:
            response = await self.client.synthesize_speech(
                request={"input": synthesis_input, "voice": voice_params, "audio_config": audio_config}
            )
            audio_data = response.audio_content
            end_time = time.perf_counter()
            
            output_filename_ext = audio_format.lower()
            if audio_encoding == texttospeech.AudioEncoding.OGG_OPUS:
                output_filename_ext = "ogg"


            output_path = os.path.join(settings.OUTPUT_ROOT_PATH, get_filename(trace_sn=self.trace_sn, ext=output_filename_ext))

            async with aiofiles.open(output_path, "wb") as f:
                await f.write(audio_data)
            L.info(f"GoogleTTS audio saved to {output_path}. Text: '{text[:50]}...', req_id: {req_id}, trace_sn:{self.trace_sn}")

             
            return TTSRsp(
                code=0,
                message="Success",
                text=text,
                audio_data=audio_data,
                audio_format=audio_format,
                audio_path=output_path,
                input_size=float(len(text)),
                output_length=len(audio_data),
                price=0.0,
                cost=int((end_time - start_time) * 1000),
            )

        except Exception as e:
            end_time = time.perf_counter()
            L.error(f"GoogleTTS error: {str(e)}. Text: '{text[:50]}...', req_id: {req_id}, trace_sn:{self.trace_sn}", exc_info=True)
            return TTSRsp(
                code=-1,
                message=f"GoogleTTS synthesis failed: {str(e)}",
                text=text,
                input_size=float(len(text)),
                cost=int((end_time - start_time) * 1000)
            )

    def __str__(self):
        return f"GoogleTTS Provider (Trace SN: {self.trace_sn})"
