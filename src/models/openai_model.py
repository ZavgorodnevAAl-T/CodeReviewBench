from openai import OpenAI
from .base_model import BaseLLM
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm
from configs.generation_config import GenerationConfig
from configs.model_config import ModelConfig
import logging, traceback
logger = logging.getLogger(__name__)


class OpenAILLM(BaseLLM):
    def __init__(self, model_config: ModelConfig):
        self.client = OpenAI(api_key=model_config.api_key, base_url=model_config.base_url)
        self.model_path = model_config.model_path

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate(self, system_prompt: Optional[str], prompt: str, generation_config: GenerationConfig, response_format: Optional[str] = None) -> str:
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
                    
        try:
            response = self.client.chat.completions.create(
                model=self.model_path,
                messages=messages,
                temperature=generation_config.temperature,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_format.__name__,
                        "schema": response_format.model_json_schema()
                    }
                } if response_format else None,
            )
            logger.info(response.choices[0].message.content)
            if response_format:
                return response_format.model_validate_json(response.choices[0].message.content)
            else:
                return response.choices[0].message.content
        except Exception as exc:
            # Log full traceback then re-raise so tenacity can retry
            logger.error("OpenAI generate failed:\n%s", traceback.format_exc())
            raise

            
    def batch_generate(self,
                    prompts: List[str],
                    generation_config: GenerationConfig,
                    system_prompt: Optional[str], 
                    max_workers: int = 8,
                    response_format: Optional[str] = None
                    ) -> List[str]:
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.generate, system_prompt, prompt, generation_config, response_format
                ): i
                for i, prompt in enumerate(prompts)
            }
            results = [None] * len(prompts)
            for future in tqdm(as_completed(futures), total=len(prompts), desc="Processing prompts"):
                idx = futures[future]
                try:
                    logger.info(f"Processing prompt {idx}")
                    result = future.result()
                    
                    results[idx] = result
                    logger.info(f"result {result}")
                except Exception as e:
                    logger.error(
                        "[ERROR] openai call failed for prompt %s. Traceback:\n%s",
                        idx,
                        traceback.format_exc(),
                    )
                    results[idx] = None

        return results
    
    
    @property
    def type(self) -> str:
        return "openai"
