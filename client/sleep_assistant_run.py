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


logger = logging.getLogger(__name__)

class SleepAssistantClient:
    def __init__(self, ws_url: str = "ws://192.168.0.221:9001/ws"):
        self.ws_client = WSClient(ws_url, self.handle_message)
        self.conversation_id = None
        self.running = False
        self.stop_event = asyncio.Event()
        self.message_queue = asyncio.Queue(maxsize=10)
        self._send_task = None
        
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
            if resp.method == VCMethod.EXECUTE_COMMAND:
                if resp.data:
                    action_data = ActionRespData.model_validate(resp.data)
                    logger.info(f"Received scene: {action_data.scene}")
                    logger.info(f"Received actions: {action_data.actions}")
                    # 这里可以添加对动作的具体处理逻辑
        except Exception as e:
            logger.error(f"Error handling message: {e}\n{traceback.format_exc()}")

    async def capture_image(self) -> tuple[str, str]:
        """捕获图像并返回base64编码的数据和文件路径"""
        cap = cv2.VideoCapture(0)
        try:
            # 设置摄像头分辨率
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280.0)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720.0)
            
            ret, frame = cap.read()
            if not ret:
                raise Exception("Failed to capture image")
            
            message_id = get_message_id()
            photo_path = f"data/sleep_assistant/{message_id}.jpg"
            
            # 图像预处理
            frame = cv2.flip(frame, 1)  # 水平翻转
            frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=30)  # 提高亮度和对比度
            
            # 确保图像分辨率
            frame = cv2.resize(frame, (1280, 720))
            
            cv2.imwrite(photo_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            with open(photo_path, 'rb') as f:
                photo_bytes = f.read()
            return base64.b64encode(photo_bytes).decode('utf-8'), photo_path
        finally:
            cap.release()

    async def send_report(self):
        """发送状态报告到服务器"""
        try:
            # 捕获图像
            image_data, image_path = await self.capture_image()
            
            # 获取当前场景和状态
            scene, status = await self._get_current_scene_and_status()
            logger.info(f"Current scene: {scene}, status: {status}")
            
            # 构造请求数据，确保格式符合规范
            message = Req(
                method=VCMethod.REPORT_STATE,
                conversation_id=self.conversation_id,
                message_id=get_message_id(),
                timestamp=datetime.now().isoformat(),
                data=ReportReqData(
                    images=ImageDataPayload(
                        format="jpeg",
                        data=[image_data]
                    ),
                    scene_exec_status=SceneExecStatus(
                        command=self.test_command,
                        scene=scene,
                        status=status
                    )
                )
            )
            
            await self.message_queue.put(message)

            logger.info(f"Report queued - scene: {scene}, status: {status}, image: {image_path}")
            
        except Exception as e:
            logger.error(f"Error sending report: {e}\n{traceback.format_exc()}")

    async def _get_current_scene_and_status(self):
        """获取当前场景和状态"""
        if self.is_first_report:
            # 第一次报告：进入流程，IN_PROGRESS
            self.is_first_report = False
            logger.info(f"First report: scene={self.current_scene}, status=IN_PROGRESS")
            return self.current_scene, "IN_PROGRESS"
        
        if self.current_status == "IN_PROGRESS":
            # 当前状态是IN_PROGRESS，切换到COMPLETED但不改变场景
            self.current_status = "COMPLETED"
            logger.info(f"Status changed to COMPLETED: scene={self.current_scene}")
            return self.current_scene, "COMPLETED"
        else:
            # 当前状态是COMPLETED，获取下一个场景
            if not self.test_conversation_id:
                self.test_conversation_id = get_conversation_id()
            
            logger.info(f"Getting next state for conversation_id={self.test_conversation_id}, command={self.test_command}")
            
            scene_exec_status = SceneExecStatus(
                command=self.test_command,
                scene=self.current_scene,
                status=self.current_status
            )
            try:
                next_state = await self.command_state_manager.update_state_by_exec_status(
                    self.test_conversation_id, 
                    scene_exec_status
                )
                logger.info(f"Next state returned: {next_state}")
                
                if next_state:
                    self.current_scene = next_state
                    self.current_status = "IN_PROGRESS"
                    logger.info(f"Moving to next scene: {self.current_scene}, status=IN_PROGRESS")
                    return self.current_scene, "IN_PROGRESS"
                else:
                    # 如果没有下一个状态，保持当前状态
                    logger.info(f"No next state available, staying at scene: {self.current_scene}, status=COMPLETED")
                    return self.current_scene, "COMPLETED"
            except Exception as e:
                logger.error(f"Error getting next state: {e}\n{traceback.format_exc()}")
                return self.current_scene, "COMPLETED"

    async def _run_message_sender(self):
        """消息发送循环"""
        while self.running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=0.1)
                for retry in range(3):
                    if await self.ws_client.send_message(message.model_dump()):
                        logger.info(f"Successfully sent message {message.message_id}")
                        break
                    if retry < 2:
                        await asyncio.sleep(1)
                else:
                    logger.error(f"Failed to send message {message.message_id}")
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in message sender: {e}")
                await asyncio.sleep(1)

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

            self._send_task = asyncio.create_task(self._run_message_sender())
            
            while self.running:
                await self.send_report()
                await asyncio.sleep(0.5)  # 减少等待时间从2秒到0.5秒
                
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
