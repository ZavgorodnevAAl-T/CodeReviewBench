from .base_strategy import EvaluationStrategy
from ..models.base_model import BaseLLM
from typing import List, Optional, Callable
import pandas as pd
from configs.generation_config import GenerationConfig
from ..utils.predictions_parser import parse_predictions
from ..prompts.generation_prompt import SYSTEM_PROMPT
from ..metrics.compute_metrics import compute_metrics

class DefaultStrategy(EvaluationStrategy):
    def __init__(self, model: BaseLLM, judge_model: BaseLLM, metrics_to_compute: List[str]):
        super().__init__(model, [])
        self.judge_model = judge_model
        self.metrics_to_compute = metrics_to_compute

    def evaluate(
        self,
        generation_config: GenerationConfig,
        passes: List[int] = [1, 5, 10],
        progress_callback: "Optional[Callable[[float, str], None]]" = None,
    ):

        predictions = self.model.batch_generate(
            self.prompts, generation_config, system_prompt=SYSTEM_PROMPT
        )

        predictions = parse_predictions(predictions)
        sanitize_preds: list[list[str]] = []
        for hyp_list in predictions:
            if not hyp_list:
                sanitize_preds.append([""])  # placeholder empty string
            else:
                sanitize_preds.append(hyp_list)

        predictions = sanitize_preds

        metrics_results = compute_metrics(
            predictions,
            self.outputs,
            self.diffs,
            self.metrics_to_compute,
            self.judge_model,
            passes,
        )

        # Expose predictions for inspection in UI
        self.latest_predictions = predictions  # type: ignore[attr-defined]

        return metrics_results
    
    