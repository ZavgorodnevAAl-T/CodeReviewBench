from .base_metric import BaseMetric
from typing import List, Dict, Any, Optional, Tuple
from ..judge.exact_match_judge import ExactMatchJudge
from ..models.base_model import BaseLLM
import pandas as pd

class ExactMatchMetric(BaseMetric):
    def __init__(self, model: BaseLLM, **kwargs):
        self.judge = ExactMatchJudge(model)
        
    def calculate(
        self,
        references: List[str],
        hypothesises: List[List[str]],
        passes: List[int],
        diffs: List[str],
    ) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """Compute LLM-based exact-match scores.

        The judge returns a list of *per-hypothesis* binary scores for every sample.
        We convert them into the common *max@k* format (same as other metrics).
        """

        all_scores: list[dict[str, float]] = []

        # Obtain per-hypothesis judgements for the whole batch in one call
        batch_scores: list[list[int]] = self.judge.judge(diffs, references, hypothesises)

        for micro_scores in batch_scores:
            if not micro_scores:
                # Guard against empty hypothesis list (should not happen, but be safe)
                micro_scores = [0]

            row = {
                f"{self.name}_judge_{k}": max(micro_scores[:k]) for k in passes
            }
            all_scores.append(row)

        df = pd.DataFrame(all_scores)
        return df, df.mean(axis=0), self.standard_error(df)
    
    @property
    def name(self) -> str:
        return "llm_based_exact_match"
