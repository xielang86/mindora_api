from aivc.common.chat import ReportReqData
from aivc.common.trace_tree import TraceTree
from aivc.common.sleep_common import ApiResponse, SleepResult, PoseInfo, SceneExecStatus
import zerorpc
from aivc.config.config import L,settings
import traceback
import json
from aivc.common.sleep_config import StateType, states_dict,Actions
from aivc.common.sleep_voice import voice_manager
import base64
from typing import Optional
import time

class RpcClient:
    """RPC客户端单例类"""
    _instance = None
    _client = None
    _last_connect_time = 0
    _reconnect_interval = 5  # 重连间隔时间（秒）

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_client(self):
        current_time = time.time()
        
        # 如果客户端不存在或者最后连接时间超过重连间隔，尝试重新连接
        if (self._client is None or 
            current_time - self._last_connect_time > self._reconnect_interval):
            try:
                self._client = zerorpc.Client(timeout=2)
                self._client.connect(settings.AI_RPC_SERVER)
                self._last_connect_time = current_time
            except Exception as e:
                L.error(f"RPC连接失败: {str(e)}")
                self._client = None
                
        return self._client

async def get_state_by_api(report_data: ReportReqData, trace_tree: TraceTree = None) -> ApiResponse:
    try:
        message_id = trace_tree.root.message_id if trace_tree and trace_tree.root else "unknown"
        conversation_id = trace_tree.root.conversation_id if trace_tree and trace_tree.root else "unknown"
        image_count = 0
        audio_count = 0
        if report_data.images and report_data.images.data:
            image_count = len(report_data.images.data)
        if report_data.audio and report_data.audio.data:
            audio_count = len(report_data.audio.data)
        L.debug(f"get_state_by_api 开始检测睡眠场景 [message_id={message_id}], report_data: {image_count} images, {audio_count} audio")

        # 使用RPC客户端单例
        client = RpcClient()
        rpc = client.get_client()
        if not rpc:
            L.error(f"无法获取RPC客户端 [message_id={message_id}]")
            return None
        
        # 准备请求数据
        request = {
            "uid": conversation_id,
            "messageid": message_id, 
            "conversationid": conversation_id,
            "data": {
                "images": {
                    "format": "jpg",
                    "data": report_data.images.data
                }
            }
        }

        # 发送请求获取结果
        try:
            start_time = time.time()
            L.debug(f"发送RPC请求检测场景 [message_id={message_id}]")
            response = rpc.DetectSleepPhrase(request)
            response_json_str = json.dumps(response, ensure_ascii=False)
            L.debug(f"检测结果 [message_id={message_id}]: {response_json_str} 耗时: {int((time.time()-start_time)*1000)}ms")
            
            if response:
                # 构建睡眠检测结果
                sleep_data = response.get('data', {})
                if isinstance(sleep_data, str):
                    sleep_data = json.loads(sleep_data)
                
                # 创建 SleepResult 对象
                sleep_result = SleepResult.from_dict(sleep_data)
                api_rsp = ApiResponse(
                    status_code=response.get('status_code', 200),
                    user_id=response.get('user_id', ''),
                    conversation_id=response.get('conversation_id', conversation_id),
                    message_id=response.get('message_id', message_id),
                    message=response.get('message', 'Pose detected successfully'),
                    sleep_status=response.get('sleep_status', sleep_result.sleep_type.name),
                    data=sleep_result
                )
                
                trace_tree.sleep_api_rsp = api_rsp.to_dict()
                return api_rsp
            return None
            
        except zerorpc.TimeoutExpired as e:
            L.error(f"RPC调用超时 [message_id={message_id}]: {str(e)}\n{traceback.format_exc()}")
            return None
        except Exception as e:
            L.error(f"RPC调用失败 [message_id={message_id}]: {str(e)}\n{traceback.format_exc()}")
            # 发生错误时清空客户端，触发重连
            client._client = None
            return None
            
    except Exception as e:
        message_id = trace_tree.root.message_id if trace_tree and trace_tree.root else "unknown"
        L.error(f"检测睡眠场景时发生未知错误 [message_id={message_id}]: {str(e)}\n{traceback.format_exc()}")
        return None

class StateManager:
    """管理状态转换的类 - 单例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._state_cache = {}
        return cls._instance
    
    async def update_state_by_exec_status(self, conversation_id: str, scene_exec_status: SceneExecStatus) -> Optional[StateType]:
        rsp_state = await self.get_current_state(conversation_id)
        if scene_exec_status and scene_exec_status.scene_seq < StateType.RELAX_2.order and scene_exec_status.status == "COMPLETED":
            rsp_state = StateType.get_next_state(scene_exec_status.scene_seq)
            L.debug(f"update_state_by_exec_status 会话 {conversation_id} scene_exec_status:{scene_exec_status} COMPLETED, 更新状态为 {rsp_state}")
            await self.set_state(conversation_id, rsp_state)
        
        L.debug(f"update_state_by_exec_status 更新会话 {conversation_id} scene_exec_status:{scene_exec_status} 的状态为 {rsp_state}")
        return rsp_state
    
    async def get_current_state(self, conversation_id: str) -> Optional[StateType]:
        current_state = self._state_cache.get(conversation_id, StateType.PREPARE)
        L.debug(f"get_current_state 获取会话 {conversation_id} 的当前状态 {current_state}")
        return current_state
    
    async def set_state(self, conversation_id: str, state: StateType) -> None:
        if state is not None and not state.is_abnormal():
            L.debug(f"set_state 设置会话 {conversation_id} 的状态为 {state.name}")
            self._state_cache[conversation_id] = state
        else:
            L.error(f"set_state 无法设置会话 {conversation_id} 的状态为 state：{state}")

async def process_state_audio(voice_action) -> tuple[str, str]:
    """
    处理指定语音动作的语音数据
    返回: (audio_data: str, audio_format: str) - audio_data为base64编码的字符串
    """
    if not voice_action or not voice_action.text:
        return None, None
        
    audio_file = voice_manager.get_voice_file(voice_action.text)
    if not audio_file:
        L.error(f"未找到语音文本 '{voice_action.text}' 对应的语音文件")
        return None, None
        
    try:
        with open(audio_file, 'rb') as f:
            audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        return audio_base64, "mp3"
    except Exception as e:
        L.error(f"读取语音文件失败: {str(e)}")
        return None, None

async def get_actions(state:StateType) -> Actions:
    return states_dict.get(state)    

async def get_state_voices_duration(state: StateType) -> float:
    total_duration = 0.0
    actions = states_dict.get(state)
    
    if hasattr(actions, 'voice') and actions.voice and actions.voice.voices:
        for voice_action in actions.voice.voices:
            duration = voice_manager.get_voice_time(voice_action.text)
            if duration:
                total_duration += duration
    
    return max(total_duration, 30.0)

def determine_state_type(sleep_status: str, pose: PoseInfo, recent_action: str) -> StateType:
    if sleep_status == "HalfSleep":
        return StateType.SLEEP_READY
    elif sleep_status == "LightSleep":
        return StateType.LIGHT_SLEEP
    elif sleep_status == "DeepSleep":
        return StateType.DEEP_SLEEP
    elif sleep_status == "Awake":
        if pose is not None:
            body_pose = pose.body
            left_hand_pose = pose.left_hand
            right_hand_pose = pose.right_hand

            # StateType.PREPARE
            # (半躺 or 躺姿) and 存在 and !(手持)
            if (body_pose in ["HalfLie", "LieFlat"] and
                left_hand_pose != "LiftOn" and 
                right_hand_pose != "LiftOn"):
                return StateType.PREPARE
            
            # StateType.USING_PHONE
            # (坐姿 or 半躺 or 躺姿) and 存在 and (手持)
            if (body_pose in ["SitDown", "HalfLie", "LieFlat"] and
                (left_hand_pose == "LiftOn" or 
                right_hand_pose == "LiftOn")):
                return StateType.USING_PHONE
            
            # StateType.SITTING_UP
            # (坐姿) and 存在
            if body_pose == "SitDown":
                return StateType.SITTING_UP
            
            # StateType.LEAVING
            # (站姿) and 存在
            if body_pose == "Stand":
                return StateType.LEAVING
        else:
            return StateType.LEAVING
    return None