import argparse
import json
from typing import List
from configs.model_config import ModelConfig, ModelType
from configs.generation_config import GenerationConfig
from src.models import ModelFactory
from src.strategies import StrategyFactory
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser(description="Run ruCodeReviewer benchmark from the command-line")

    # Benchmark model
    parser.add_argument("--model-type", required=True, choices=[m.value for m in ModelType])
    parser.add_argument("--model-path", required=True, help="Model name/id or local path")
    parser.add_argument("--api-key", default=None, help="API key for OpenAI models")
    parser.add_argument("--base-url", default=None, help="Base URL for OpenAI-compatible endpoint")

    # Judge model (optional, defaults to same as benchmark)
    parser.add_argument("--judge-model-type", choices=[m.value for m in ModelType])
    parser.add_argument("--judge-model-path")
    parser.add_argument("--judge-api-key")
    parser.add_argument("--judge-base-url")

    # Generation params
    parser.add_argument("--max-new", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.95)

    # Metrics & passes
    parser.add_argument("--metrics", default="exact_match", help="Comma-separated list of metrics")
    parser.add_argument("--passes", default="1,5,10", help="Comma-separated judge@k values")

    # Output paths
    parser.add_argument("--out-json", default="results.json", help="File to save aggregated metrics JSON")
    parser.add_argument("--out-jsonl", default=None, help="If given, per-sample results are saved here")

    return parser.parse_args()


def build_model_config(args, prefix: str = "") -> ModelConfig:
    t = getattr(args, f"{prefix}model_type", None) or args.model_type
    path = getattr(args, f"{prefix}model_path", None) or args.model_path
    api_key = getattr(args, f"{prefix}api_key", None) or args.api_key
    base_url = getattr(args, f"{prefix}base_url", None) or args.base_url
    return ModelConfig(
        model_type=ModelType(t),
        model_path=path,
        api_key=api_key,
        base_url=base_url,
    )


def main():
    args = parse_args()

    benchmark_cfg = build_model_config(args)
    judge_cfg = build_model_config(args, prefix="judge_") if args.judge_model_path or args.judge_model_type else benchmark_cfg

    gen_cfg = GenerationConfig(max_new_tokens=args.max_new, temperature=args.temperature, top_p=args.top_p)
    metrics = [m.strip() for m in args.metrics.split(",") if m.strip()]
    passes = [int(p) for p in args.passes.split(",") if p]

    model_factory = ModelFactory()
    strategy_factory = StrategyFactory()

    benchmark_model = model_factory.get_model(benchmark_cfg)
    judge_model = model_factory.get_model(judge_cfg)
    strategy = strategy_factory.get_strategy("default", benchmark_model, judge_model, metrics)

    # simple tqdm progress
    pbar = tqdm(total=100, desc="Benchmark", unit="%")

    def progress_cb(frac: float, msg: str):
        pbar.n = int(frac * 100)
        pbar.set_description(f"{msg}")
        pbar.refresh()

    results = strategy.evaluate(gen_cfg, passes=passes, progress_callback=progress_cb)
    pbar.close()

    # Save aggregated metrics
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump({k: {
            "mean": v[1].to_dict() if v else None,
            "std": v[2].to_dict() if v else None,
        } for k, v in results.items()}, f, ensure_ascii=False, indent=2)

    # Optionally save per-sample JSONL
    if args.out_jsonl:
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
            # add taxonomy
            combined["comment_language"] = strategy.comment_language
            combined["language"] = strategy.programming_language
            combined["topic"] = strategy.topic
            combined.to_json(args.out_jsonl, orient="records", lines=True, force_ascii=False)

    print(f"Saved aggregated metrics to {args.out_json}")
    if args.out_jsonl:
        print(f"Saved per-sample metrics to {args.out_jsonl}")


if __name__ == "__main__":
    main() 