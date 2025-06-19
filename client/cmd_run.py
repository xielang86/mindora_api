import asyncio
import logging
import base64
import traceback
import signal
import os
import cv2
from datetime import datetime
from client.ws import WSClient    
from aivc.sop.common.manager import CommandStateManager
from aivc.common.chat import Req, VCMethod, Resp, VCReqData, VCRespData,ReportReqData,ActionRespData
from aivc.utils.id import get_message_id, get_conversation_id
from aivc.sop.common.common import ImageDataPayload, SceneExecStatus
from client.common import setup_logging
import json


logger = logging.getLogger(__name__)

class SleepAssistantClient:
    def __init__(self, ws_url: str = "ws://192.168.0.132:9001/ws"):
        self.ws_client = WSClient(ws_url, self.handle_message)
        self.conversation_id = None
        self.running = False
        self.stop_event = asyncio.Event()
        # 移除消息队列相关属性
        # self.message_queue = asyncio.Queue(maxsize=10)
        # self._send_task = None
        
        # 添加状态管理相关属性
        self.command_state_manager = CommandStateManager()
        self.test_conversation_id = None
        self.test_command = "meditation.mindfulness.breathing_exercises.natural"
        self.current_scene = "进入流程"
        self.current_status = "IN_PROGRESS"
        self.is_first_report = True
        
        # 确保存储目录存在
        os.makedirs("data/sleep_assistant", exist_ok=True)

    async def handle_message(self, resp: Resp):
        try:
            logger.info(f"Received message: {resp}")
            if resp.method == VCMethod.COMMAND:
                if resp.data:
                    action_data = ActionRespData.model_validate(resp.data)
                    logger.info(f"Received ActionRespData: {json.dumps(action_data.model_dump(), indent=2, ensure_ascii=False)}")
                    # 收到服务器响应后停止客户端
                    logger.info("Command executed successfully, stopping client...")
                    self.stop()
        except Exception as e:
            logger.error(f"Error handling message: {e}\n{traceback.format_exc()}")

    async def send_cmd(self):
        """发送命令到服务器"""
        try:
            # 构造请求数据，确保格式符合规范
            message = Req(
                method=VCMethod.COMMAND,
                conversation_id=self.conversation_id,
                message_id=get_message_id(),
                timestamp=datetime.now().isoformat(),
                data=VCReqData(
                    content_type="text",
                    content=self.test_command,
                )
            )
            
            # 直接发送消息，重试3次
            for retry in range(3):
                if await self.ws_client.send_message(message.model_dump()):
                    logger.info(f"Successfully sent command: {self.test_command}")
                    return True
                if retry < 2:
                    await asyncio.sleep(1)
                    logger.warning(f"Retry sending command, attempt {retry + 2}")
            
            logger.error("Failed to send command after 3 attempts")
            return False
            
        except Exception as e:
            logger.error(f"Error sending command: {e}\n{traceback.format_exc()}")
            return False

    async def run(self):
        """主运行循环"""
        self.running = True
        if not self.conversation_id:
            self.conversation_id = get_conversation_id()
        
        # 初始化测试会话ID
        if not self.test_conversation_id:
            self.test_conversation_id = self.conversation_id
            
        try:
            if not await self.ws_client.connect():
                logger.error("Failed to connect to server")
                return

            # 发送命令
            if await self.send_cmd():
                # 等待服务器响应或停止事件
                await self.stop_event.wait()
            else:
                logger.error("Failed to send command")
                
        except Exception as e:
            logger.error(f"Error in run: {e}\n{traceback.format_exc()}")
        finally:
            self.running = False
            await self._cleanup()

    async def _cleanup(self):
        """清理资源"""
        logger.info("Starting cleanup...")
        try:
            await self.ws_client.close()
        except Exception as e:
            logger.error(f"Cleanup error: {e} \n{traceback.format_exc()}")

    def stop(self):
        """停止客户端"""
        logger.info("Stopping client...")
        self.running = False
        self.stop_event.set()

def main():
    setup_logging()
    
    client = SleepAssistantClient()
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
