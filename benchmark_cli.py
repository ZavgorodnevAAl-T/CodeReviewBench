import argparse
import json
import os
import re
import pandas as pd
from dotenv import load_dotenv
from configs.model_config import ModelConfig, ModelType
from configs.generation_config import GenerationConfig
from src.models import ModelFactory
from src.strategies import StrategyFactory

load_dotenv()


def slugify(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", name)


def parse_args():
    parser = argparse.ArgumentParser(description="Run CodeReviewer benchmark from the command-line")

    # Benchmark model
    parser.add_argument("--model-type", default="openai", choices=[m.value for m in ModelType])
    parser.add_argument("--model-path", default=os.getenv("LLM_MODEL"), help="Model name/id (default: $LLM_MODEL)")
    parser.add_argument("--api-key", default=os.getenv("LLM_API_KEY"), help="API key (default: $LLM_API_KEY)")
    parser.add_argument("--base-url", default=os.getenv("LLM_BASE_URL"), help="Base URL (default: $LLM_BASE_URL)")

    # Judge models (comma or newline separated)
    parser.add_argument(
        "--judge-model-path",
        default=os.getenv("JUDGE_LLM_MODELS", os.getenv("JUDGE_LLM_MODEL")),
        help="Judge model(s), comma-separated (default: $JUDGE_LLM_MODELS)",
    )
    parser.add_argument("--judge-api-key", default=os.getenv("LLM_API_KEY"))
    parser.add_argument("--judge-base-url", default=os.getenv("LLM_BASE_URL"))

    # Generation params
    parser.add_argument("--max-new", type=int, default=2048)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=0.95)

    # Metrics & passes
    parser.add_argument("--metrics", default="llm_exact_match,multi_metric")
    parser.add_argument("--passes", default="1,5,10")

    # Data & parallelism
    parser.add_argument("--data-path", default=None)
    parser.add_argument("--workers", type=int, default=8)

    # Output
    parser.add_argument("--out-dir", default="results")

    return parser.parse_args()


def build_model_config(args, model_path: str, prefix: str = "") -> ModelConfig:
    api_key = getattr(args, f"{prefix}api_key", None) or args.api_key
    base_url = getattr(args, f"{prefix}base_url", None) or args.base_url
    model_type = getattr(args, f"{prefix}model_type", None) or args.model_type
    return ModelConfig(
        model_type=ModelType(model_type),
        model_path=model_path,
        api_key=api_key,
        base_url=base_url,
    )


def save_results(results, strategy, out_json: str, out_jsonl: str):
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(
            {k: {"mean": v[1].to_dict(), "std": v[2].to_dict()} for k, v in results.items() if v is not None},
            f, ensure_ascii=False, indent=2,
        )

    rows = []
    for metric_name, v in results.items():
        if v is None:
            continue
        rows.append(v[0].add_prefix(f"{metric_name}__"))
    if rows:
        combined = pd.concat(rows, axis=1)
        combined["language"] = strategy.programming_language
        combined["topic"] = strategy.topic
        combined.to_json(out_jsonl, orient="records", lines=True, force_ascii=False)

    print(f"  → {out_json}")
    print(f"  → {out_jsonl}")


def main():
    args = parse_args()

    if not args.model_path:
        raise ValueError("Model path not set. Pass --model-path or set $LLM_MODEL")

    # Parse judge models — JSON array or comma/newline separated
    raw_judges = args.judge_model_path or ""
    raw_judges = raw_judges.strip()
    if raw_judges.startswith("["):
        judge_paths = json.loads(raw_judges)
    else:
        judge_paths = [j.strip() for j in re.split(r"[,\n]", raw_judges) if j.strip()]
    if not judge_paths:
        raise ValueError("No judge models set. Pass --judge-model-path or set $JUDGE_LLM_MODELS")

    gen_cfg = GenerationConfig(max_new_tokens=args.max_new, temperature=args.temperature, top_p=args.top_p)
    metrics = [m.strip() for m in args.metrics.split(",") if m.strip()]
    passes = [int(p) for p in args.passes.split(",") if p]

    model_factory = ModelFactory()
    strategy_factory = StrategyFactory()

    benchmark_cfg = build_model_config(args, args.model_path)
    benchmark_model = model_factory.get_model(benchmark_cfg)
    strategy = strategy_factory.get_strategy("default", benchmark_model, metrics, args.data_path)

    model_slug = slugify(args.model_path)
    os.makedirs(args.out_dir, exist_ok=True)

    # Cache path for generations — reused across judges
    cache_path = os.path.join(args.out_dir, f"{model_slug}_generations.jsonl")

    # Generate once (or load from cache)
    predictions = strategy.generate(gen_cfg, passes=passes, max_workers=args.workers, cache_path=cache_path)

    # Evaluate with each judge
    for judge_path in judge_paths:
        judge_slug = slugify(judge_path)
        print(f"\nEvaluating with judge: {judge_path}")

        judge_cfg = build_model_config(args, judge_path, prefix="judge_")
        judge_model = model_factory.get_model(judge_cfg)

        results = strategy.evaluate(predictions, judge_model, passes=passes)

        prefix = f"{model_slug}__judge_{judge_slug}"
        out_json  = os.path.join(args.out_dir, f"{prefix}.json")
        out_jsonl = os.path.join(args.out_dir, f"{prefix}_samples.jsonl")
        save_results(results, strategy, out_json, out_jsonl)

    print("\nDone.")


if __name__ == "__main__":
    main()
