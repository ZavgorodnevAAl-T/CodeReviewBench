import streamlit as st
from typing import List

from configs.model_config import ModelConfig, ModelType
from configs.generation_config import GenerationConfig
from src.models import ModelFactory
from src.strategies import StrategyFactory
from styles import get_common_styles

st.set_page_config(page_title="CodeReviewBench • Configuration", page_icon="⚙️", layout="wide")

# --------------------------------------------------
# Apply common styles
# --------------------------------------------------
st.markdown(get_common_styles(), unsafe_allow_html=True)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <div class="main-title">Benchmark Configuration</div>
        <div class="main-subtitle">Configure models, parameters, and metrics for evaluation</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Helper functions
# --------------------------------------------------
def build_model_config(prefix: str, title: str) -> ModelConfig:
    """Build model configuration in a compact format without extra HTML wrappers."""
    
    # Model type selection
    model_type_str = st.selectbox(
        "Type", 
        options=[m.value for m in ModelType], 
        key=f"{prefix}_model_type",
        label_visibility="collapsed"
    )
    
    # Model path
    default_path = "google/gemini-2.5-flash"
    model_path = st.text_input(
        "Model", 
        value=default_path,
        key=f"{prefix}_model_path",
        label_visibility="collapsed"
    )
    
    # Conditional parameters
    api_key = st.text_input(
        "API Key",
        type="password",
        key=f"{prefix}_api_key",
        label_visibility="collapsed"
    )
    base_url = st.text_input(
        "Base URL",
        value="https://openrouter.ai/api/v1",
        key=f"{prefix}_base_url",
        label_visibility="collapsed"
    )
    
    return ModelConfig(
        model_type=ModelType(model_type_str),
        api_key=api_key,
        base_url=base_url,
        model_path=model_path,
    )

# --------------------------------------------------
# Model Configuration – side-by-side columns (avoids crooked layout)
# --------------------------------------------------
col_bench, col_judge = st.columns(2, gap="large")

with col_bench:
    st.markdown("<div class='panel-title'>Benchmark Model</div>", unsafe_allow_html=True)
    benchmark_model_config = build_model_config("benchmark", "Benchmark Model")

with col_judge:
    st.markdown("<div class='panel-title'>Judge Model</div>", unsafe_allow_html=True)
    judge_model_config = build_model_config("judge", "Judge Model")

# --------------------------------------------------
# Generation Parameters
# --------------------------------------------------
st.markdown(
    """
    <div class="panel-title">Generation Parameters</div>
    <div class="generation-grid">
    """,
    unsafe_allow_html=True,
)

# --- New layout for better alignment and style ---
col1, col2, col3 = st.columns([1.1, 0.9, 0.9], gap="medium")

with col1:
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=16,
        max_value=4096,
        value=4096,
        step=64,
        label_visibility="visible"
    )

with col2:
    temperature = st.number_input(
        "Temperature",
        min_value=0.0,
        max_value=2.1,
        value=1.0,
        step=0.1,
        label_visibility="visible"
    )

with col3:
    top_p = st.number_input(
        "Top-p",
        min_value=0.0,
        max_value=1.0,
        value=0.95,
        step=0.05,
        label_visibility="visible"
    )

generation_config = GenerationConfig(
    max_new_tokens=max_tokens,
    temperature=temperature,
    top_p=top_p
)

# --------------------------------------------------
# Metrics Selection
# --------------------------------------------------
st.markdown(
    """
        <div class="panel-title">Evaluation Metrics</div>
        <div class="metrics-grid">
    """,
    unsafe_allow_html=True,
)

metrics_options = [
    "exact_match",
    "bleu", 
    "chrf",
    "llm_exact_match",
    "multi_metric"
]

selected_metrics = st.multiselect(
    "Select metrics",
    options=metrics_options,
    default=["exact_match"],
    label_visibility="collapsed"
)

st.markdown('</div></div>', unsafe_allow_html=True)

# --------------------------------------------------
# Run Section
# --------------------------------------------------
st.markdown(
    """
    <div class="run-panel">
        <div class="run-title">Ready to Run</div>
        <div class="main-subtitle">
            Start your benchmark evaluation with this configuration<br>
            Review settings below before launching
        </div>
        <div style="display: flex; justify-content: center; width: 100%;">
    """, unsafe_allow_html=True
)
# Центрируем кнопку с помощью columns Streamlit и параметра use_container_width=True
center_col1, center_col2, center_col3 = st.columns([2,1,2])
with center_col2:
    run_button = st.button(
        "Start Benchmark",
        key="real_bench_btn",
        type="primary",
        help="Run the benchmark",
        use_container_width=True,
    )
st.markdown("</div></div>", unsafe_allow_html=True)

# --------------------------------------------------
# Benchmark Execution
# --------------------------------------------------
if run_button:
    if not selected_metrics:
        st.markdown(
            """
            <div class="alert alert-warning">
                <strong>No metrics selected</strong><br>
                Please select at least one evaluation metric.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    model_factory = ModelFactory()
    strategy_factory = StrategyFactory()

    with st.status("Loading models", expanded=False):
        benchmark_model = model_factory.get_model(benchmark_model_config)
        judge_model = model_factory.get_model(judge_model_config)
        strategy = strategy_factory.get_strategy(
            "default", benchmark_model, judge_model, selected_metrics
        )

    st.markdown(
        """
        <div class="alert alert-info">
            <strong>Benchmark running</strong><br>
            This may take several minutes depending on your configuration.
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    progress_bar = st.progress(0.0, text="Initializing...")

    def _ui_progress_callback(progress: float, message: str):
        progress_bar.progress(min(max(progress, 0.0), 1.0), text=message)

    try:
        results = strategy.evaluate(
            generation_config=generation_config, 
            progress_callback=_ui_progress_callback
        )
    except Exception as exc:
        st.markdown(
            f"""
            <div class="alert alert-warning">
                <strong>Benchmark failed</strong><br>
                {str(exc)}
            </div>
            """,
            unsafe_allow_html=True,
        )
        raise

    progress_bar.progress(1.0, text="Complete")

    # Store results
    st.session_state["last_benchmark_results"] = results
    st.session_state["last_predictions"] = getattr(strategy, "latest_predictions", None)
    st.session_state["prompts"] = strategy.prompts
    st.session_state["references"] = strategy.outputs
    st.session_state["comment_language"] = getattr(strategy, "comment_language", [])
    st.session_state["programming_language"] = getattr(strategy, "programming_language", [])
    st.session_state["topic"] = getattr(strategy, "topic", [])

    st.markdown(
        """
        <div class="alert alert-success">
            <strong>Benchmark completed</strong><br>
            Results are available in the Observation and Examples pages.
        </div>
        """,
        unsafe_allow_html=True,
    ) 