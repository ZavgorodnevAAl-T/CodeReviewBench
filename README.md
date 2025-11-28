# CodeReviewBench

A lightweight, extensible benchmark suite for evaluating LLM-powered code reviewers. CodeReviewBench provides a comprehensive framework to assess how well language models perform on code review tasks, with support for multiple evaluation metrics, flexible model backends, and interactive visualization tools.

## Features

- **Configurable Workflows**: Quickly tailor datasets, models, and metrics to your needs
- **Insightful Analytics**: Interactive dashboards to explore aggregate and per-sample results
- **Plugin Architecture**: Add new LLM backends, tasks, or evaluation strategies in a few lines of code
- **Ready-to-Run**: Ships with curated sample dataset and sensible defaults – start benchmarking in seconds
- **Multiple Interfaces**: Web UI (Streamlit), CLI, and REST API (FastAPI)

## Installation

### Setup

1. Clone the repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install as a package:
```bash
pip install -e .
```

## Quick Start

### Web Interface (Streamlit)

Launch the interactive web interface:

```bash
streamlit run Welcome.py
```

Navigate through the pages:
- **Welcome**: Overview and features
- **Configuration**: Set up models, metrics, and generation parameters
- **Observation**: View aggregated results and statistics
- **Examples**: Explore per-sample predictions and references

### Command Line Interface

Run a benchmark from the command line:

```bash
python benchmark_cli.py \
  --model-type openai \
  --model-path anthropic/claude-3.7-sonnet \
  --base-url https://openrouter.ai/api/v1 \
  --api-key $OPENROUTER_API_KEY \
  --judge-model-type openai \
  --judge-model-path qwen/qwen-2.5-coder-32b-instruct \
  --judge-base-url https://openrouter.ai/api/v1 \
  --judge-api-key $OPENROUTER_API_KEY \
  --metrics "llm_exact_match,bleu,multi_metric,chrf" \
  --passes "1,5,10" \
  --out-json results.json \
  --out-jsonl samples.jsonl
```

### REST API

Start the FastAPI server:

```bash
python api.py
```

The API will be available at `http://0.0.0.0:8000`. Use the interactive docs at `http://0.0.0.0:8000/docs`.

**Endpoints:**
- `POST /init_benchmark`: Initialize a benchmark configuration
- `POST /run_benchmark`: Run evaluation with the specified configuration

## Configuration

### Model Configuration

The benchmark supports OpenAI-compatible APIs. Configure models using:

- **Model Type**: `openai` (OpenAI-compatible API)
- **Model Path**: Model identifier (e.g., `anthropic/claude-3.7-sonnet`)
- **API Key**: Your API key
- **Base URL**: API endpoint (e.g., `https://openrouter.ai/api/v1`)

### Evaluation Metrics

Available metrics:

- **exact_match**: Exact string matching between predictions and references
- **bleu**: BLEU score for text similarity
- **chrf**: Character-level F-score (ChrF)
- **llm_exact_match**: LLM-based exact match using a judge model
- **multi_metric**: Multi-faceted evaluation using a judge model

### Generation Parameters

- **Max Tokens**: Maximum number of tokens to generate (default: 4096)
- **Temperature**: Sampling temperature (default: 1.0)
- **Top-p**: Nucleus sampling parameter (default: 0.95)

### Judge@K

The benchmark supports evaluation at multiple judge levels (e.g., 1, 5, 10), allowing you to assess performance when considering the top-K predictions.

## Project Structure

```
CodeReviewBench/
├── src/
│   ├── models/           # LLM model backends
│   │   ├── base_model.py
│   │   └── openai_model.py
│   ├── metrics/          # Evaluation metrics
│   │   ├── exact_match.py
│   │   ├── bleu.py
│   │   ├── ChrF.py
│   │   ├── llm_based_exact_match.py
│   │   └── multi_metric.py
│   ├── strategies/      # Evaluation strategies
│   │   ├── base_strategy.py
│   │   └── default_strategy.py
│   ├── judge/           # Judge models for LLM-based metrics
│   ├── prompts/         # Prompt templates
│   └── utils/           # Utility functions
├── configs/             # Configuration classes
├── pages/               # Streamlit pages
├── data/                # Benchmark datasets
├── benchmark_cli.py     # CLI interface
├── api.py               # FastAPI REST interface
└── Welcome.py           # Streamlit main page
```

## Extending the Framework

### Adding a New Model Backend

1. Create a new model class inheriting from `BaseLLM` in `src/models/`
2. Implement required methods: `generate()`, `batch_generate()`, and `type` property
3. Register the model in `src/models/__init__.py`

### Adding a New Metric

1. Create a new metric class inheriting from `BaseMetric` in `src/metrics/`
2. Implement the `calculate()` method
3. Register the metric in `src/metrics/compute_metrics.py`

### Adding a New Evaluation Strategy

1. Create a new strategy class inheriting from `EvaluationStrategy` in `src/strategies/`
2. Implement the `evaluate()` method
3. Register the strategy in `src/strategies/__init__.py`

## Data Format

The benchmark expects data in JSONL format with the following structure:

```json
{
  "instruction": "You are a code reviewer...",
  "inputs": {
    "diff_block": "code diff here"
  },
  "outputs": "expected review comments",
  "comment_language": "en",
  "language": "python",
  "topic": "bug-fix"
}
```

## Output Format

### Aggregated Results (JSON)

```json
{
  "metric_name": {
    "mean": {...},
    "std": {...}
  }
}
```

### Per-Sample Results (JSONL)

Each line contains per-sample metrics with prefixes, plus taxonomy fields:
- `metric_name__judge_1`, `metric_name__judge_5`, etc.
- `comment_language`, `language`, `topic`

## License

MIT