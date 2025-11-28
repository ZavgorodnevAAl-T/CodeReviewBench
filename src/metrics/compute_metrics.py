from typing import List, Dict, Any, Optional, Tuple
from .base_metric import BaseMetric
from ..models.base_model import BaseLLM
from .exact_match import ExactMatchMetric
from .bleu import BLEUMetric
from .ChrF import ChrFMetric
from .multi_metric import MultiMetric
from .llm_based_exact_match import ExactMatchMetric as LLMExactMatchMetric
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class MetricsFactory:    
    @staticmethod
    def get_metric(metric_name: str, judge_model: Optional[BaseLLM] = None, **kwargs) -> BaseMetric:

        metric_name = metric_name.lower().strip()
        
        if metric_name in ['exact_match', 'exact-match']:
            return ExactMatchMetric(**kwargs)
        elif metric_name in ['bleu']:
            return BLEUMetric(**kwargs)
        elif metric_name in ['chrf', 'chr-f']:
            return ChrFMetric(**kwargs)
        elif metric_name in ['multi_metric', 'multi-metric', 'multimetric']:
            if judge_model is None:
                raise ValueError(f"Metric '{metric_name}' requires a judge_model parameter")
            return MultiMetric(model=judge_model, **kwargs)
        elif metric_name in ['llm_exact_match', 'llm-exact-match', 'llm_exact']:
            if judge_model is None:
                raise ValueError(f"Metric '{metric_name}' requires a judge_model parameter")
            return LLMExactMatchMetric(model=judge_model, **kwargs)
        else:
            raise ValueError(f"Unknown metric: {metric_name}")


def compute_metrics(
    predictions: List[List[str]], 
    outputs: List[str],
    diffs: List[str],
    metrics_to_compute: List[str], 
    judge_model: Optional[BaseLLM] = None,
    passes: List[int] = [1, 5, 10]
) -> Dict[str, Tuple[pd.DataFrame, pd.Series, pd.Series]]:
        
    results = {}
    
    for metric_name in metrics_to_compute:
        try:
            metric = MetricsFactory.get_metric(metric_name, judge_model)
            result = metric.calculate(outputs, predictions, passes, diffs)
            results[metric_name] = result
        except Exception as e:
            logger.error(f"Error computing metric '{metric_name}': {str(e)}")
            results[metric_name] = None
    
    return results