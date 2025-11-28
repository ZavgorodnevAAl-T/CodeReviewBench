from typing import List, Tuple
from ..models.base_model import BaseLLM
from ..prompts.multimetric_prompt import USER_PROMPT_MULTIMETRIC as MULTIMETRIC_JUDGE_PROMPT, SYSTEM_PROMPT
from pydantic import BaseModel
from .base_judge import BaseJudge
from configs.generation_config import GenerationConfig

class Metrics(BaseModel):
    readability: int
    relevance: int
    explanation_clarity: int
    problem_identification: int
    actionability: int
    completeness: int
    specificity: int
    contextual_adequacy: int
    consistency: int
    brevity: int

class MultimetricJudge(BaseJudge):
    def __init__(self, model: BaseLLM):
        self.model = model
        self.generation_config = GenerationConfig(
            max_new_tokens=4096,
            temperature=0.7,
            top_p=1.0
        )
    def judge(self, diff: List[str], references: List[str], hypotheses: List[List[str]]) -> List[Metrics]:
        
        prompts = [
            MULTIMETRIC_JUDGE_PROMPT.format(
                diff=diff,
                hypothesis=hypotheses[0]
            )
            for diff, hypotheses in zip(diff, hypotheses)
        ]
        
        responses = self.model.batch_generate(
            prompts=prompts,
            system_prompt=SYSTEM_PROMPT,
            response_format=Metrics,
                        generation_config=self.generation_config,

        )
        
        return responses