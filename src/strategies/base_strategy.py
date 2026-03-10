from abc import ABC, abstractmethod
from ..models.base_model import BaseLLM
from ..metrics.base_metric import BaseMetric
from typing import List
from ..utils.load_data import load_data

class EvaluationStrategy(ABC):
    def __init__(self, model: BaseLLM, metrics_to_compute: list[BaseMetric], data_path: str = None):
        self.model = model
        self.metrics_to_compute = metrics_to_compute
        self.data = load_data(data_path)
        self.prompts = self.data["prompts"]
        self.outputs = self.data["outputs"]
        self.diffs = self.data["diffs"]

        # Taxonomy / metadata for filtering in UI
        self.comment_language = self.data.get("comment_language", [])
        self.programming_language = self.data.get("language", [])
        self.topic = self.data.get("topic", [])

    @abstractmethod
    def evaluate(self, code: str, reference: str) -> float:
        pass