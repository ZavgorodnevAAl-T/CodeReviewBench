from .base_strategy import EvaluationStrategy
from ..models.base_model import BaseLLM
from typing import List, Optional, Callable
import pandas as pd
from configs.generation_config import GenerationConfig
from ..prompts.generation_prompt import SYSTEM_PROMPT
from ..metrics.compute_metrics import compute_metrics

class DefaultStrategy(EvaluationStrategy):
    def __init__(self, model: BaseLLM, judge_model: BaseLLM, metrics_to_compute: List[str], data_path: str = None):
        super().__init__(model, [], data_path)
        self.judge_model = judge_model
        self.metrics_to_compute = metrics_to_compute

    def evaluate(
        self,
        generation_config: GenerationConfig,
        passes: List[int] = [1, 5, 10],
        max_workers: int = 8,
        progress_callback: "Optional[Callable[[float, str], None]]" = None,
    ):
        n_generations = max(passes)

        # Generate n_generations times, each call returns one prediction per sample
        all_runs = []
        for i in range(n_generations):
            print(f"Generation run {i + 1}/{n_generations}")
            run = self.model.batch_generate(
                self.prompts, generation_config, system_prompt=SYSTEM_PROMPT, max_workers=max_workers
            )
            all_runs.append(run)

        # Transpose: List[run][sample] -> List[sample][run]
        predictions = [
            [all_runs[run_i][sample_i] or "" for run_i in range(n_generations)]
            for sample_i in range(len(self.prompts))
        ]

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
    
    