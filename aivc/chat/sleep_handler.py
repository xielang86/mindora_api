import typing
import base64
import os.path
from dataclasses import dataclass
from aivc.common.chat import Req, ReportReqData, Resp, ActionRespData, VCMethod
from aivc.common.trace_tree import TraceTree, TraceRoot
from aivc.common.file import save_upload_file
from aivc.chat.sleep_dect_rpc import get_state_by_api,determine_state_type,get_actions,get_state_by_llm,llm_response_to_state
from aivc.chat.sleep_state import StateManager, SleepMonitor
from aivc.chat.sleep_alert_state import AlertStateManager
from aivc.config.config import  L,settings
import traceback
from aivc.common.sleep_config import StateType
import asyncio
from aivc.data.db.trace_log import save_trace
from aivc.data.db.pg_engine import engine
from sqlmodel import Session
from aivc.chat import conversation
from aivc.common.task_class import QuestionType
import time


async def handler_robot_report(req_data: typing.Any, client_addr:str) -> typing.Any:
    try:
        req = Req[ReportReqData](**req_data)
        trace_tree = TraceTree(
            root = TraceRoot(
                client_addr=client_addr,
                method=req.method,
                conversation_id=req.conversation_id,
                message_id=req.message_id,
                req_timestamp=req.timestamp
            )
        )
        L.debug(f"handler_robot_report scene_exec_status: {req.data.scene_exec_status} msg_id:{req.message_id}")

        # 直接使用 StateManager() 即可,它会返回同一个实例
        local_state = await StateManager().update_state_by_exec_status(
            req.conversation_id,
            req.data.scene_exec_status
        )

        # 保存文件
        audio_path, image_paths = await save_report_files(req.data, req.message_id)
        L.debug(f"save_report_files audio_path: {audio_path} image_paths: {image_paths} msg_id:{req.message_id}")

        start_time = time.time()
        # 调用独立出来的服务函数获取状态
        service_states = await get_states_from_services(
            req.data, trace_tree
        )
        L.debug(f"get_states_from_services cost: {round(time.time() - start_time, 3)} msg_id:{req.message_id}")


        # 通过配置修改mock状态
        if settings.AI_RPC_MOCK:
            L.debug("AI_RPC_MOCK is True, use local state")
            service_states.api_state = StateType.PREPARE

        # 睡眠状态检测
        await SleepMonitor().check_sleep_condition(
            conversation_id = req.conversation_id,
            eye_status = service_states.eye_status,
            lie_status = service_states.lie_status,
            current_state = service_states.api_state)
        if await SleepMonitor().is_sleeping(req.conversation_id):
            service_states.api_state = StateType.DEEP_SLEEP
            L.debug(f"req.conversation_id:{req.conversation_id} is_sleeping api_state:{service_states.api_state}")

        current_state = get_curren_state(local_state, service_states.api_state, service_states.llm_state)
        L.debug(f"current_state: {current_state} local_state:{local_state} api_state:{service_states.api_state} llm_state:{service_states.llm_state} req.message_id:{req.message_id}")

        alert_level = None
        actions = None
        if current_state is None:
            L.error("无法获取当前状态")
            return None
        else:
            alert_level, actions = await AlertStateManager().update_state(req.conversation_id, current_state)
            L.debug(f"AlertStateManager update_state: {alert_level} actions: {actions} msg_id:{req.message_id}")
    
        if alert_level and actions:
            # 如果触发告警，直接返回告警动作
            rsp = Resp[ActionRespData](
                version="1.0",
                method=VCMethod.EXECUTE_COMMAND,
                conversation_id=req.conversation_id,
                message_id=req.message_id,
                data=ActionRespData(
                    scene=actions.action_feature,  
                    scene_seq=0, 
                    actions=actions
                )
            )
            return rsp
        else:
            # 如果没有告警，使用本地流程
            current_state = local_state
            actions = await get_actions(current_state)
            rsp = Resp[ActionRespData](
                version="1.0",
                method=VCMethod.EXECUTE_COMMAND,
                conversation_id=req.conversation_id,
                message_id=req.message_id,
                data=ActionRespData(
                    scene=current_state.name_cn,  
                    scene_seq=current_state.order, 
                    actions=actions
                )
            )

        # 创建异步任务处理日志和轨迹，不阻塞主流程
        asyncio.create_task(process_logs_and_traces(
            current_state,
            actions,
            trace_tree,
            req,
            audio_path,
            image_paths,
            rsp
        ))

        return rsp
    except Exception as e:
        L.error(f"Error handling robot report: {str(e)} \ntraceback:\n{traceback.format_exc()} msg_id:{req_data.get('message_id')}")
        return None


@dataclass
class ServiceStates:
    api_state: typing.Optional[StateType] = None
    eye_status: typing.Optional[str] = None
    lie_status: typing.Optional[str] = None
    llm_state: typing.Optional[StateType] = None
    llm_eye_status: typing.Optional[str] = None
    llm_lie_status: typing.Optional[str] = None


async def get_states_from_services(report_data: ReportReqData, trace_tree: TraceTree) -> ServiceStates:
    message_id = trace_tree.root.message_id
    states = ServiceStates()

    try:
        api_task = asyncio.create_task(get_state_by_api(report_data, trace_tree))
        llm_task = asyncio.create_task(get_state_by_llm(report_data, trace_tree))
        
        done, pending = await asyncio.wait(
            [api_task, llm_task], 
            timeout=3, # 超时时间
            return_when=asyncio.ALL_COMPLETED
        )
        
        for task in done:
            if task is api_task:
                api_rsp = task.result()
                if api_rsp:
                    states.api_state, states.eye_status, states.lie_status = determine_state_type(
                        sleep_status=api_rsp.sleep_status,
                        pose=api_rsp.data.pose_info,
                        recent_action=api_rsp.data.recent_action.body_action
                    )
                L.debug(f"get_states_from_services api_rsp: {api_rsp} api_state:{states.api_state} eye_status:{states.eye_status} lie_status:{states.lie_status} msg_id:{message_id}")
            
            elif task is llm_task:
                llm_rsp, llm_cost = task.result()
                states.llm_state, states.llm_eye_status, states.llm_lie_status = await llm_response_to_state(llm_rsp)
                L.debug(f"get_states_from_services llm_rsp: {llm_rsp} llm_state:{states.llm_state} llm_eye_status:{states.llm_eye_status} llm_lie_status:{states.llm_lie_status} llm_cost:{llm_cost} msg_id:{message_id}")
        
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                if task is api_task:
                    L.warning(f"get_states_from_services API检测任务超时被取消 msg_id:{message_id}")
                else:
                    L.warning(f"get_states_from_services LLM检测任务超时被取消 msg_id:{message_id}")
            except Exception as e:
                L.error(f"get_states_from_services 取消任务时发生错误: {str(e)} \ntraceback:\n{traceback.format_exc()} msg_id:{message_id}")
        
    except Exception as e:
        L.error(f"get_states_from_services 并行任务执行错误: {str(e)} \ntraceback:\n{traceback.format_exc()} msg_id:{message_id}")
    
    return states


def get_curren_state(
        local_state: StateType, 
        api_state: StateType,
        llm_state: StateType) -> StateType:
    # API请求失败时，直接返回本地状态
    if not api_state and not llm_state:
        return local_state

    sp_state_list = [StateType.USING_PHONE, StateType.SITTING_UP]
    # 如果一方判断到使用手机状态，一方判断坐起状态，返回使用坐起状态
    if (api_state in sp_state_list and llm_state in sp_state_list) and api_state != llm_state:
        return StateType.SITTING_UP

    # SITTING_UP OR 
    if api_state == StateType.SITTING_UP or llm_state == StateType.SITTING_UP:
        return StateType.SITTING_UP
    
    # USING_PHONE AND
    if api_state == StateType.USING_PHONE and llm_state == StateType.USING_PHONE:
        return StateType.USING_PHONE

    # 本地状态机处于准备状态时，本地顺序执行
    if api_state in [StateType.PREPARE]:
        if local_state:
            return local_state
        else:
            return api_state 
    
    return local_state

def get_curren_state_only_api(
        local_state: StateType, 
        api_state: StateType,
        llm_state: StateType) -> StateType:
    # API请求失败时，直接返回本地状态
    if not api_state:
        return local_state

    sp_state_list = [StateType.USING_PHONE, StateType.SITTING_UP]
    # 如果一方判断到使用手机状态，一方判断坐起状态，返回使用坐起状态
    if (api_state in sp_state_list):
        return api_state

    # 本地状态机处于准备状态时，本地顺序执行
    if api_state in [StateType.PREPARE]:
        if local_state:
            return local_state
        else:
            return api_state 
    
    return local_state

def add_params_to_trace_tree(
        trace_tree: TraceTree, 
        req: Req,
        audio_path: str = None,
        image_paths: typing.List[str] = [],
        rsp: Resp = None):
    
    try:
        # 使用 os.path.basename 从路径中提取文件名
        audio_file = os.path.basename(audio_path) if audio_path else None
        image_files = [os.path.basename(path) for path in image_paths] if image_paths else []
        
        req_dict = req.model_dump() 
        if "data" in req_dict:
            req_dict["data"] = {}
            req_dict["data"]["image_files"] = image_files
            req_dict["data"]["audio_file"] = audio_file
        else:
            req_dict["data"] = {
                "image_files": image_files,
                "audio_file": audio_file
            }
        trace_tree.sleep_req = req_dict
    except Exception as e:
        L.error(f"Error adding params to trace tree: {str(e)}")
    
    try:
        rsp_dict = rsp.model_dump() if rsp else None
        if rsp_dict:
            data = rsp_dict.get("data")
            if data and isinstance(data, dict):
                actions = data.get("actions")
                if actions and isinstance(actions, dict):
                    voice = actions.get("voice")
                    if voice and isinstance(voice, dict):
                        voices = voice.get("voices")
                        if voices and isinstance(voices, list):
                            for voice in voices:
                                if isinstance(voice, dict) and "audio_data" in voice and voice["audio_data"]:
                                    voice["audio_data"] = "audio_data len " + str(len(voice["audio_data"]))
        
        trace_tree.sleep_rsp = rsp_dict
    except Exception as e:
        L.error(f"Error adding params to trace tree: {str(e)} \ntraceback:\n{traceback.format_exc()}")

async def save_report_files(data: ReportReqData, trace_sn: str) -> tuple[str | None, list[str]]:
    audio_path = None
    image_paths = []
    
    # 保存音频文件
    if data.audio and data.audio.data:
        audio_bytes = base64.b64decode(data.audio.data)
        audio_path = await save_upload_file(
            audio_bytes,
            f"{trace_sn}.wav"
        )
    
    # 保存图片文件
    if data.images and data.images.data:
        for idx, image_data in enumerate(data.images.data):
            if image_data:
                image_bytes = base64.b64decode(image_data)
                image_path = await save_upload_file(
                    image_bytes,
                    f"{trace_sn}_{idx}.jpg"
                )
                image_paths.append(image_path)
                
    return audio_path, image_paths

async def process_logs_and_traces(
    current_state: StateType,
    actions: typing.Any,
    trace_tree: TraceTree,
    req: Req,
    audio_path: str,
    image_paths: typing.List[str],
    rsp: Resp
):
    """异步处理日志和轨迹数据，不阻塞主流程"""
    try:
        # 保存对话记录
        if current_state.is_abnormal():
            answer = ""
            if actions and actions.voice and actions.voice.voices:
                answer = actions.voice.voices[0].text
            await asyncio.to_thread(
                conversation.save_conversation, 
                req.conversation_id, 
                "", 
                answer,
                question_type=QuestionType.SLEEP_ASSISTANT.value)
        
        # # 旁路请求get_state_by_llm
        # llm_rsp, llm_cost = await get_state_by_llm(
        #     report_data=req.data,
        #     trace_tree=trace_tree
        # )

        # 保存trace
        def save_trace_with_session():
            add_params_to_trace_tree(trace_tree, req, audio_path, image_paths, rsp)
            with Session(engine) as session:
                save_trace(session, trace_tree)
        await asyncio.to_thread(save_trace_with_session)
    except Exception as e:
        L.error(f"Error in process_logs_and_traces: {str(e)} \ntraceback:\n{traceback.format_exc()}")
