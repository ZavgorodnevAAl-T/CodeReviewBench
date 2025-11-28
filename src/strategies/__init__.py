from .default_strategy import DefaultStrategy
from ..models.base_model import BaseLLM
from typing import List

STRATEGY_REGISTRY = {
    "default": DefaultStrategy
}

class StrategyFactory:
    def __init__(self):
        self.strategies = STRATEGY_REGISTRY
    
    def get_strategy(self, strategy_name: str, model: BaseLLM, judge_model: BaseLLM, metrics_to_compute: List[str]):
        if strategy_name not in self.strategies:
            raise ValueError(f"Strategy {strategy_name} not found")
        return self.strategies[strategy_name](model, judge_model, metrics_to_compute)