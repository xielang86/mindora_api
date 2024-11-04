from pydantic import BaseModel

class SRTRsp(BaseModel):
    code: int = 0
    message: str = ""
    audio_size: float = 0.0
    text: str
    text_length: int = 0
    price: float = 0.0
    cost: int = 0
