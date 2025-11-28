from .base_judge import BaseJudge
from typing import List, Dict, Any, Optional, Tuple
from ..models.base_model import BaseLLM
from ..prompts.exact_match_prompt import EXACT_MATCH_PROMPT , SYSTEM_PROMPT
from configs.generation_config import GenerationConfig

class ExactMatchJudge(BaseJudge):
    def __init__(self, model: BaseLLM):
        self.model = model
        self.generation_config = GenerationConfig(
            max_new_tokens=4096,
            temperature=0.7,
            top_p=1.0
        )
    def judge(
        self,
        diffs: List[str],
        references: List[str],
        hypotheses_batch: List[List[str]],
    ) -> List[List[int]]:
        """
        Vectorised judge: builds *one* prompt list, sends it through a single
        batch_generate call, and reconstructs the per-sample results.

        Returns
        -------
        List[List[int]]
            Binary scores (1 = correct, 0 = incorrect) per hypothesis,
            preserving the original nested shape: [[h₀₀, h₀₁, …], [h₁₀, …], …]
        """

        prompt_counts: list[int] = []        
        flat_prompts: list[str] = []

        for diff, reference, hypotheses in zip(diffs, references, hypotheses_batch):
            prompt_counts.append(len(hypotheses))
            flat_prompts.extend(
                EXACT_MATCH_PROMPT.format(
                    reference=reference,
                    hypothesis=hypothesis,
                )
                for hypothesis in hypotheses
            )

        # 2. One-shot generation
        raw_responses = self.model.batch_generate(
            prompts=flat_prompts,
            system_prompt=SYSTEM_PROMPT,
            generation_config=self.generation_config,
        )

        flat_scores: list[int] = [
            0
            if (resp is None or "wrong" in str(resp).lower())
            else 1
            for resp in raw_responses
        ]

        # 4. Reshape flat_scores back to the original nested structure
        batch_results: list[list[int]] = []
        idx = 0
        for count in prompt_counts:
            batch_results.append(flat_scores[idx : idx + count])
            idx += count

        return batch_results