import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from aivc.common.chat import ConverMsg
from aivc.config.config import L

class MessageManager:
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.messages: Dict[str, List[ConverMsg]] = {}   
            self.cleanup_task: Optional[asyncio.Task] = None
            self.initialized = True
    
    async def start_cleanup_task(self):
        async with self._lock:
            if self.cleanup_task is None or self.cleanup_task.done():
                # 如果有旧的已完成任务，先清理掉
                if self.cleanup_task and self.cleanup_task.done():
                    try:
                        await self.cleanup_task
                    except Exception:
                        pass
                self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop_cleanup_task(self):
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            self.cleanup_task = None
    
    async def _cleanup_loop(self):
        try:
            while True:
                await asyncio.sleep(1200)  # 20分钟
                await self._cleanup_old_messages()
        except asyncio.CancelledError:
            pass
    
    async def _cleanup_old_messages(self):
        async with self._lock:
            current_time = datetime.now()  # 不需要指定UTC，与isoformat()保持一致
            keys_to_remove = []
            
            for conv_id, msgs in self.messages.items():
                if not msgs:
                    keys_to_remove.append(conv_id)
                    continue
                
                try:
                    last_msg = msgs[-1]
                    # 直接解析 isoformat 格式的时间字符串
                    last_time = datetime.fromisoformat(last_msg.conversation_id_ts)
                    if current_time - last_time > timedelta(hours=6):
                        keys_to_remove.append(conv_id)
                        L.debug(f"cleanup old messages: {conv_id} last_time: {last_msg.conversation_id_ts}")
                except (ValueError, AttributeError):
                    # 如果时间格式解析失败，为安全起见也将其移除
                    keys_to_remove.append(conv_id)
            
            for key in keys_to_remove:
                del self.messages[key]
    
    async def insert_message(self, conversation_id: str, message: ConverMsg):
        if not isinstance(message, ConverMsg):
            raise ValueError("message must be an instance of ConverMsg")
            
        async with self._lock:
            if conversation_id not in self.messages:
                self.messages[conversation_id] = []
            self.messages[conversation_id].append(message)
    
    async def get_latest_message(self, conversation_id: str) -> Optional[ConverMsg]:
        async with self._lock:
            messages = self.messages.get(conversation_id, [])
            return messages[-1] if messages else None
    
    async def is_latest_message(self, conversation_id: str, message_id: str) -> tuple[bool, str]:
        latest_msg = await self.get_latest_message(conversation_id)
        if latest_msg is None:
            return True, 0
        if message_id != latest_msg.message_id:
            L.debug(f"MessageManager is_latest_message latest_msg: {latest_msg} message_id: {message_id} conversation_id: {conversation_id}")
        return message_id >= latest_msg.message_id, latest_msg.message_id