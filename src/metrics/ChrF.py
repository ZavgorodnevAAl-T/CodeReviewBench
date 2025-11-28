import evaluate
from .base_metric import BaseMetric
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

class ChrFMetric(BaseMetric):
    def __init__(self, **kwargs):
        self.metric = evaluate.load("chrf")
        
    def calculate(self, references: List[str], hypothesises: List[List[str]], passes: List[int], diffs: List[str]) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        scores = []
        for reference, hypotheses in zip(references, hypothesises):
            micro_scores = []
            for hypothesis in hypotheses:
                micro_scores.append(self.metric.compute(predictions=[hypothesis], references=[[reference]])["score"])
            scores.append({f"{self.name}_judge_{k}": max(micro_scores[:k]) for k in passes})
        scores = pd.DataFrame(scores)
        return scores, scores.mean(axis=0), self.standard_error(scores)
        
    @property
    def name(self) -> str:
        return "chrf"
