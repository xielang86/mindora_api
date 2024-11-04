from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import os
from typing import Optional
from aivc.srt.manager import SRTManager, SRTType
from aivc.utils.id import get_id
from aivc.srt.common import SRTRsp
from aivc.config.config import settings

router = APIRouter()

class RecognizeResponse(BaseModel):
    code: int = 0
    message: str = ""
    audio_size: Optional[float] = None
    text: Optional[str] = None
    text_length: Optional[int] = None
    price: Optional[float] = None
    cost: Optional[int] = None
    trace_sn: Optional[str] = None


@router.post("/recognize-by-path", response_model=RecognizeResponse)
async def recognize_by_path(
    audio_path: str = Form(..., description="已知的音频文件路径"),
    srt_type: str = Form("XUNFEI", description="SRT识别类型，默认为 XUNFEI"),
    trace_sn: Optional[str] = Form(None, description="追踪标识，若未提供则自动生成")
):
    """
    接口1：通过已知的音频文件路径进行识别（POST请求）
    参数：
        - audio_path (str): 已知的音频文件路径（必填）
        - srt_type (str, 可选): SRT识别类型，默认为 "XUNFEI"
        - trace_sn (str, 可选): 追踪标识，若未提供则自动生成
    返回：
        识别结果
    """
    trace_sn = trace_sn or get_id()
    try:
        if not audio_path:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": -1,
                    "message": "audio_path 不能为空",
                    "trace_sn": trace_sn
                }
            )
        
        try:
            srt_type_enum = SRTType[srt_type.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": -1,
                    "message": f"无效的 srt_type: {srt_type}",
                    "trace_sn": trace_sn
                }
            )
        
        srt = SRTManager.create_srt(srt_type=srt_type_enum)
        rsp: SRTRsp = await srt.recognize(audio_path=audio_path)
        
        if rsp.code != 0:
            return RecognizeResponse(
                code=rsp.code,
                message=rsp.message,
                trace_sn=trace_sn
            )
        
        return RecognizeResponse(
            code=0,
            message="success",
            text=rsp.text,
            audio_size=rsp.audio_size,
            text_length=rsp.text_length,
            price=rsp.price,
            cost=rsp.cost,
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


@router.post("/recognize", response_model=RecognizeResponse)
async def recognize(
    file: UploadFile = File(..., description="上传的音频文件"),
    srt_type: str = Form("XUNFEI", description="SRT识别类型，默认为 XUNFEI"),
    trace_sn: Optional[str] = Form(None, description="追踪标识，若未提供则自动生成")
):
    """
    接口2：通过上传的音频文件进行识别（POST请求）
    参数：
        - file (UploadFile): 上传的音频文件（必填）
        - srt_type (str, 可选): SRT识别类型，默认为 "XUNFEI"
        - trace_sn (str, 可选): 追踪标识，若未提供则自动生成
    返回：
        识别结果
    """
    trace_sn = trace_sn or get_id()
    try:
        # 确保上传目录存在
        os.makedirs(settings.UPLOAD_ROOT_PATH, exist_ok=True)
        
        # 保存文件
        file_extension = os.path.splitext(file.filename)[1]
        saved_filename = f"{trace_sn}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_ROOT_PATH, saved_filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            srt_type_enum = SRTType[srt_type.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": -1,
                    "message": f"无效的 srt_type: {srt_type}",
                    "trace_sn": trace_sn
                }
            )
        
        srt = SRTManager.create_srt(srt_type=srt_type_enum)
        rsp: SRTRsp = await srt.recognize(audio_path=file_path)
        
        if rsp.code != 0:
            return RecognizeResponse(
                code=rsp.code,
                message=rsp.message,
                trace_sn=trace_sn
            )
        
        return RecognizeResponse(
            code=0,
            message="success",
            audio_size=rsp.audio_size,
            text=rsp.text,
            text_length=rsp.text_length,
            price=rsp.price,
            cost=rsp.cost,
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