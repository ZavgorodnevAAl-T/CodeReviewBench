from .base_strategy import EvaluationStrategy
from ..models.base_model import BaseLLM
from typing import List, Optional
import json
import os
from configs.generation_config import GenerationConfig
from ..prompts.generation_prompt import SYSTEM_PROMPT
from ..metrics.compute_metrics import compute_metrics


class DefaultStrategy(EvaluationStrategy):
    def __init__(self, model: BaseLLM, metrics_to_compute: List[str], data_path: str = None):
        super().__init__(model, [], data_path)
        self.metrics_to_compute = metrics_to_compute

    def generate(
        self,
        generation_config: GenerationConfig,
        passes: List[int] = [1, 5, 10],
        max_workers: int = 8,
        cache_path: str = None,
    ) -> List[List[str]]:
        """Generate predictions (n=max(passes) runs per sample). Load from cache if available."""
        n_generations = max(passes)

        if cache_path and os.path.exists(cache_path):
            print(f"Loading generations from cache: {cache_path}")
            with open(cache_path) as f:
                predictions = [json.loads(line)["predictions"] for line in f]
            return predictions

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

        if cache_path:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "w") as f:
                for i, preds in enumerate(predictions):
                    f.write(json.dumps({"sample_idx": i, "predictions": preds}, ensure_ascii=False) + "\n")
            print(f"Saved generations to cache: {cache_path}")

        self.latest_predictions = predictions
        return predictions

    def evaluate(
        self,
        predictions: List[List[str]],
        judge_model: BaseLLM,
        passes: List[int] = [1, 5, 10],
    ):
        """Run metrics on pre-computed predictions using the given judge model."""
        return compute_metrics(
            predictions,
            self.outputs,
            self.diffs,
            self.metrics_to_compute,
            judge_model,
            passes,
        )
