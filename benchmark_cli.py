import argparse
import json
import os
import re
from typing import List
from dotenv import load_dotenv
from configs.model_config import ModelConfig, ModelType
from configs.generation_config import GenerationConfig
from src.models import ModelFactory
from src.strategies import StrategyFactory

load_dotenv()


def parse_args():
    parser = argparse.ArgumentParser(description="Run CodeReviewer benchmark from the command-line")

    # Benchmark model
    parser.add_argument("--model-type", default="openai", choices=[m.value for m in ModelType])
    parser.add_argument("--model-path", default=os.getenv("LLM_MODEL"), help="Model name/id (default: $LLM_MODEL)")
    parser.add_argument("--api-key", default=os.getenv("LLM_API_KEY"), help="API key (default: $LLM_API_KEY)")
    parser.add_argument("--base-url", default=os.getenv("LLM_BASE_URL"), help="Base URL (default: $LLM_BASE_URL)")

    # Judge model
    parser.add_argument("--judge-model-type", default="openai", choices=[m.value for m in ModelType])
    parser.add_argument("--judge-model-path", default=os.getenv("JUDGE_LLM_MODEL"), help="Judge model (default: $JUDGE_LLM_MODEL)")
    parser.add_argument("--judge-api-key", default=os.getenv("LLM_API_KEY"), help="Judge API key (default: $LLM_API_KEY)")
    parser.add_argument("--judge-base-url", default=os.getenv("LLM_BASE_URL"), help="Judge base URL (default: $LLM_BASE_URL)")

    # Generation params
    parser.add_argument("--max-new", type=int, default=2048)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=0.95)

    # Metrics & passes
    parser.add_argument("--metrics", default="exact_match", help="Comma-separated list of metrics")
    parser.add_argument("--passes", default="1,5,10", help="Comma-separated judge@k values")

    # Data
    parser.add_argument("--data-path", default=None, help="Path to dataset JSONL (default: data/codereview_data.jsonl)")
    parser.add_argument("--workers", type=int, default=8, help="Parallel requests to LLM API (default: 8)")

    # Output paths
    parser.add_argument("--out-dir", default="results", help="Directory to save output files")
    parser.add_argument("--out-json", default=None, help="Override output JSON path (default: <out-dir>/<model>.json)")
    parser.add_argument("--out-jsonl", default=None, help="Override output JSONL path (default: <out-dir>/<model>_samples.jsonl)")

    return parser.parse_args()


def build_model_config(args, prefix: str = "") -> ModelConfig:
    t = getattr(args, f"{prefix}model_type", None) or args.model_type
    path = getattr(args, f"{prefix}model_path", None) or args.model_path
    api_key = getattr(args, f"{prefix}api_key", None) or args.api_key
    base_url = getattr(args, f"{prefix}base_url", None) or args.base_url
    if not path:
        raise ValueError(f"Model path not set. Pass --{'judge-' if prefix else ''}model-path or set ${'JUDGE_' if prefix else ''}LLM_MODEL")
    return ModelConfig(
        model_type=ModelType(t),
        model_path=path,
        api_key=api_key,
        base_url=base_url,
    )


def main():
    args = parse_args()

    benchmark_cfg = build_model_config(args)
    judge_cfg = build_model_config(args, prefix="judge_")

    gen_cfg = GenerationConfig(max_new_tokens=args.max_new, temperature=args.temperature, top_p=args.top_p)
    metrics = [m.strip() for m in args.metrics.split(",") if m.strip()]
    passes = [int(p) for p in args.passes.split(",") if p]

    model_factory = ModelFactory()
    strategy_factory = StrategyFactory()

    benchmark_model = model_factory.get_model(benchmark_cfg)
    judge_model = model_factory.get_model(judge_cfg)
    strategy = strategy_factory.get_strategy("default", benchmark_model, judge_model, metrics, args.data_path)

    # Derive output paths from model name
    model_slug = re.sub(r"[^a-zA-Z0-9_.-]", "_", args.model_path)
    os.makedirs(args.out_dir, exist_ok=True)
    out_json = args.out_json or os.path.join(args.out_dir, f"{model_slug}.json")
    out_jsonl = args.out_jsonl or os.path.join(args.out_dir, f"{model_slug}_samples.jsonl")

    results = strategy.evaluate(gen_cfg, passes=passes, max_workers=args.workers)

    # Save aggregated metrics
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({k: {
            "mean": v[1].to_dict() if v else None,
            "std": v[2].to_dict() if v else None,
        } for k, v in results.items()}, f, ensure_ascii=False, indent=2)

    # Save per-sample JSONL
    import pandas as pd
    rows = []
    for metric_name, v in results.items():
        if v is None:
            continue
        df = v[0]
        df_prefixed = df.add_prefix(f"{metric_name}__")
        rows.append(df_prefixed)
    if rows:
        combined = pd.concat(rows, axis=1)
        combined["comment_language"] = strategy.comment_language
        combined["language"] = strategy.programming_language
        combined["topic"] = strategy.topic
        combined.to_json(out_jsonl, orient="records", lines=True, force_ascii=False)

    print(f"Saved aggregated metrics to {out_json}")
    print(f"Saved per-sample metrics to {out_jsonl}")


if __name__ == "__main__":
    main() 