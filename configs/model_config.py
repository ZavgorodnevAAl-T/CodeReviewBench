from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ModelType(Enum):
    OPENAI = "openai"

class ModelConfig(BaseModel):    
    model_type: ModelType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_path: str
    
    
