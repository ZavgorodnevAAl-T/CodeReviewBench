from ..judge.multimetric_judge import MultimetricJudge
from ..models.base_model import BaseLLM
from typing import List, Tuple
from .base_metric import BaseMetric
import json
import pandas as pd
from pydantic import BaseModel

class MultiMetricResult(BaseModel):
    readability: float
    relevance: float
    problem_identification: float
    actionability: float
    specificity: float

class MultiMetric(BaseMetric):
    def __init__(self, model: BaseLLM, **kwargs):
        self.judge = MultimetricJudge(model)
        
        
    def calculate(self, references: List[str], hypotheses: List[List[str]], diffs: List[str]) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        first_only = [hyp[:1] if hyp else [""] for hyp in hypotheses]
        scores = self.judge.judge(diffs, references, first_only)
        scores = [score.model_dump() for score in scores]
        df = pd.DataFrame(scores)
        return df, df.mean(axis=0), self.standard_error(df)
    
    @property
    def name(self) -> str:
        return "multi_metric"