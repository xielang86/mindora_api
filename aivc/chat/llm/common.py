from pydantic import BaseModel
from typing import Optional

class LLMRsp(BaseModel):
    content: str
    input_tokens: int
    output_tokens: int
    price: float
    cost: float
    
class PricingInfo(BaseModel):
    input: float
    output: float

class ModelInfo(BaseModel):
    name: str
    context_size: int = 0
    pricing: Optional[PricingInfo] = None
    local_path: str = ""