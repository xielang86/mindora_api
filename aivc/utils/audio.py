import base64

def calculate_pcm_duration(
        buffer: bytes, 
        sample_rate: int = 16000, 
        channels: int = 1, 
        sample_format: str = "S16LE") -> float:
    if sample_format == "S16LE":
        bytes_per_sample = 2  # 16位 = 2字节
    elif sample_format == "S32LE":
        bytes_per_sample = 4  # 32位 = 4字节
    elif sample_format == "F32LE":
        bytes_per_sample = 4  # 32位浮点
    else:
        raise ValueError(f"Unsupported sample format: {sample_format}")
    
    # 每帧的字节数
    bytes_per_frame = channels * bytes_per_sample
    
    # 总帧数
    total_frames = len(buffer) / bytes_per_frame
    
    # 时长（秒）
    duration_seconds = total_frames / sample_rate
    
    return duration_seconds

def audio_file_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        buffer = f.read()
    return base64.b64encode(buffer).decode()