from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from ..models.base_model import BaseLLM


class BaseJudge(ABC):
    @abstractmethod
    def __init__(self, model: BaseLLM, **kwargs):
        pass
    
    @abstractmethod
    def judge(self, reference: str, hypothesis: List[str]) -> Tuple[List[float], float]:
        pass