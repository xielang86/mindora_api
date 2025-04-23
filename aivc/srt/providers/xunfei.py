import websocket
from datetime import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from time import mktime
from concurrent.futures import ThreadPoolExecutor
import asyncio
import os
from aivc.config.config import L
from aivc.srt.base import BaseSRT
from aivc.srt.common import SRTRsp
import traceback

class XunFeiSRT(BaseSRT):
    PROVIDER = "xunfei"

    APP_ID_ENV_KEY="XUNFEI_APP_ID"
    API_KEY_ENV_KEY="XUNFEI_API_KEY"
    API_SECRET_ENV_KEY="XUNFEI_API_SECRET"

    def __init__(self):
        self.CommonArgs = {"app_id": self.get_app_id()}
        self.BusinessArgs = {
            "domain": "iat",
            "language": "zh_cn",
            "accent": "mandarin",
            "vinfo": 1,
            "vad_eos": 10000
        }

        self.result = ""  
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.message_id = ""  # 添加message_id实例变量

    def get_app_id(self) -> str:
        return os.getenv(self.APP_ID_ENV_KEY)
    
    def get_api_key(self) -> str:
        return os.getenv(self.API_KEY_ENV_KEY)
    
    def get_api_secret(self) -> str:
        return os.getenv(self.API_SECRET_ENV_KEY)

    def create_url(self):
        """
        生成WebSocket连接URL，包含认证参数
        """
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接签名字符串
        signature_origin = "host: ws-api.xfyun.cn\n" 
        signature_origin += f"date: {date}\n"
        signature_origin += "GET /v2/iat HTTP/1.1"

        # HMAC-SHA256加密
        signature_sha = hmac.new(
            self.get_api_secret().encode('utf-8'),
            signature_origin.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_sha = base64.b64encode(signature_sha).decode('utf-8')

        # 拼接Authorization参数
        authorization_origin = (
            f'api_key="{self.get_api_key()}", '
            f'algorithm="hmac-sha256", '
            f'headers="host date request-line", '
            f'signature="{signature_sha}"'
        )
        authorization = base64.b64encode(
            authorization_origin.encode('utf-8')
        ).decode('utf-8')

        # 生成最终URL
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        url = f"{url}?{urlencode(v)}"
        return url

    def on_message(self, ws, message):
        """
        处理接收到的消息
        """
        L.debug(f"讯飞语音听写响应:{message}")
        try:
            data = json.loads(message)
            code = data.get("code", -1)
            sid = data.get("sid", "")
            data_content = data.get("data", {})
            status = data_content.get("status", -1)

            if code != 0:
                errMsg = data.get("message", "")
                L.warning(f"讯飞语音听写 sid:{sid} 调用出错: {errMsg} 错误码:{code} message_id:{self.message_id}")
                raise Exception(f"Error {code}: {errMsg}")
            else:
                ws_data = data_content.get("result", {}).get("ws", [])
                # 提取识别结果
                for item in ws_data:
                    for w in item.get("cw", []):
                        self.result += w.get("w", "")
                L.debug(f"讯飞语音听写 sid:{sid} 识别结果: ### {self.result} ### message_id:{self.message_id}")

                # 如果是最后一条消息，则设置完整结果
                if status == self.STATUS_LAST_FRAME:
                    ws.close()
        except Exception as e:
            L.error(f"讯飞语音听写处理响应时出错: {e} message_id:{self.message_id} trace:{traceback.format_exc()}")
            ws.close()

    def on_error(self, ws, error):
        """
        处理WebSocket错误
        """
        L.error(f"讯飞语音听写WebSocket错误: {error} message_id:{self.message_id}")
        L.error(traceback.format_exc())
        ws.close()

    def on_close(self, ws, close_status_code, close_msg):
        """
        处理WebSocket关闭
        """
        L.debug(f"讯飞语音听写WebSocket关闭 message_id:{self.message_id}")

    # 常量定义
    STATUS_FIRST_FRAME = 0        # 第一帧的标识
    STATUS_CONTINUE_FRAME = 1    # 中间帧标识
    STATUS_LAST_FRAME = 2         # 最后一帧的标识

    def on_open(self, ws, audio_path: str, message_id: str):
        """
        当WebSocket连接建立时，开始发送音频数据
        """
        def run():
            frameSize = 8192    # 每一帧的音频大小
            intervel = 0        # 发送音频间隔(单位:s)
            status = self.STATUS_FIRST_FRAME
            L.debug(f"讯飞语音听写WebSocket连接已打开，开始发送音频数据... message_id:{message_id}")

            try:
                with open(audio_path, "rb") as fp:
                    frame_count = 0
                    while True:
                        buf = fp.read(frameSize)
                        if not buf:
                            status = self.STATUS_LAST_FRAME

                        if status == self.STATUS_FIRST_FRAME:
                            data = {
                                "common": self.CommonArgs,
                                "business": self.BusinessArgs,
                                "data": {
                                    "status": self.STATUS_FIRST_FRAME,
                                    "format": "audio/L16;rate=16000",
                                    "audio": base64.b64encode(buf).decode('utf-8'),
                                    "encoding": "raw"
                                }
                            }
                            ws.send(json.dumps(data))
                            frame_count += 1
                            L.debug(f"讯飞语音听写发送第{frame_count}帧 (第一帧) message_id:{message_id}")
                            status = self.STATUS_CONTINUE_FRAME

                        elif status == self.STATUS_CONTINUE_FRAME:
                            data = {
                                "data": {
                                    "status": self.STATUS_CONTINUE_FRAME,
                                    "format": "audio/L16;rate=16000",
                                    "audio": base64.b64encode(buf).decode('utf-8'),
                                    "encoding": "raw"
                                }
                            }
                            ws.send(json.dumps(data))
                            frame_count += 1

                        elif status == self.STATUS_LAST_FRAME:
                            data = {
                                "data": {
                                    "status": self.STATUS_LAST_FRAME,
                                    "format": "audio/L16;rate=16000",
                                    "audio": base64.b64encode(buf).decode('utf-8'),
                                    "encoding": "raw"
                                }
                            }
                            ws.send(json.dumps(data))
                            frame_count += 1
                            L.debug(f"讯飞语音听写发送第{frame_count}帧 (最后一帧) message_id:{message_id}")
                            time.sleep(1)  # 等待处理
                            break

                        time.sleep(intervel)
                    L.debug("讯飞语音听写音频数据发送完毕。 message_id:{message_id}")
            except Exception as e:
                L.debug(f"讯飞语音听写发送音频时出错: {e} message_id:{message_id}")
                ws.close()
                raise

        self.executor.submit(run)

    async def recognize(self, audio_path: str, message_id:str = "") -> SRTRsp:
        """
        异步启动WebSocket连接并等待结果
        """
        # 设置message_id实例变量
        self.message_id = message_id
        start_time = time.perf_counter()

        url = self.create_url()
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # 创建WebSocketApp
        ws_app = websocket.WebSocketApp(
            url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        ws_app.on_open = lambda ws: self.on_open(ws, audio_path, message_id)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(ws_app.run_forever, sslopt={"cert_reqs": ssl.CERT_NONE})
            await asyncio.wrap_future(future)

            try:
                future.result()
            except Exception as e:
                L.debug(f"讯飞语音听写识别过程中出错: {e} message_id:{message_id}")
                cost=int((time.perf_counter() - start_time) * 1000)
                return SRTRsp(
                    code=-1, 
                    message=str(e), 
                    cost=cost)

        cost=int((time.perf_counter() - start_time) * 1000)
        return SRTRsp(
            text=self.result,
            cost=cost)
