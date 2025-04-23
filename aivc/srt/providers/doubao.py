import base64
import gzip
import hmac
import json
import os
import wave
import uuid
from hashlib import sha256
from io import BytesIO
from urllib.parse import urlparse
import time
import traceback
import websockets

from aivc.config.config import L
from aivc.srt.base import BaseSRT
from aivc.srt.common import SRTRsp

class DoubaoSRT(BaseSRT):
    PROVIDER = "doubao"
    
    APPID_ENV_KEY = "DOUBAO_SRT_APPID"
    CLUSTER_ENV_KEY = "DOUBAO_SRT_CLUSTER"
    TOKEN_ENV_KEY = "DOUBAO_SRT_TOKEN"
    SECRET_ENV_KEY = "DOUBAO_SRT_SECRET"
    
    # 豆包协议常量定义 - 直接作为类常量
    # 协议版本和头部大小
    PROTOCOL_VERSION = 0b0001
    DEFAULT_HEADER_SIZE = 0b0001
    
    # 位偏移定义
    PROTOCOL_VERSION_BITS = 4
    HEADER_BITS = 4
    MESSAGE_TYPE_BITS = 4
    MESSAGE_TYPE_SPECIFIC_FLAGS_BITS = 4
    MESSAGE_SERIALIZATION_BITS = 4
    MESSAGE_COMPRESSION_BITS = 4
    RESERVED_BITS = 8
    
    # 消息类型
    CLIENT_FULL_REQUEST = 0b0001     # 客户端完整请求
    CLIENT_AUDIO_ONLY_REQUEST = 0b0010  # 客户端仅音频请求
    SERVER_FULL_RESPONSE = 0b1001    # 服务器完整响应
    SERVER_ACK = 0b1011             # 服务器确认
    SERVER_ERROR_RESPONSE = 0b1111  # 服务器错误响应
    
    # 序列标志
    NO_SEQUENCE = 0b0000    # 无序列
    POS_SEQUENCE = 0b0001   # 正序列
    NEG_SEQUENCE = 0b0010   # 负序列
    NEG_SEQUENCE_1 = 0b0011 # 负序列1
    
    # 序列化方法
    NO_SERIALIZATION = 0b0000  # 无序列化
    JSON = 0b0001              # JSON序列化
    THRIFT = 0b0011            # THRIFT序列化
    CUSTOM_TYPE = 0b1111      # 自定义类型
    
    # 压缩类型
    NO_COMPRESSION = 0b0000    # 无压缩
    GZIP = 0b0001              # GZIP压缩
    CUSTOM_COMPRESSION = 0b1111  # 自定义压缩
    
    def __init__(self):
        self.ws_url = "wss://openspeech.bytedance.com/api/v2/asr"
        self.success_code = 1000  # 成功码默认是1000
        self.seg_duration = 15000  # 分段时长，单位毫秒
        self.nbest = 1  # 返回的识别结果数量
        self.workflow = "audio_in,resample,partition,vad,fe,decode,itn,nlu_punctuate"
        self.show_language = False
        self.show_utterances = False
        self.result_type = "full"
        self.format = "raw"  
        self.rate = 16000
        self.language = "zh-CN"
        self.bits = 16
        self.channel = 1
        self.codec = "raw"
        self.mp3_seg_size = 10000
        self.auth_method = "token"
        self.result_text = ""

    def get_appid(self) -> str:
        return os.getenv(self.APPID_ENV_KEY, "")
    
    def get_token(self) -> str:
        return os.getenv(self.TOKEN_ENV_KEY, "")
    
    def get_cluster(self) -> str:
        return os.getenv(self.CLUSTER_ENV_KEY, "")
    
    def get_secret(self) -> str:
        return os.getenv(self.SECRET_ENV_KEY, "")

    def generate_header(
        self,
        version=PROTOCOL_VERSION,
        message_type=CLIENT_FULL_REQUEST,
        message_type_specific_flags=NO_SEQUENCE,
        serial_method=JSON,
        compression_type=GZIP,
        reserved_data=0x00,
        extension_header=bytes()
    ):
        """
        生成豆包协议头
        
        协议格式:
        - 第1字节: 版本(4位) + 头部大小(4位)
        - 第2字节: 消息类型(4位) + 消息类型标志(4位)
        - 第3字节: 序列化方法(4位) + 压缩类型(4位)
        - 第4字节: 保留字段(8位)
        - 扩展头: (可选，根据头部大小计算)
        """
        header = bytearray()
        header_size = int(len(extension_header) / 4) + 1
        header.append((version << 4) | header_size)
        header.append((message_type << 4) | message_type_specific_flags)
        header.append((serial_method << 4) | compression_type)
        header.append(reserved_data)
        header.extend(extension_header)
        return header

    def generate_full_default_header(self):
        """生成完整请求的默认头"""
        return self.generate_header()

    def generate_audio_default_header(self):
        """生成音频请求的默认头"""
        return self.generate_header(
            message_type=self.CLIENT_AUDIO_ONLY_REQUEST
        )

    def generate_last_audio_default_header(self):
        """生成最后一个音频请求的默认头"""
        return self.generate_header(
            message_type=self.CLIENT_AUDIO_ONLY_REQUEST,
            message_type_specific_flags=self.NEG_SEQUENCE
        )
    
    def parse_response(self, res):
        """
        解析豆包响应
        
        响应格式:
        - 头部: 协议版本(4位) + 头部大小(4位) + 消息类型(4位) + 类型标志(4位) + 序列化方法(4位) + 压缩类型(4位) + 保留字段(8位) + 扩展头
        - 负载: 根据消息类型有不同结构
        """
        protocol_version = res[0] >> 4
        header_size = res[0] & 0x0f
        message_type = res[1] >> 4
        message_type_specific_flags = res[1] & 0x0f
        serialization_method = res[2] >> 4
        message_compression = res[2] & 0x0f
        reserved = res[3]
        header_extensions = res[4:header_size * 4]
        payload = res[header_size * 4:]
        result = {}
        payload_msg = None
        payload_size = 0
        
        if message_type == self.SERVER_FULL_RESPONSE:
            payload_size = int.from_bytes(payload[:4], "big", signed=True)
            payload_msg = payload[4:]
        elif message_type == self.SERVER_ACK:
            seq = int.from_bytes(payload[:4], "big", signed=True)
            result['seq'] = seq
            if len(payload) >= 8:
                payload_size = int.from_bytes(payload[4:8], "big", signed=False)
                payload_msg = payload[8:]
        elif message_type == self.SERVER_ERROR_RESPONSE:
            code = int.from_bytes(payload[:4], "big", signed=False)
            result['code'] = code
            payload_size = int.from_bytes(payload[4:8], "big", signed=False)
            payload_msg = payload[8:]
            
        if payload_msg is None:
            return result
        if message_compression == self.GZIP:
            payload_msg = gzip.decompress(payload_msg)
        if serialization_method == self.JSON:
            payload_msg = json.loads(str(payload_msg, "utf-8"))
        elif serialization_method != self.NO_SERIALIZATION:
            payload_msg = str(payload_msg, "utf-8")
        result['payload_msg'] = payload_msg
        result['payload_size'] = payload_size
        return result
    
    def construct_request(self, reqid):
        """构建请求参数"""
        req = {
            'app': {
                'appid': self.get_appid(),
                'cluster': self.get_cluster(),
                'token': self.get_token(),
            },
            'user': {
                'uid': f'aivoicechat_{self.PROVIDER}'
            },
            'request': {
                'reqid': reqid,
                'nbest': self.nbest,
                'workflow': self.workflow,
                'show_language': self.show_language,
                'show_utterances': self.show_utterances,
                'result_type': self.result_type,
                "sequence": 1
            },
            'audio': {
                'format': self.format,
                'rate': self.rate,
                'language': self.language,
                'bits': self.bits,
                'channel': self.channel,
                'codec': self.codec
            }
        }
        return req
    
    def token_auth(self):
        """Token认证"""
        return {'Authorization': f'Bearer; {self.get_token()}'}

    def signature_auth(self, data):
        """签名认证"""
        header_dicts = {
            'Custom': 'auth_custom',
        }

        url_parse = urlparse(self.ws_url)
        input_str = f'GET {url_parse.path} HTTP/1.1\n'
        auth_headers = 'Custom'
        for header in auth_headers.split(','):
            input_str += f'{header_dicts[header]}\n'
        input_data = bytearray(input_str, 'utf-8')
        input_data += data
        mac = base64.urlsafe_b64encode(
            hmac.new(self.get_secret().encode('utf-8'), input_data, digestmod=sha256).digest())
        header_dicts['Authorization'] = f'HMAC256; access_token="{self.get_token()}"; mac="{str(mac, "utf-8")}"; h="{auth_headers}"'
        return header_dicts
    
    @staticmethod
    def read_wav_info(data: bytes = None) -> tuple:
        """读取WAV文件信息"""
        with BytesIO(data) as _f:
            wave_fp = wave.open(_f, 'rb')
            nchannels, sampwidth, framerate, nframes = wave_fp.getparams()[:4]
            wave_bytes = wave_fp.readframes(nframes)
        return nchannels, sampwidth, framerate, nframes, len(wave_bytes)
    
    @staticmethod
    def slice_data(data: bytes, chunk_size: int):
        """切分数据"""
        data_len = len(data)
        offset = 0
        while offset + chunk_size < data_len:
            yield data[offset: offset + chunk_size], False
            offset += chunk_size
        else:
            yield data[offset: data_len], True

    async def segment_data_processor(self, wav_data: bytes, segment_size: int, message_id: str = ""):
        """处理分段数据"""
        # 生成或使用现有请求ID
        reqid = str(uuid.uuid4())
        if message_id:
            # 检查并清理message_id，确保格式正确
            clean_message_id = message_id.strip()
            if len(clean_message_id) > 0:
                reqid = clean_message_id
            
        # 清空之前的识别结果
        self.result_text = ""
        
        # 构建请求参数
        request_params = self.construct_request(reqid)
        L.debug(f"豆包语音识别请求参数: {request_params} message_id:{message_id}")
        
        # JSON序列化并转为bytes，与demo保持一致
        payload_bytes = json.dumps(request_params).encode('utf-8')
        
        # GZIP压缩
        payload_compressed = gzip.compress(payload_bytes)
        
        # 构建完整请求
        full_request = bytearray(self.generate_full_default_header())
        full_request.extend(len(payload_compressed).to_bytes(4, 'big'))
        full_request.extend(payload_compressed)
        
        # 准备认证头
        ws_headers = None
        if self.auth_method == "token":
            ws_headers = self.token_auth()
        elif self.auth_method == "signature":
            ws_headers = self.signature_auth(full_request)
        
        # 添加更多日志来跟踪连接过程
        try:            
            async with websockets.connect(
                self.ws_url, 
                extra_headers=ws_headers, 
                max_size=1000000000,
                close_timeout=10,
                compression=None  # 禁用WebSocket压缩，避免与应用层压缩冲突
            ) as ws:
                # 发送初始请求前检查连接状态
                L.debug(f"WebSocket连接已建立，准备发送初始请求 message_id:{message_id} url:{self.ws_url}")
                
                # 发送请求并记录详细信息
                await ws.send(bytes(full_request))
                
                # 接收响应
                res = await ws.recv()
                result = self.parse_response(res)
                L.debug(f"收到初始响应: {result} message_id:{message_id}")
                
                if 'payload_msg' in result and result['payload_msg'].get('code') != self.success_code:
                    L.error(f"豆包语音识别请求错误: {result} message_id:{message_id}")
                    return result
                
                # 处理音频数据分片
                total_segments = 0
                processed_segments = 0
                # 先计算总分片数
                for _ in self.slice_data(wav_data, segment_size):
                    total_segments += 1
                
                L.debug(f"音频将被分为{total_segments}个分片处理 message_id:{message_id}")
                
                # 处理各个分片
                for seq, (chunk, last) in enumerate(self.slice_data(wav_data, segment_size), 1):
                    processed_segments += 1
                    
                    # 压缩音频数据
                    audio_compressed = gzip.compress(chunk)
                    
                    # 根据是否为最后一个分片选择请求头
                    if last:
                        header = self.generate_last_audio_default_header()
                    else:
                        header = self.generate_audio_default_header()
                    
                    # 构建音频请求
                    audio_request = bytearray(header)
                    audio_request.extend(len(audio_compressed).to_bytes(4, 'big'))
                    audio_request.extend(audio_compressed)
                    
                    # 发送音频数据
                    await ws.send(bytes(audio_request))
                    
                    # 接收响应
                    res = await ws.recv()
                    result = self.parse_response(res)
                    L.debug(f"收到分片{seq}响应: {result} message_id:{message_id}")
                    
                    # 处理返回的识别结果
                    if 'payload_msg' in result:
                        if result['payload_msg']['code'] != self.success_code:
                            L.error(f"豆包语音识别错误: {result} message_id:{message_id}")
                            return result
                        
                        # 提取识别文本
                        if 'result' in result['payload_msg'] and isinstance(result['payload_msg']['result'], list):
                            for item in result['payload_msg']['result']:
                                if 'text' in item:
                                    self.result_text += item['text']
                
                # 验证全部分片是否已处理
                if processed_segments != total_segments:
                    L.warning(f"音频分片处理不完整: 处理了{processed_segments}/{total_segments}个分片 message_id:{message_id}")
                
                # 处理最终结果
                L.debug(f"豆包语音识别完成，最终结果: {self.result_text} message_id:{message_id}")
                return result
                
        except websockets.exceptions.InvalidStatusCode as e:
            L.error(f"豆包语音识别WebSocket连接状态码错误: {e} message_id:{message_id}")
            L.error(traceback.format_exc())
            return {"error": f"WebSocket连接错误(状态码): {str(e)}"}
        except websockets.exceptions.ConnectionClosedError as e:
            L.error(f"豆包语音识别WebSocket连接关闭错误: {e} message_id:{message_id}")
            L.error(traceback.format_exc())
            return {"error": f"WebSocket连接被关闭: {str(e)}"}
        except Exception as e:
            L.error(f"豆包语音识别WebSocket连接异常: {e} message_id:{message_id}")
            L.error(traceback.format_exc())
            return {"error": str(e)}

    async def recognize(self, audio_path: str, message_id: str= "") -> SRTRsp:
        """识别音频文件"""
        start_time = time.perf_counter()
        
        try:
            # 读取音频文件数据
            with open(audio_path, mode="rb") as _f:
                audio_data = _f.read()
            
            # 简化逻辑，确保音频数据格式正确
            L.debug(f"读取音频文件: {audio_path}, 大小: {len(audio_data)} bytes, 格式: {self.format}")
            
            result = None
            
            if self.format == "mp3":
                # MP3格式处理
                segment_size = self.mp3_seg_size
                result = await self.segment_data_processor(audio_data, segment_size, message_id)
            elif self.format == "wav":
                # WAV格式处理
                try:
                    nchannels, sampwidth, framerate, nframes, wav_len = self.read_wav_info(audio_data)
                    L.debug(f"WAV信息: 通道={nchannels}, 采样宽度={sampwidth}, 采样率={framerate}, 帧数={nframes}")
                    
                    size_per_sec = nchannels * sampwidth * framerate
                    segment_size = int(size_per_sec * self.seg_duration / 1000)
                    L.debug(f"WAV分段大小: {segment_size} bytes (每秒 {size_per_sec} bytes)")
                    
                    result = await self.segment_data_processor(audio_data, segment_size, message_id)
                except Exception as e:
                    L.error(f"WAV处理错误: {e}")
                    raise
            elif self.format == "raw":
                # 原生PCM数据处理
                bytes_per_sample = self.bits // 8
                size_per_sec = self.rate * bytes_per_sample * self.channel
                segment_size = int(size_per_sec * self.seg_duration / 1000)
                L.debug(f"PCM分段大小: {segment_size} bytes (每秒 {size_per_sec} bytes)")
                
                result = await self.segment_data_processor(audio_data, segment_size, message_id)
            else:
                raise Exception(f"不支持的音频格式: {self.format}")
            
            # 计算耗时
            cost = int((time.perf_counter() - start_time) * 1000)
            
            # 处理错误情况
            if isinstance(result, dict) and result.get("error"):
                return SRTRsp(code=-1, message=str(result.get("error")), cost=cost)
                
            return SRTRsp(text=self.result_text, cost=cost)
            
        except Exception as e:
            cost = int((time.perf_counter() - start_time) * 1000)
            L.error(f"豆包语音识别出错: {e}")
            L.error(traceback.format_exc())
            return SRTRsp(code=-1, message=str(e), cost=cost)
