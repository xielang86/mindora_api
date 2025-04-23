import asyncio
from aivc.common.chat import ReportReqData
from aivc.common.trace_tree import TraceTree
from aivc.common.sleep_common import ApiResponse, SleepResult, PoseInfo, VoiceSequence
import zerorpc
from aivc.config.config import L,settings
import traceback
import json
from aivc.common.sleep_config import StateType, states_dict,Actions
from aivc.common.sleep_voice import voice_manager
import base64
import time
from aivc.common.sleep_common import EyeStatus, BodyPoseType, SleepStatus, PersonStatus
from aivc.chat.chat import Chat, ContentType
from aivc.chat.prompt_selector import PromptTemplate
from aivc.chat.llm.manager import LLMType, ZhiPuLLM
import random

class RpcClient:
    """RPC客户端异步安全单例类"""
    _instance = None
    _client = None
    _lock = asyncio.Lock()
    _instance_lock = asyncio.Lock()
    
    def __new__(cls):
        return super().__new__(cls)
        
    @classmethod
    async def get_instance(cls) -> 'RpcClient':
        if not cls._instance:
            async with cls._instance_lock:
                if not cls._instance:
                    cls._instance = RpcClient()
        return cls._instance

    def reset_client(self):
        self._client = None

    async def get_client(self):
        async with self._lock:
            if not self._client:
                try:
                    self._client = zerorpc.Client(timeout=2)
                    self._client.connect(settings.AI_RPC_SERVER)
                    L.debug(f"RPC服务器:{settings.AI_RPC_SERVER} 连接成功")
                except Exception as e:
                    L.error(f"RPC服务器:{settings.AI_RPC_SERVER} 连接失败: {str(e)}")
                    await self.reset_client()
            return self._client

    @classmethod
    async def get_connected_client(cls):
        instance = await cls.get_instance()
        return await instance.get_client()

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
                
        rpc = await RpcClient.get_connected_client()
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
                
                log_dict = api_rsp.to_dict()
                log_dict['cost'] = round(time.time()-start_time, 2)
                trace_tree.sleep_api_rsp = log_dict
                return api_rsp
            return None
            
        except zerorpc.TimeoutExpired as e:
            L.error(f"RPC调用超时 [message_id={message_id}]: {str(e)}\n{traceback.format_exc()}")
            (await RpcClient.get_instance()).reset_client()
            return None
        except Exception as e:
            L.error(f"RPC调用失败 [message_id={message_id}]: {str(e)}\n{traceback.format_exc()}")
            (await RpcClient.get_instance()).reset_client()
            return None
            
    except Exception as e:
        message_id = trace_tree.root.message_id if trace_tree and trace_tree.root else "unknown"
        L.error(f"检测睡眠场景时发生未知错误 [message_id={message_id}]: {str(e)}\n{traceback.format_exc()}")
        return None


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
    actions = states_dict.get(state)
    
    # 处理异常状态，如玩手机或坐起
    if state and state.is_abnormal() and actions and actions.voice and actions.voice.voices:
        # 从语音列表中随机选择一个
        random_voice = random.choice(actions.voice.voices)
        
        # 创建一个新的 VoiceSequence，只包含随机选择的语音
        new_voice_sequence = VoiceSequence(voices=[random_voice])
        
        # 创建新的 Actions 对象，只保留随机选择的语音
        new_actions = Actions(
            action_feature=actions.action_feature,
            voice=new_voice_sequence,
            bgm=actions.bgm,
            light=actions.light,
            fragrance=actions.fragrance,
            display=actions.display
        )
        return new_actions
        
    return actions

async def get_state_voices_duration(state: StateType) -> float:
    total_duration = 0.0
    actions = states_dict.get(state)
    
    if hasattr(actions, 'voice') and actions.voice and actions.voice.voices:
        for voice_action in actions.voice.voices:
            duration = voice_manager.get_voice_time(voice_action.text)
            if duration:
                total_duration += duration
    
    return max(total_duration, 30.0)

def determine_state_type(sleep_status: str, pose: PoseInfo, recent_action: str) -> tuple[StateType, str, str]:
    state_type = None
    eye_status = None
    lie_status = None
    
    LIE_POSES = ["HalfLie", "LieFlat", "Lie"]
    
    if pose is not None:
        left_eye_pose = pose.left_eye
        right_eye_pose = pose.right_eye
        eye_status = EyeStatus.Closed.value if left_eye_pose == EyeStatus.Closed.value and right_eye_pose == EyeStatus.Closed.value else EyeStatus.Open.value

        body_pose = pose.body
        lie_status = BodyPoseType.Lie.value if body_pose in LIE_POSES else None
    
    if sleep_status ==SleepStatus.Awake.value:
        if pose is not None:
            body_pose = pose.body
            left_hand_pose = pose.left_hand
            right_hand_pose = pose.right_hand
            
            # StateType.PREPARE
            if (body_pose in LIE_POSES and
                left_hand_pose != "LiftOn" and 
                right_hand_pose != "LiftOn"):
                state_type = StateType.PREPARE
            
            # StateType.SITTING_UP
            if body_pose == "SitDown":
                state_type = StateType.SITTING_UP 
            
            # StateType.USING_PHONE
            if (body_pose in LIE_POSES + ["SitDown"] and
                (left_hand_pose == "LiftOn" or 
                right_hand_pose == "LiftOn")):
                state_type = StateType.USING_PHONE 
                            
            # StateType.LEAVING
            if body_pose == "Stand":
                state_type = StateType.LEAVING 
        else:
            state_type = StateType.LEAVING 

    return state_type, eye_status, lie_status

# api_state, eye_status, lie_status
async def get_state_by_llm(report_data: ReportReqData, trace_tree: TraceTree = None) -> tuple[dict, float]:
    message_id = trace_tree.root.message_id if trace_tree and trace_tree.root else "unknown"
    try:
        llm_type = LLMType.ZhiPu
        model_name=ZhiPuLLM.GLM_4V_FlASH
        chat_instance = Chat(
            llm_type=llm_type,
            model_name=model_name,
            timeout=6,
            content_type=ContentType.IMAGE.value
        )
        question = PromptTemplate.SLEEP_CHECK_PROMPT

        last_image = None
        if report_data and report_data.images and report_data.images.data:
            last_image = report_data.images.data[-1]
        else:
            L.error(f"get_state_by_llm 无法获取图片数据 [message_id={message_id}]")
            return None, "", ""
        
        try:
            response, cost = await asyncio.wait_for(
                chat_instance.chat_image(
                    question=question,
                    image_data=last_image,
                    image_format=report_data.images.format
                ),
                timeout=6  
            )
            L.debug(f"get_state_by_llm [message_id={message_id}] response:{response}, cost:{cost}")


            response["model"] = model_name
            response["cost"] = cost
            trace_tree.llm.model = model_name
            trace_tree.llm.cost = cost
            trace_tree.sleep_api_rsp_llm = response

            return response, cost
        except asyncio.TimeoutError:
            L.error(f"get_state_by_llm LLM请求超时 [message_id={message_id}]")
            return {}, 0
    except Exception as e:
        L.error(f"get_state_by_llm 发生异常 [message_id={message_id}]: {str(e)}\n{traceback.format_exc()}")
        return {}, 0

async def llm_response_to_state(response: dict) -> tuple[StateType, str, str]:
    state = None
    eye_status = None
    lie_status = None
    try:
        person_status = PersonStatus(**response)
        if person_status and person_status.sleepSignals:
            posture = person_status.sleepSignals.posture
            if posture == "sitting":
                state = StateType.SITTING_UP
                lie_status = BodyPoseType.Sit.value
            elif posture == "standing":
                state = StateType.LEAVING
                lie_status = BodyPoseType.Stand.value
            elif posture == "lying" or posture == "lying_down":
                state = StateType.PREPARE
                lie_status = BodyPoseType.Lie.value

            if person_status.sleepSignals.eyes == "closed":
                eye_status = EyeStatus.Closed.value
            
            if person_status.sleepSignals.eyes == "open":
                eye_status = EyeStatus.Open.value

            handActivity = person_status.sleepSignals.handActivity
            if handActivity == "active_device_use":
                state = StateType.USING_PHONE

        if person_status and not person_status.personPresent:
            state = StateType.LEAVING


    except Exception as e:
        L.error(f"response_to_state error:{e}")  

    return state, eye_status, lie_status