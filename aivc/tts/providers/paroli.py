import time
import os
import aiohttp
import aiofiles
from aivc.config.config import settings, L
from aivc.tts.common import TTSRsp
from aivc.tts.base import BaseTTS
from aivc.utils.id import get_filename

class ParoliTTS(BaseTTS):
    PROVIDER = "paroli"
    
    PAROLI_SERVER_HOST_ENV_KEY = "PAROLI_SERVER_HOST"
    PAROLI_SERVER_PORT_ENV_KEY = "PAROLI_SERVER_PORT"
    
    SUPPORTED_FORMATS = ["opus", "wav"]
    
    def __init__(self, trace_sn: str = None):
        super().__init__(trace_sn)
        self.host = self.get_server_host()
        self.port = self.get_server_port()
        self.api_url = f"http://{self.host}:{self.port}/api/v1/synthesise"
        
        os.makedirs(settings.OUTPUT_ROOT_PATH, exist_ok=True)

    def get_server_host(self) -> str:
        return "192.168.0.221"

    def get_server_port(self) -> int:
        return 8848

    def _normalize_audio_format(self, audio_format: str) -> str:
        """标准化音频格式"""
        format_lower = audio_format.lower()
        
        # paroli-server 默认输出 opus 格式
        format_mapping = {
            "mp3": "opus",
            "m4a": "opus", 
            "flac": "opus",
            "ogg": "opus",
            "pcm": "opus",
            "raw": "opus",
        }
        
        normalized_format = format_mapping.get(format_lower, format_lower)
        
        if normalized_format not in self.SUPPORTED_FORMATS:
            L.warning(f"Unsupported audio format: {audio_format}, using default 'opus'")
            return "opus"
        
        return normalized_format

    def _build_request_data(self, text: str) -> dict:
        """构建请求数据 - 根据 curl 命令格式"""
        return {
            "text": text
        }

    async def tts(self, text: str, audio_format: str = "opus", compression_rate: int = 10, speed_ratio: float = 1.0, voice_name: str = None) -> TTSRsp:
        try:
            start_time = time.perf_counter()
            
            original_format = audio_format
            normalized_format = self._normalize_audio_format(audio_format)
            
            if original_format.lower() != normalized_format:
                L.info(f"Audio format converted from {original_format} to {normalized_format} for paroli compatibility")
            
            request_data = self._build_request_data(text=text)
            
            L.debug(f"paroli tts req: {request_data} trace_sn:{self.trace_sn}")
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.api_url,
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    
                    if resp.status != 200:
                        error_text = await resp.text()
                        L.error(f"Paroli server request failed: {resp.status}, {error_text}")
                        return TTSRsp(
                            code=-1,
                            message=f"Request failed with status code: {resp.status}, error: {error_text}"
                        )
                    
                    # 检查响应内容类型
                    content_type = resp.headers.get('content-type', '')
                    L.debug(f"Response content-type: {content_type}")
                    
                    audio_data = await resp.read()
                    end_time = time.perf_counter()
                    
                    if not audio_data:
                        return TTSRsp(
                            code=-1,
                            message="No audio data in response"
                        )
                    
                    # 保存音频文件，使用实际格式
                    output_path = os.path.join(settings.OUTPUT_ROOT_PATH, get_filename(trace_sn=self.trace_sn, ext=normalized_format))
                    
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

                    # 构建响应
                    rsp = TTSRsp(
                        code=0,
                        message="Success",
                        text=text,
                        audio_data=audio_data,
                        audio_format=normalized_format,
                        channels=1,
                        sample_rate=22050,  # 从配置文件中读取的采样率
                        audio_path=output_path,
                        input_size=float(len(text)),
                        output_length=len(audio_data),
                        price=0.0,
                        cost=int((end_time - start_time) * 1000)
                    )
                    
                    # 设置音频格式相关参数
                    if normalized_format == "opus":
                        rsp.sample_format = "OPUS"
                        rsp.bitrate = 64000  # OPUS 典型比特率
                    elif normalized_format == "wav":
                        rsp.sample_format = "S16LE"
                        rsp.bitrate = 352800  # 22050 * 16 * 1
                    
                    return rsp
            
        except aiohttp.ClientConnectorError as e:
            L.error(f"Cannot connect to paroli server: {e}")
            return TTSRsp(
                code=-1,
                message=f"Cannot connect to paroli server at {self.host}:{self.port}. Please ensure the server is running."
            )
        except aiohttp.ClientTimeout as e:
            L.error(f"Paroli server timeout: {e}")
            return TTSRsp(
                code=-1,
                message="Request timeout. Paroli server may be overloaded."
            )
        except Exception as e:
            L.error(f"Paroli TTS error: {e}")
            return TTSRsp(
                code=-1,
                message=f"Error occurred: {str(e)}"
            )
