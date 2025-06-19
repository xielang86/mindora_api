from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from aivc.config.config import settings,L
from aivc.common.chat import Req, VCMethod, Resp, VCReqData, VCRespData,ReportReqData,ActionRespData
from aivc.common.trace_tree import TraceTree, TraceRoot
from aivc.sop.common.common import Actions
from aivc.sop.common.manager import CommandDataManager
from aivc.common.task_class import QuestionType

async def handle_command_request(
    websocket: WebSocket,
    req_data: dict,
    message_id: str,
    conversation_id: str
):
    req = Req[VCReqData](**req_data)
    trace_tree = TraceTree(
        root = TraceRoot(
            client_addr=f"{websocket.client.host}:{websocket.client.port}",
            method=req.method,
            conversation_id=req.conversation_id,
            message_id=req.message_id,
            req_timestamp=req.timestamp
        )
    )

    req_command = req.data.content if req.data and req.data.content else ""
    
    # 使用 CommandDataManager 获取命令数据（支持自动加载）
    command_data_manager = CommandDataManager()
    actions_dict, error = await command_data_manager.get_command_data(req_command)
    if error:
        L.error(f"处理命令失败: {error}")
        # 发送错误响应给客户端
        error_resp = Resp[ActionRespData](
            method=VCMethod.COMMAND,
            conversation_id=conversation_id,
            message_id=message_id,
            code=400,
            message=error,
        )
        return error_resp

    # 获取第一个动作（取字典中的第一个值）
    first_action = next(iter(actions_dict.values())) if actions_dict else None
    first_scene = next(iter(actions_dict.keys())) if actions_dict else None
    first_scene_seq = 1

    # 第一阶段，不开摄像头
    if first_action:
        first_action.skip_photo_capture = True

    # 发送成功响应给客户端
    success_resp = Resp[ActionRespData](
        method=VCMethod.EXECUTE_COMMAND,
        conversation_id=conversation_id,
        message_id=message_id,
        data=ActionRespData(
            cmd=req_command,
            scene=first_scene,
            scene_seq=first_scene_seq,
            actions=first_action
        )
    )
    return success_resp