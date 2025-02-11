import typing
import base64
import os.path
from aivc.common.chat import Req, ReportReqData, Resp, ActionRespData, VCMethod
from aivc.common.trace_tree import TraceTree, TraceRoot
from aivc.common.file import save_upload_file
from aivc.chat.sleep_dect_rpc import get_state_by_api,determine_state_type,get_actions,StateManager
from aivc.config.config import  L
import traceback
from aivc.common.sleep_config import StateType
import asyncio
from aivc.data.db.trace_log import save_trace
from aivc.data.db.pg_engine import engine
from sqlmodel import Session
from aivc.chat import conversation
from aivc.common.task_class import QuestionType

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
        L.debug(f"handler_robot_report scene_exec_status: {req.data.scene_exec_status}")

        # 本地状态机
        local_state = await StateManager().update_state_by_exec_status(req.conversation_id,req.data.scene_exec_status)

        # 保存文件
        audio_path, image_paths = await save_report_files(req.data, req.message_id)
        L.debug(f"save_report_files audio_path: {audio_path} image_paths: {image_paths}")

        # AI服务检测
        api_rsp = await get_state_by_api(req.data, trace_tree)
        api_state = None
        if api_rsp:
            api_state = determine_state_type(
                sleep_status=api_rsp.sleep_status,
                pose = api_rsp.data.pose_info,
                recent_action=api_rsp.data.recent_action.body_action
            )
        L.debug(f"api_rsp: {api_rsp} api_state:{api_state}")

        # 测试用代码
        # api_state = StateType.PREPARE

        current_state = get_curren_state(local_state, api_state)
        L.debug(f"current_state: {current_state} local_state:{local_state} api_state:{api_state}")

        if current_state is None:
            L.error("无法获取当前状态")
            return None

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

        def save_trace_with_session():
            add_params_to_trace_tree(trace_tree, req, audio_path, image_paths, rsp)
            with Session(engine) as session:
                save_trace(session, trace_tree)
        await asyncio.to_thread(save_trace_with_session)

        return rsp
    except Exception as e:
        L.error(f"Error handling robot report: {str(e)} \ntraceback:\n{traceback.format_exc()}")
        return None


def get_curren_state(local_state: StateType, api_state: StateType) -> StateType:
    # API请求失败时，直接返回本地状态
    if not api_state:
        return local_state

    # API状态检测到睡眠状态时，直接返回
    if api_state.order >= StateType.SLEEP_READY.order:
        return api_state
    
    # 本地状态机处于准备状态时，本地顺序执行
    if api_state in [StateType.PREPARE]:
        if local_state:
            return local_state
        else:
            return api_state 
    
    return api_state

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
        if rsp_dict and "data" in rsp_dict:
            voices = rsp_dict.get("data", {}).get("actions", {}).get("voice", {}).get("voices")
            if voices:
                for voice in voices :
                    if "audio_data" in voice and voice["audio_data"]:
                        voice["audio_data"] = "audio_data len "+str(len(voice["audio_data"]))
        
        trace_tree.sleep_rsp = rsp_dict
    except Exception as e:
        L.error(f"Error adding params to trace tree: {str(e)}")

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
