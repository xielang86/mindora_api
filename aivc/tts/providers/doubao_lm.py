import base64
import time
import os
import uuid
from aivc.config.config import settings,L
from aivc.tts.common import TTSRsp
from aivc.tts.base import BaseTTS
import aiohttp
import aiofiles
import json
from enum import Enum
from aivc.utils.id import get_filename

class DoubaoLMVoice(Enum):
    MEILINVYOU = "zh_female_meilinvyou_moon_bigtts"     # 魅力女友
    XINLINGJITANG = "zh_female_xinlingjitang_moon_bigtts" # 心灵鸡汤

class DoubaoLMTTS(BaseTTS):
    PROVIDER = "doubao_lm"
    
    APP_ID_ENV_KEY = "DOUBAO_TTS_APP_ID"
    ACCESS_TOKEN_ENV_KEY = "DOUBAO_TTS_ACCESS_TOKEN"
    
    def __init__(self, trace_sn: str = None):
        self.trace_sn = trace_sn
        self.appid = self.get_app_id()
        self.access_token = self.get_access_token()
        self.cluster = "volcano_tts"
        
        self.voice_type = DoubaoLMVoice.XINLINGJITANG.value
        self.host = "openspeech.bytedance.com"
        self.api_url = f"https://{self.host}/api/v1/tts"
        
        # 修改 Authorization header 格式
        self.headers = {
            "Authorization": f"Bearer;{self.access_token}"
        }
        
        os.makedirs(settings.OUTPUT_ROOT_PATH, exist_ok=True)

    def get_app_id(self) -> str:
        app_id = os.getenv(self.APP_ID_ENV_KEY)
        if not app_id:
            raise ValueError(f"Environment variable {self.APP_ID_ENV_KEY} is not set.")
        return app_id

    def get_access_token(self) -> str:
        access_token = os.getenv(self.ACCESS_TOKEN_ENV_KEY)
        if not access_token:
            raise ValueError(f"Environment variable {self.ACCESS_TOKEN_ENV_KEY} is not set.")
        return access_token

    def _build_request(self, text: str, audio_format: str="mp3",compression_rate:int=10, speed_ratio:float = 1.0, text_type:str = None) -> dict:
        reuest = {
            "app": {
                "appid": self.appid,
                "token": "access_token",  
                "cluster": self.cluster
            },
            "user": {
                "uid": "seven_ai"
            },
            "audio": {
                "voice_type": self.voice_type,
                "encoding": audio_format,
                "speed_ratio": speed_ratio,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "operation": "query",
            }
        }

        if text_type:
            reuest["request"]["text_type"] = text_type

        return reuest

    async def tts(self, text: str, audio_format: str="mp3", compression_rate:int=10, speed_ratio:float = 0.8, text_type:str = None) -> TTSRsp:
        try:
            start_time = time.perf_counter()
            
            request_json = self._build_request(
                text=text, 
                audio_format=audio_format,
                compression_rate=compression_rate,
                speed_ratio=speed_ratio,
                text_type=text_type)
            L.debug(f"doubao tts req: {json.dumps(request_json, indent=2, ensure_ascii=False)} trace_sn:{self.trace_sn}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=request_json,
                    headers=self.headers
                ) as resp:
                    resp_json = await resp.json()
                    end_time = time.perf_counter()

                    # 检查响应状态
                    if resp.status != 200 or resp_json.get("code") != 3000:
                        return TTSRsp(
                            code=-1,
                            message=f"Request failed: {resp_json.get('message', 'Unknown error')}"
                        )
                    
                    if "data" not in resp_json:
                        return TTSRsp(
                            code=-1, 
                            message="No data in response"
                        )
                    
                    audio_data = base64.b64decode(resp_json["data"])
                    duration = int(resp_json.get("addition", {}).get("duration", 0))
                    output_path = os.path.join(settings.OUTPUT_ROOT_PATH, get_filename(trace_sn=self.trace_sn, ext=audio_format))

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
                        audio_path=output_path,
                        input_size=float(len(text)),
                        output_length=len(audio_data),
                        price=0.0,
                        cost=int((end_time - start_time) * 1000),
                        duration=duration
                    )
                    if audio_format == "pcm":
                        rsp.sample_format = "S16LE"
                        rsp.bitrate = 256000
                        rsp.channels = 1
                        rsp.sample_rate = 16000
                    return rsp
            
        except Exception as e:
            return TTSRsp(
                code=-1,
                message=f"Error occurred: {str(e)}"
            )