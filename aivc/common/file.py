import os
import time
import asyncio
from pathlib import Path
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

async def cleanup_old_files() -> dict:
    """
    清理预定义目录下24小时前的文件
    清理目录：UPLOAD_ROOT_PATH 和 OUTPUT_ROOT_PATH
    
    Returns:
        dict: 包含删除统计信息的字典
    """
    result = {
        "deleted_count": 0,
        "failed_count": 0,
        "total_size_freed": 0,
        "errors": [],
        "cleaned_directories": []
    }
    
    # 定义要清理的目录列表
    directories_to_clean = [
        settings.UPLOAD_ROOT_PATH,
        settings.OUTPUT_ROOT_PATH
    ]
    
    hours_threshold = settings.FILE_CLEANUP_HOURS_THRESHOLD
    current_time = time.time()
    threshold_seconds = hours_threshold * 3600
    cutoff_time = current_time - threshold_seconds
    
    L.info(f"开始清理预定义目录，删除 {hours_threshold} 小时前的文件")
    
    for directory_path in directories_to_clean:
        try:
            # 检查目录是否存在
            if not os.path.exists(directory_path):
                L.warning(f"目录不存在: {directory_path}")
                continue
            
            if not os.path.isdir(directory_path):
                L.warning(f"路径不是目录: {directory_path}")
                continue
            
            L.info(f"清理目录: {directory_path}")
            result["cleaned_directories"].append(directory_path)
            
            # 遍历目录中的文件
            for root, dirs, files in os.walk(directory_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    
                    try:
                        # 获取文件状态
                        file_stat = os.stat(file_path)
                        file_mtime = file_stat.st_mtime
                        file_size = file_stat.st_size
                        
                        # 检查文件是否超过时间阈值
                        if file_mtime < cutoff_time:
                            # 删除文件
                            os.remove(file_path)
                            result["deleted_count"] += 1
                            result["total_size_freed"] += file_size
                            
                            L.info(f"已删除旧文件: {file_path} (大小: {file_size} bytes)")
                            
                            # 添加小延迟避免过度占用系统资源
                            await asyncio.sleep(0.001)
                        
                    except PermissionError as e:
                        error_msg = f"权限错误，无法删除文件 {file_path}: {e}"
                        L.error(error_msg)
                        result["failed_count"] += 1
                        result["errors"].append(error_msg)
                        
                    except FileNotFoundError:
                        # 文件可能在检查和删除之间被其他进程删除了
                        L.debug(f"文件已不存在，可能被其他进程删除: {file_path}")
                        
                    except Exception as e:
                        error_msg = f"删除文件时发生错误 {file_path}: {e}"
                        L.error(error_msg)
                        result["failed_count"] += 1
                        result["errors"].append(error_msg)
            
        except Exception as e:
            error_msg = f"清理目录 {directory_path} 时发生错误: {e}"
            L.error(error_msg)
            result["errors"].append(error_msg)
    
    L.info(f"清理完成。删除文件数: {result['deleted_count']}, "
           f"失败数: {result['failed_count']}, "
           f"释放空间: {result['total_size_freed']} bytes, "
           f"清理目录: {result['cleaned_directories']}")
    
    return result