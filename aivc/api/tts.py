from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from aivc.tts.manager import TTSManager, TTSType
from aivc.utils.id import get_id
from aivc.tts.common import TTSRsp
from fastapi.responses import StreamingResponse
from io import BytesIO
from aivc.config.config import L

router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    tts_type: Optional[str] = "XUNFEI"
    trace_sn: Optional[str] = ""

class TTSResponse(BaseModel):
    code: int
    message: str
    audio_data_base64: Optional[str] = None
    audio_path: Optional[str] = None
    cost: Optional[int] = None
    trace_sn: Optional[str] = None

@router.post("/tts", response_model=TTSResponse)
async def tts(request: TTSRequest):
    """
    新增接口：通过文本进行语音合成（POST请求）
    参数：
        - text (str): 需要进行语音合成的文本（必填）
        - tts_type (str, 可选): TTS语音合成类型，默认为 "XUNFEI"
        - trace_sn (str, 可选): 追踪标识，若未提供则自动生成
    返回：
        语音合成结果
    """
    trace_sn = request.trace_sn or get_id()
    L.debug(f"tts trace_sn:{trace_sn} text:{request.text} tts_type:{request.tts_type}")

    try:
        if not request.text:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": -1,
                    "message": "text 不能为空",
                    "trace_sn": trace_sn
                }
            )
        
        try:
            tts_type_enum = TTSType[request.tts_type.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": -1,
                    "message": f"无效的 tts_type: {request.tts_type}",
                    "trace_sn": trace_sn
                }
            )
        
        tts = TTSManager.create_tts(tts_type=tts_type_enum)
        response: TTSRsp = await tts.tts(text=request.text)
        
        if response.code != 0:
            return TTSResponse(
                code=response.code,
                message=response.message,
                trace_sn=trace_sn
            )
        
        return TTSResponse(
            code=0,
            message="success",
            audio_data_base64=response.audio_data_base64,
            audio_path=response.audio_path,
            cost=response.cost,
            trace_sn=trace_sn
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": -1,
                "message": str(e),
                "trace_sn": trace_sn
            }
        )


@router.post("/tts-stream")
async def tts_stream(request: TTSRequest):
    trace_sn = request.trace_sn or get_id()
    L.debug(f"tts_stream start trace_sn:{trace_sn} text:{request.text} tts_type:{request.tts_type}")

    try:
        if not request.text:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": -1,
                    "message": "text 不能为空",
                    "trace_sn": trace_sn
                }
            )
        
        try:
            tts_type_enum = TTSType[request.tts_type.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": -1,
                    "message": f"无效的 tts_type: {request.tts_type}",
                    "trace_sn": trace_sn
                }
            )
        
        tts = TTSManager.create_tts(tts_type=tts_type_enum)
        response: TTSRsp = await tts.tts(text=request.text)
        L.debug(f"tts_stream done trace_sn:{trace_sn} cost:{response.cost}")
        
        if response.code != 0:
            return TTSResponse(
                code=response.code,
                message=response.message,
                trace_sn=trace_sn
            )
        
        # 将bytes转换为BytesIO
        buffer = BytesIO(response.audio_data)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="audio/x-pcm",
            headers={
                "Content-Type": "audio/x-pcm",
                "Sample-Rate": "16000",
                "Channels": "1",
                "Sample-Format": "S16LE",
                "Bitrate": "256000"
            }
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": -1,
                "message": str(e),
                "trace_sn": trace_sn
            }
        )
    
