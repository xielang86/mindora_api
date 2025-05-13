from pydantic import BaseModel
from typing import Optional
from aivc.common.chat import ActionParams

class TTSRsp(BaseModel):
    code: int = 0
    message: str = ""
    action: Optional[str] = None
    text: Optional[str] = None
    action_params: Optional[ActionParams] = None
    audio_filename: Optional[str] = None
    audio_format: Optional[str] = None
    sample_format: Optional[str] = None 
    bitrate: Optional[int] = None
    channels: Optional[int] = None
    sample_rate: Optional[int] = None
    audio_data: Optional[bytes] = b""
    stream_seq: int = 0
    status: int = 0
    audio_path: Optional[str] = None   
    input_size: float = 0.0            
    output_length: int = 0              
    price: float = 0.0                  
    cost: int = 0  
    duration: Optional[int] = None # Added duration, similar to DoubaoLMTTS

    def __str__(self):
        return f"code: {self.code}, message: {self.message}, text: {self.text}, audio_path: {self.audio_path}, stream_seq:{self.stream_seq}, input_size: {self.input_size}, output_length: {self.output_length}, price: {self.price}, cost: {self.cost}, duration: {self.duration}"
