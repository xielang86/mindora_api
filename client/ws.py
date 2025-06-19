import asyncio
import logging
import websockets
import time
import json
import base64
import traceback
from typing import Optional, Callable, Any, Dict
from aivc.common.chat import Req, Resp, VCMethod

logger = logging.getLogger(__name__)

class WSClient:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, ws_url: str, message_handler: Callable = None):
        if not hasattr(self, 'initialized'):
            self.ws_url = ws_url
            self.ws: Optional[websockets.WebSocketClientProtocol] = None
            self.message_handler = message_handler
            self.is_connected = False
            self.heartbeat_task = None
            self.initialized = True
            self.receive_task: Optional[asyncio.Task] = None
            self._closing = False
            self.reconnect_attempts = 0
            self.max_reconnect_attempts = 5
            self.retry_delay = 1 
            self.receive_queue = asyncio.Queue()
            self.process_task = None
    
    async def connect(self) -> bool:
        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                # 设置max_size为10MB (10 * 1024 * 1024字节)
                self.ws = await websockets.connect(
                    self.ws_url,
                    max_size=10 * 1024 * 1024  # 10MB
                )
                self.is_connected = True
                self.reconnect_attempts = 0  
                logger.info(f"Successfully connected to WebSocket server using URL: {self.ws_url}")

                if self.heartbeat_task is None or self.heartbeat_task.done():
                    self.heartbeat_task = asyncio.create_task(self.send_heartbeat())
                self.receive_task = asyncio.create_task(self._receive_messages())
                self.process_task = asyncio.create_task(self._process_messages())
                return True
            except Exception as e:
                self.reconnect_attempts += 1
                delay = min(self.retry_delay * (2 ** self.reconnect_attempts), 30)  
                logger.error(f"Connection attempt {self.reconnect_attempts} failed: {e} traceback: {traceback.format_exc()} URL: {self.ws_url}")
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error("Max reconnection attempts reached")
                    break
        
        self.is_connected = False
        return False
            
    async def send_heartbeat(self):
        while True:
            if not self.is_connected:
                logger.debug("Connection lost, attempting to reconnect...")
                await self.connect()
            
            if self.is_connected:
                try:
                    ping_req = Req(
                        method=VCMethod.PING,
                        conversation_id="heartbeat",
                        message_id=str(int(time.time()))
                    )
                    await self.send_message(ping_req.dict())
                except Exception as e:
                    logger.error(f"Failed to send heartbeat: {e}\n{traceback.format_exc()}")
                    self.is_connected = False
            await asyncio.sleep(6)
    
    def _serialize_message(self, message: Dict[str, Any]) -> str:
        try:
            if not isinstance(message, dict):
                raise ValueError(f"Message must be a dictionary, got {type(message)}")
            
            # 深拷贝以避免修改原始数据
            message_copy = message.copy()
            
            # 检查数据部分
            if message_copy and 'data' in message_copy:
                data = message_copy.get('data')
                if isinstance(data, dict) and 'content' in data:
                    content = data.get('content')
                    if isinstance(content, bytes):
                        data['content'] = base64.b64encode(content).decode('utf-8')
            
            return json.dumps(message_copy)
        except Exception as e:
            logger.error(f"Message serialization failed: {e}\nMessage: {message}\n{traceback.format_exc()}")
            raise

    def _deserialize_message(self, message: str) -> Dict[str, Any]:
        try:
            data = json.loads(message)
            if not isinstance(data, dict):
                raise ValueError(f"Deserialized message must be a dictionary, got {type(data)}")
                
            if (data.get('data') and 
                isinstance(data['data'], dict) and 
                data['data'].get('content_type') == 'AUDIO' and
                data['data'].get('content')):
                data['data']['content'] = base64.b64decode(data['data']['content'])
            
            return data
        except Exception as e:
            logger.error(f"Message deserialization failed: {e}\nMessage: {message}\n{traceback.format_exc()}")
            raise
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            if not self.is_connected:
                logger.info("No active connection, attempting to reconnect...")
                if not await self.connect():
                    retry_count += 1
                    await asyncio.sleep(1)
                    continue
                    
            try:
                serialized_message = self._serialize_message(message)
                await self.ws.send(serialized_message)
                logger.debug(f"send message ---> : {json.dumps(message, ensure_ascii=False, indent=2)}")
                return True
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Connection closed while sending, attempting to reconnect...")
                self.is_connected = False
                retry_count += 1
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Failed to send message: {e}\n{traceback.format_exc()}")
                retry_count += 1
                await asyncio.sleep(1)
        
        return False
            
    async def _receive_messages(self):
        while self.ws and not self._closing:
            try:
                message = await self.ws.recv()
                logger.debug(f"recv message <--- : {json.dumps(message, ensure_ascii=False, indent=2)}")
                await self.receive_queue.put(message)
            except Exception as e:
                if not self._closing:
                    logger.error(f"Error receiving message: {e} stack: {traceback.format_exc()}")
                break
        
        if not self._closing:
            await self.close()

    async def _process_messages(self):
        while not self._closing:
            try:
                message = await asyncio.wait_for(self.receive_queue.get(), timeout=0.1)
                if self.message_handler:
                    deserialized_message = self._deserialize_message(message)
                    resp = Resp.model_validate(deserialized_message)
                    await self.message_handler(resp)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                if not self._closing:
                    logger.error(f"Error processing message: {e}")

    async def close(self):
        if self._closing:
            return
            
        self._closing = True
        try:
            for task in [self.heartbeat_task, self.receive_task, self.process_task]:
                if task and not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                
            if self.ws:
                await self.ws.close()
        except Exception as e:
            logger.error(f"Error closing WebSocket connection: {e}\n{traceback.format_exc()}")
        finally:
            self._closing = False
            self.ws = None
            self.receive_task = None
            self.is_connected = False
            logger.info("WebSocket connection closed successfully")
