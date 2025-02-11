import os
from fastapi import HTTPException, status
from aivc.config.config import L, settings

def get_filename(trace_sn: str) -> str:
    return f"{trace_sn}"

def get_file_extension(filename: str) -> str:
    return filename.split(".")[-1].lower()

async def validate_audio_file_size(filepath:str):
    MAX_FILE_SIZE = 10 * 1024 * 1024  

    L.debug(f"validate_audio_file_size filepath:{filepath}")
    file_size = os.path.getsize(filepath)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制: {MAX_FILE_SIZE / (1024 * 1024)} MB",
        )

    return file_size

async def save_upload_file(
    file_data: bytes, 
    trace_sn: str) -> str:
    os.makedirs(settings.UPLOAD_ROOT_PATH, exist_ok=True)
    saved_filename = get_filename(trace_sn)
    file_path = os.path.join(settings.UPLOAD_ROOT_PATH, saved_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file_data)
    return file_path