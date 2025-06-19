import asyncio
import logging
import base64
import traceback
import signal
import os
import cv2
import argparse
from typing import Optional, Literal
from datetime import datetime
from client.ws import WSClient   
from client.audio import AudioHandler   
from client.common import setup_logging
import readline  
from aivc.sop.common.manager import CommandStateManager
from aivc.common.chat import Req, VCMethod, Resp, VCReqData, VCRespData,ReportReqData,ActionRespData,ContentType
from aivc.utils.id import get_message_id, get_conversation_id
from aivc.sop.common.common import ImageDataPayload, SceneExecStatus
from client.common import setup_logging
import json



logger = logging.getLogger(__name__)

class Client:
    def __init__(self, ws_url: str = "ws://192.168.0.221:9001/ws", 
                 input_type: Literal["text", "sound"] = "text"):
        self.audio_handler = AudioHandler()
        self.ws_client = WSClient(ws_url, self.handle_message)
        self.conversation_id: Optional[str] = None
        self.running = False
        self.stop_event = asyncio.Event()
        self.message_queue = asyncio.Queue(maxsize=10)
        self.input_type = input_type
        self._send_task = None
        os.makedirs("data/send", exist_ok=True)

    async def take_photo_handler(self):
        cap = None
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
            if not cap.isOpened():
                logger.error("Failed to open camera with AVFoundation")
                return

            cap.set(cv2.CAP_PROP_CONVERT_RGB, 1.0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320.0)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240.0)

            await asyncio.sleep(0.1)

            ret, frame = cap.read()
            if not ret or frame is None:
                logger.error("Failed to capture photo")
                return
            
            if frame.size == 0:
                logger.error("Captured frame is empty")
                return
                
            logger.info(f"Frame shape: {frame.shape}, mean value: {frame.mean()}")
            
            message_id = get_message_id()
            photo_path = f"data/send/{message_id}.jpg"
            
            frame = cv2.flip(frame, 1)  # 水平翻转
            # 提高亮度和对比度
            frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=30)
            
            # 保存图像
            success = cv2.imwrite(photo_path, frame)
            if not success:
                logger.error("Failed to save photo")
                return
                
            logger.info(f"Photo saved to {photo_path} with message_id {message_id}")
            
            with open(photo_path, 'rb') as f:
                photo_bytes = f.read()
            encoded_photo = base64.b64encode(photo_bytes).decode('utf-8')
            
            message = Req(
                method=VCMethod.VOICE_CHAT,
                conversation_id=self.conversation_id,
                message_id=message_id,
                token="token",
                timestamp=datetime.now().isoformat(),
                data=VCReqData(
                    content_type=ContentType.IMAGE,
                    content=encoded_photo,
                    tts_audio_format="ogg_opus"
                )
            )
            
            await self.message_queue.put(message)
            logger.info("Photo message queued for sending")

        except Exception as e:
            logger.error(f"Error in take_photo_handler: {e}\n{traceback.format_exc()}")
        finally:
            if cap is not None:
                cap.release()

    async def handle_message(self, resp:Resp):
        try:
            logger.info(f"Received message: {resp}")
            if resp.method == VCMethod.VOICE_CHAT:
                if resp.data:
                    voice_data = VCRespData.model_validate(resp.data)
                    if not voice_data.audio_data:
                        logger.error("Received empty audio data")
                        return
                    audio_bytes = base64.b64decode(voice_data.audio_data)
                    audio_format = voice_data.audio_format # pcm or mp3
                    self.audio_handler.play_audio(
                        audio_data = audio_bytes,
                        message_id=resp.message_id,
                        stream_seq=voice_data.stream_seq,
                        audio_format=audio_format
                    )
                    if voice_data.action == 'take_photo':
                        logger.info("Received take photo command")
                        await self.take_photo_handler()                        
        except Exception as e:
            logger.error(f"Error handling message: {e}\n{traceback.format_exc()}")

    def stop(self):
        logger.info("Stopping client...")
        self.running = False
        self.stop_event.set()

    async def run(self):
        self.running = True
        if not self.conversation_id:
            self.conversation_id = get_conversation_id()
            
        try:
            if not await self.ws_client.connect():
                logger.error(f"Failed to connect to server using ws_url: {self.ws_client.ws_url}")
                return

            logger.info(f"Starting client with input_type: {self.input_type}")
            
            # 根据输入类型选择不同的输入处理任务
            input_task = None
            if self.input_type == "sound":
                input_task = asyncio.create_task(self._run_voice_detection())
            else:  # text mode
                input_task = asyncio.create_task(self._run_text_input())

            self._send_task = asyncio.create_task(self._run_message_sender())
            
            await asyncio.gather(
                self.stop_event.wait(),
                input_task,
                self._send_task,
                return_exceptions=True
            )
                    
        except Exception as e:
            logger.error(f"Error in run: {e}\n{traceback.format_exc()}")
        finally:
            self.running = False
            await self._cleanup()

    async def _cleanup(self):
        logger.info("Starting cleanup...")
        try:
            await self.ws_client.close()
            self.audio_handler.close()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    async def _run_voice_detection(self):
        try:
            async for audio_data, message_id in self.audio_handler.detect_voice():                
                try:
                    encoded_audio = base64.b64encode(audio_data).decode('utf-8')
                    message = Req(
                        method=VCMethod.VOICE_CHAT,
                        conversation_id=self.conversation_id,
                        message_id=message_id,
                        token="token",
                        timestamp=datetime.now().isoformat(),
                        data=VCReqData(
                            content_type=ContentType.AUDIO,
                            content=encoded_audio,
                            tts_audio_format="pcm")
                    )
                    
                    try:
                        await asyncio.wait_for(
                            self.message_queue.put(message),
                            timeout=0.5  
                        )
                    except asyncio.TimeoutError:
                        logger.warning(f"Message queue full, dropping message {message_id}")
                        
                except Exception as e:
                    logger.error(f"Error preparing message: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Voice detection cancelled")
            raise

    async def _run_text_input(self):
        """处理文本输入模式"""
        try:
            # 配置 readline
            readline.parse_and_bind('set editing-mode emacs')  # 设置编辑模式
            readline.set_completer(None)  # 清除任何已存在的补全器
            readline.clear_history()  # 清除历史记录
            
            # 设置提示符
            prompt = "\033[2K\r请输入消息 (按回车发送): "  # \033[2K 清除整行
            
            while self.running:
                try:
                    loop = asyncio.get_event_loop()
                    # 使用 readline 读取输入
                    user_input = await loop.run_in_executor(None, lambda: input(prompt).strip())
                    
                    # 清除当前行并移动光标到行首
                    print("\033[2K\r", end="", flush=True)
                    
                    if not user_input:
                        continue
                    
                    # 将输入添加到历史记录
                    readline.add_history(user_input)
                    
                    message = Req(
                        method=VCMethod.VOICE_CHAT,
                        conversation_id=self.conversation_id,
                        message_id=get_message_id(),
                        token="token",
                        timestamp=datetime.now().isoformat(),
                        data=VCReqData(
                            content_type=ContentType.TEXT,
                            content=user_input,
                            tts_audio_format="pcm"
                        )
                    )
                    
                    try:
                        await self.message_queue.put(message)
                        logger.info(f"Text message queued: {user_input}")
                    except asyncio.QueueFull:
                        logger.warning("Message queue full, dropping text input")
                    
                except EOFError:  # 处理 Ctrl+D
                    self.stop()
                    break
                except KeyboardInterrupt:  # 处理 Ctrl+C
                    print("\033[2K\r", end="", flush=True)  # 清除当前行
                    continue
                    
        except asyncio.CancelledError:
            logger.info("Text input cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in text input: {e}\n{traceback.format_exc()}")

    async def _run_message_sender(self):
        while self.running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=0.1)
                for retry in range(3):
                    if await self.ws_client.send_message(message.model_dump()):
                        break
                    if retry < 2:
                        logger.warning(f"Retry {retry + 1} for message {message.message_id}")
                        await asyncio.sleep(1)
                else:
                    logger.error(f"Failed to send audio message {message.message_id} after all retries")
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in message sender: {e}")
                await asyncio.sleep(1)

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description='Voice/Text Chat Client')
    parser.add_argument('--input-type', 
                       choices=['text', 'sound'],
                       default='text',
                       help='Input type: text or sound (default: text)')
    parser.add_argument('--ws-url',
                       default='ws://192.168.0.221:9001/ws',
                       help='WebSocket server URL (default: ws://192.168.0.221:9001/ws)')
    
    args = parser.parse_args()
    
    client = Client(ws_url=args.ws_url, input_type=args.input_type)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    def signal_handler():
        client.stop()
        for task in asyncio.all_tasks(loop):
            task.cancel()
        
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        loop.run_until_complete(client.run())
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        loop.run_until_complete(client._cleanup())
        loop.close()

if __name__ == "__main__":
    main()
