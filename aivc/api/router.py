from fastapi import APIRouter
from aivc.api import chat, srt, tts, voice_chat

api_router_v1 = APIRouter()
api_router_v1.include_router(voice_chat.router, tags=["voice_chat"])
api_router_v1.include_router(chat.router, tags=["chat"])
api_router_v1.include_router(srt.router, tags=["srt"])
api_router_v1.include_router(tts.router, tags=["tts"])
