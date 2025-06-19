import asyncio
import websockets
import json
import numpy as np
import librosa
import time
import os
from aivc.config.config import L
from aivc.srt.base import BaseSRT
from aivc.srt.common import SRTRsp
import traceback

class RknnSRT(BaseSRT):
    PROVIDER = "rknn"
    
    SERVER_URL_ENV_KEY = "RKNN_SERVER_URL"
    
    def __init__(self):
        self.server_url = self.get_server_url()
    
    def get_server_url(self) -> str:
        return "ws://192.168.0.221:9101" 
    
    def _load_and_process_audio(self, audio_path: str):
        """加载并预处理音频文件，支持WAV、MP3等格式以及PCM裸流"""
        
        # 检查文件扩展名，如果是.pcm则按PCM裸流处理
        if audio_path.lower().endswith('.wav') or audio_path.lower().endswith('.mp3'):
            return self._load_audio_file(audio_path)
        else:
            return self._load_pcm_raw(audio_path)

    def _load_pcm_raw(self, pcm_path: str, sample_rate: int = 16000):
        """加载PCM裸流文件（假设为16bit, 单声道, 16kHz）"""
        try:
            # 读取PCM原始数据
            with open(pcm_path, 'rb') as f:
                pcm_data = f.read()
            
            # 将bytes转换为int16数组
            audio_data = np.frombuffer(pcm_data, dtype=np.int16)
            
            # 转换为float32类型，归一化到[-1, 1]范围
            audio_data = audio_data.astype(np.float32) / 32768.0
            
            L.debug(f"PCM裸流加载完成，样本数: {len(audio_data)}, 采样率: {sample_rate}")
            return audio_data, sample_rate
            
        except Exception as e:
            L.error(f"加载PCM裸流失败: {e}")
            raise
    
    def _load_audio_file(self, audio_path: str):
        """加载常规音频文件（wav、mp3等）"""
        # 读取音频文件
        audio_data, sample_rate = librosa.load(audio_path, sr=None, mono=True)
        
        # 确保采样率为16kHz（如果不是则重采样）
        if sample_rate != 16000:
            audio_data = librosa.resample(
                y=audio_data,
                orig_sr=sample_rate,
                target_sr=16000,
                res_type='kaiser_best'
            )
            sample_rate = 16000
        
        # 转换为float32类型（与服务器端保持一致）
        audio_data = audio_data.astype(np.float32)
        
        return audio_data, sample_rate
    
    async def recognize(self, audio_path: str, message_id: str = "") -> SRTRsp:
        """
        异步识别音频文件，支持WAV、MP3、PCM等格式
        """
        start_time = time.perf_counter()
        
        try:
            L.debug(f"RKNN语音识别开始 audio_path:{audio_path} message_id:{message_id}")
            
            async with websockets.connect(self.server_url) as websocket:
                # 1. 发送配置信息
                config = {"language": "auto"}
                await websocket.send(json.dumps(config))
                L.debug(f"RKNN语音识别发送配置 message_id:{message_id}")
                
                # 2. 读取并处理音频文件
                audio_data, sample_rate = self._load_and_process_audio(audio_path)
                audio_size = len(audio_data) / sample_rate  # 音频时长（秒）
                
                # 3. 发送音频数据（一次性发送）
                audio_bytes = audio_data.tobytes()
                await websocket.send(audio_bytes)
                L.debug(f"RKNN语音识别发送音频数据 size:{len(audio_bytes)} duration:{audio_size:.2f}s message_id:{message_id}")
                
                # 4. 发送结束标志
                await websocket.send(json.dumps({"end": True}))
                L.debug(f"RKNN语音识别发送结束标志 message_id:{message_id}")
                
                # 5. 接收识别结果
                results = []
                final_text = ""
                
                async for message in websocket:
                    try:
                        result = json.loads(message)
                        results.append(result)
                        L.debug(f"RKNN语音识别收到结果: {result} message_id:{message_id}")
                        
                        if result.get("is_final", False):
                            final_text = result.get("text", "")
                            break
                        else:
                            # 中间结果也更新文本
                            final_text = result.get("text", "")
                            
                    except json.JSONDecodeError as e:
                        L.warning(f"RKNN语音识别解析响应失败: {e} message_id:{message_id}")
                        continue
                
                cost = int((time.perf_counter() - start_time) * 1000)
                
                L.debug(f"RKNN语音识别完成 结果: ### {final_text} ### cost:{cost}ms message_id:{message_id}")
                
                return SRTRsp(
                    text=final_text,
                    text_length=len(final_text),
                    audio_size=audio_size,
                    cost=cost
                )
                
        except websockets.exceptions.ConnectionClosed as e:
            cost = int((time.perf_counter() - start_time) * 1000)
            L.error(f"RKNN语音识别连接关闭: {e} message_id:{message_id}")
            return SRTRsp(
                code=-1,
                message=f"WebSocket连接关闭: {str(e)}",
                cost=cost,
                text=""
            )
            
        except websockets.exceptions.WebSocketException as e:
            cost = int((time.perf_counter() - start_time) * 1000)
            L.error(f"RKNN语音识别WebSocket错误: {e} message_id:{message_id}")
            return SRTRsp(
                code=-1,
                message=f"WebSocket错误: {str(e)}",
                cost=cost,
                text=""
            )
            
        except Exception as e:
            cost = int((time.perf_counter() - start_time) * 1000)
            L.error(f"RKNN语音识别出错: {e} message_id:{message_id} trace:{traceback.format_exc()}")
            return SRTRsp(
                code=-1,
                message=str(e),
                cost=cost,
                text=""
            )
