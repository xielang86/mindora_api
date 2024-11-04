from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from aivc.chat.chat import Chat
from aivc.utils.id import get_id
from typing import AsyncGenerator
from fastapi.responses import StreamingResponse
from aivc.config.config import L
from aivc.common.trace_tree import TraceTree

router = APIRouter()

class QARequest(BaseModel):
    question: str
    trace_sn: str

@router.post("/qa-stream", response_class=StreamingResponse)
async def qa_stream(request: Request, qa_request: QARequest):
    trace_sn = qa_request.trace_sn or get_id()
    question = qa_request.question
    L.debug(f"qa_stream trace_sn:{trace_sn} question:{question} remote:{request.client.host}")

    if not question:
        raise HTTPException(
            status_code=400,
            detail={
                "code": -1,
                "message": "question can't be empty",
                "trace_sn": trace_sn
            }
        )
    
    trace_tree = TraceTree()
    if trace_sn:
        trace_tree.root.message_id = trace_sn

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            chat_instance = Chat()
            async for chunk in chat_instance.chat_stream_by_sentence(
                    question=question,
                    trace_tree=trace_tree):  
                L.debug(f"chat_stream_by_sentence chunk:{chunk}")
                yield chunk
        except Exception as e:
            L.error(f"qa_stream error trace_sn:{trace_sn} error:{e}")
            yield None
        finally:
            pass

    return StreamingResponse(event_generator(), media_type="text/plain")

class QAResponse(BaseModel):
    code: int
    message: str
    content: str
    trace_sn: str
    cost: float

@router.post("/qa", response_model=QAResponse)
async def qa(request: Request, qa_request: QARequest):
    trace_sn = qa_request.trace_sn or get_id()
    question = qa_request.question
    L.debug(f"qa trace_sn:{trace_sn} question:{question} remote:{request.client.host}")

    if not question:
        raise HTTPException(
            status_code=400, 
            detail={
                "code": -1, 
                "message": "question can't be empty", 
                "trace_sn": trace_sn
            }
        )
    
    trace_tree = TraceTree()
    if trace_sn:
        trace_tree.root.message_id = trace_sn

    rsp = await Chat().chat(
        question=question,
        trace_tree=trace_tree
    )

    return QAResponse(
        code=0,
        message="success",
        content=rsp.content, 
        trace_sn=trace_sn, 
        cost=rsp.cost
    )
