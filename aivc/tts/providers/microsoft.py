import os
import time
import uuid
import aiofiles
import asyncio
import azure.cognitiveservices.speech as speech
from aivc.tts.base import BaseTTS
from aivc.tts.common import TTSRsp
from aivc.config.config import settings, L
from aivc.utils.id import get_filename
from enum import Enum

class MicrosoftVoice(Enum):

    EN_US_JENNY_NEURAL = "en-US-JennyNeural" # 冥想场景
    EN_US_CORA_NEURAL = "en-US-CoraNeural" # 冥想场景
    ZH_CN_XIAOXIAO_NEURAL = "zh-CN-XiaoxiaoNeural" # 晓晓 (普通话，简体)
    ZH_CN_YUNXI_NEURAL = "zh-CN-YunxiNeural"     # 云希 (普通话，简体)

    def __str__(self):
        return self.value


class MicrosoftTTS(BaseTTS):
    PROVIDER = "microsoft"
    AZURE_API_KEY_ENV = "AZURE_API_KEY"
    AZURE_REGION_ENV = "AZURE_REGION"

    def __init__(self, trace_sn: str = None):
        super().__init__(trace_sn)
        self.speech_key = os.getenv(self.AZURE_API_KEY_ENV)
        self.speech_region = os.getenv(self.AZURE_REGION_ENV)

        if not self.speech_key or not self.speech_region:
            L.error(f"Azure Speech Key or Region not set. Please set {self.AZURE_API_KEY_ENV} and {self.AZURE_REGION_ENV} environment variables. Trace SN: {self.trace_sn}")
            raise ValueError("Azure Speech Key or Region not configured.")

        try:
            self.speech_config = speech.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
        except Exception as e:
            L.error(f"Failed to initialize Azure SpeechConfig: {e} trace_sn:{self.trace_sn}")
            raise ValueError(f"Azure SpeechConfig initialization failed: {e}")

        os.makedirs(settings.OUTPUT_ROOT_PATH, exist_ok=True)
        L.info(f"MicrosoftTTS provider initialized. Region: {self.speech_region}. Trace SN: {self.trace_sn}")

    def _map_audio_format(self, audio_format_str: str) -> speech.SpeechSynthesisOutputFormat:
        # Based on https://learn.microsoft.com/en-us/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech.speechsynthesisoutputformat?view=azure-python
        fmt_map = {
            "mp3": speech.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3, # Example, choose appropriate
            "wav": speech.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm,
            "ogg_opus": speech.SpeechSynthesisOutputFormat.Ogg16Khz16BitMonoOpus,
            # Add more mappings as needed
        }
        default_format = speech.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        selected_format = fmt_map.get(audio_format_str.lower(), None)
        if selected_format is None:
            L.warning(f"Unsupported audio format '{audio_format_str}' for Microsoft TTS, defaulting to Audio16Khz32KBitRateMonoMp3. Trace SN: {self.trace_sn}")
            return default_format
        return selected_format
    
    def _format_ssml(self, text: str, voice_name: str, speed_ratio: float) -> str:
        # speed_ratio: 1.0 is normal. <1.0 is slower, >1.0 is faster.
        # SSML rate: "default", "x-slow", "slow", "medium", "fast", "x-fast", or percentage like "+20.00%" or "-20.00%"
        # A speed_ratio of 0.8 means 20% slower (-20%). A speed_ratio of 1.2 means 20% faster (+20%).
        rate_value = "default"
        if speed_ratio != 1.0:
            percentage_change = (speed_ratio - 1.0) * 100
            rate_value = f"{percentage_change:+.2f}%" # Format as +20.00% or -20.00%

        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
          <voice name='{voice_name}'>
            <prosody rate='{rate_value}'>
              {text}
            </prosody>
          </voice>
        </speak>
        """
        # Note: xml:lang should ideally match the language of the voice_name for better synthesis.
        # For simplicity, it's hardcoded here but could be derived from voice_name.
        # E.g., if voice_name is zh-CN-XiaoxiaoNeural, lang should be zh-CN.
        lang_code = voice_name.split('-',1)[0] + '-' + voice_name.split('-')[1] # e.g. "zh-CN"
        ssml = ssml.replace("xml:lang='en-US'", f"xml:lang='{lang_code}'")
        return ssml


    async def tts(self, text: str, audio_format:str, compression_rate:int, speed_ratio:float = 1.0, voice_name: str = None) -> TTSRsp:
        start_time = time.perf_counter()

        if not text:
            return TTSRsp(code=-1, message="Input text cannot be empty.")

        selected_voice_name = voice_name if voice_name else MicrosoftVoice.EN_US_CORA_NEURAL.value
        
        output_format_enum = self._map_audio_format(audio_format)
        self.speech_config.set_speech_synthesis_output_format(output_format_enum)
        # Voice name is set via SSML for finer control with prosody

        ssml_text = self._format_ssml(text, selected_voice_name, speed_ratio)

        output_path = os.path.join(settings.OUTPUT_ROOT_PATH, get_filename(trace_sn=self.trace_sn, ext=audio_format.lower()))
        
        # Using file output directly with SDK
        file_config = speech.audio.AudioOutputConfig(filename=output_path)
        speech_synthesizer = speech.SpeechSynthesizer(speech_config=self.speech_config, audio_config=file_config)

        L.info(f"MicrosoftTTS request (SSML): {ssml_text.strip()}, Output Path: {output_path}, trace_sn:{self.trace_sn}")

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: speech_synthesizer.speak_ssml(ssml_text))
            # Must manually close synthesizer to ensure file is written and resources released
            # See: https://github.com/Azure-Samples/cognitive-services-speech-sdk/issues/1220
            del speech_synthesizer 

            end_time = time.perf_counter()

            if result.reason == speech.ResultReason.SynthesizingAudioCompleted:
                L.info(f"MicrosoftTTS audio saved to {output_path}. Text: '{text[:50]}...', trace_sn:{self.trace_sn}")
                
                audio_data = None
                try:
                    async with aiofiles.open(output_path, "rb") as f:
                        audio_data = await f.read()
                except Exception as e:
                    L.warning(f"Could not read back synthesized audio file {output_path}: {e}, trace_sn:{self.trace_sn}")

                # Duration in ticks (100 nanoseconds). Convert to milliseconds.
                duration_ms = result.audio_duration.total_seconds() * 1000 if result.audio_duration else None

                return TTSRsp(
                    code=0,
                    message="Success",
                    text=text,
                    audio_data=audio_data, # SDK writes to file, optionally read back
                    audio_format=audio_format,
                    audio_path=output_path,
                    input_size=float(len(text)),
                    output_length=len(audio_data) if audio_data else os.path.getsize(output_path) if os.path.exists(output_path) else 0,
                    price=0.0, # Placeholder
                    cost=int((end_time - start_time) * 1000),
                    duration=int(duration_ms) if duration_ms is not None else None
                )
            elif result.reason == speech.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                L.error(f"MicrosoftTTS synthesis canceled. Reason: {cancellation_details.reason}. Error: {cancellation_details.error_details}. Text: '{text[:50]}...', trace_sn:{self.trace_sn}")
                # Clean up potentially empty/partially written file
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except Exception as e_rm:
                        L.warning(f"Failed to remove incomplete file {output_path}: {e_rm}")
                return TTSRsp(
                    code=-1,
                    message=f"MicrosoftTTS synthesis canceled: {cancellation_details.reason} - {cancellation_details.error_details}",
                    text=text,
                    input_size=float(len(text)),
                    cost=int((end_time - start_time) * 1000)
                )
            else: # Other reasons
                L.error(f"MicrosoftTTS synthesis failed. Reason: {result.reason}. Text: '{text[:50]}...', trace_sn:{self.trace_sn}")
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except Exception as e_rm:
                        L.warning(f"Failed to remove incomplete file {output_path}: {e_rm}")
                return TTSRsp(
                    code=-1,
                    message=f"MicrosoftTTS synthesis failed, reason: {result.reason}",
                    text=text,
                    input_size=float(len(text)),
                    cost=int((end_time - start_time) * 1000)
                )

        except Exception as e:
            end_time = time.perf_counter()
            L.error(f"MicrosoftTTS error: {str(e)}. Text: '{text[:50]}...', trace_sn:{self.trace_sn}", exc_info=True)
            if 'speech_synthesizer' in locals() and speech_synthesizer:
                 del speech_synthesizer # Ensure synthesizer is cleaned up on error too
            if os.path.exists(output_path): # Clean up file on general exception
                try:
                    os.remove(output_path)
                except Exception as e_rm:
                    L.warning(f"Failed to remove file {output_path} on error: {e_rm}")
            return TTSRsp(
                code=-1,
                message=f"MicrosoftTTS synthesis failed: {str(e)}",
                text=text,
                input_size=float(len(text)),
                cost=int((end_time - start_time) * 1000)
            )

    def __str__(self):
        return f"MicrosoftTTS Provider (Region: {self.speech_region}, Trace SN: {self.trace_sn})"
