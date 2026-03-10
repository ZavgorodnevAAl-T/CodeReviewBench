import httpx
import json
import re
import logging
import traceback
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm
from configs.generation_config import GenerationConfig
from configs.model_config import ModelConfig
from .base_model import BaseLLM

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> str:
    """Extract first JSON object from text (handles markdown code blocks)."""
    # Strip ```json ... ``` fences
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)
    # Find first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    raise ValueError(f"No JSON object found in response: {text[:200]}")


class OpenAILLM(BaseLLM):
    def __init__(self, model_config: ModelConfig):
        self.api_key = model_config.api_key
        base = model_config.base_url.rstrip("/")
        self.base_url = base if base.endswith("/v1") else f"{base}/v1"
        self.model_path = model_config.model_path
        self._http = httpx.Client(verify=False, timeout=120)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=30))
    def generate(self, system_prompt: Optional[str], prompt: str, generation_config: GenerationConfig, response_format=None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_path,
            "messages": messages,
            "temperature": generation_config.temperature,
            "max_tokens": generation_config.max_new_tokens,
            "top_p": generation_config.top_p,
        }
        if response_format:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = self._http.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]

            if content is None:
                # Model doesn't support response_format — retry without it
                payload.pop("response_format", None)
                resp = self._http.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=payload,
                )
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"]["content"]

            if content is None:
                raise ValueError("Model returned null content")

            logger.info(content)

            if response_format:
                try:
                    return response_format.model_validate_json(content)
                except Exception:
                    return response_format.model_validate_json(_extract_json(content))

            return content
        except Exception:
            logger.error("generate failed:\n%s", traceback.format_exc())
            raise

    def batch_generate(self, prompts: List[str], generation_config: GenerationConfig,
                       system_prompt: Optional[str], max_workers: int = 8,
                       response_format=None) -> List[str]:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.generate, system_prompt, prompt, generation_config, response_format): i
                for i, prompt in enumerate(prompts)
            }
            results = [None] * len(prompts)
            for future in tqdm(as_completed(futures), total=len(prompts), desc="Generating"):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception:
                    logger.error("prompt %d failed:\n%s", idx, traceback.format_exc())
                    results[idx] = None
        return results

    @property
    def type(self) -> str:
        return "openai"
