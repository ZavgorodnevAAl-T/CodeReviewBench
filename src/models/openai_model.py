import httpx
import json
import re
import logging
import traceback
import threading
from collections import defaultdict
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
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)
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
        # Token stats: tag -> {prompt, completion, count}
        self._token_stats: dict = defaultdict(lambda: {"prompt": 0, "completion": 0, "count": 0})
        self._stats_lock = threading.Lock()

    def _record_usage(self, tag: str, usage: dict):
        if not usage:
            return
        with self._stats_lock:
            s = self._token_stats[tag]
            s["prompt"] += usage.get("prompt_tokens", 0)
            s["completion"] += usage.get("completion_tokens", 0)
            s["count"] += 1

    def token_stats(self) -> dict:
        """Return average tokens per request, grouped by tag."""
        result = {}
        with self._stats_lock:
            for tag, s in self._token_stats.items():
                n = s["count"] or 1
                result[tag] = {
                    "avg_prompt_tokens": round(s["prompt"] / n, 1),
                    "avg_completion_tokens": round(s["completion"] / n, 1),
                    "total_requests": s["count"],
                }
        return result

    def _apply_no_reasoning(self, payload: dict):
        """Add model-specific parameter to suppress/minimize reasoning."""
        model = self.model_path.lower()
        if "glm" in model:
            # Z-AI / GLM style
            payload["reasoning"] = {"effort": "none"}
        elif any(m in model for m in ("o1", "o3", "o4", "o-mini")):
            # OpenAI o-series (o1, o3, o4-mini, etc.)
            payload["reasoning_effort"] = "low"
        elif "claude" in model:
            # Anthropic Claude (via OpenRouter or compatible proxy)
            payload["thinking"] = {"type": "disabled"}
        # Regular GPT / unknown models — no reasoning param, nothing to disable

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=30))
    def generate(self, system_prompt: Optional[str], prompt: str, generation_config: GenerationConfig,
                 response_format=None, tag: str = "unknown") -> str:
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
        if generation_config.no_reasoning:
            self._apply_no_reasoning(payload)
        if response_format:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = self._http.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            usage = dict(data.get("usage") or {})
            content = data["choices"][0]["message"]["content"]

            if content is None:
                # Model doesn't support response_format — retry without it
                payload.pop("response_format", None)
                resp = self._http.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                # Merge usage from both requests into one record
                for k, v in (data.get("usage") or {}).items():
                    usage[k] = usage.get(k, 0) + v
                content = data["choices"][0]["message"]["content"]

            self._record_usage(tag, usage)

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
                       response_format=None, tag: str = "unknown") -> List[str]:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.generate, system_prompt, prompt, generation_config, response_format, tag): i
                for i, prompt in enumerate(prompts)
            }
            results = [None] * len(prompts)
            for future in tqdm(as_completed(futures), total=len(prompts), desc=f"Generating [{tag}]"):
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
