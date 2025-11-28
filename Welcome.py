import streamlit as st

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="CodeReviewBench",
    page_icon="📊",
    layout="wide",
)

# --------------------------------------------------
# Custom CSS for gradient header & styling
# --------------------------------------------------
st.markdown(
    """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    .gradient-text {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 3.5rem;
        background: linear-gradient(90deg, #ff512f 0%, #dd2476 50%, #06beb6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25em;
        text-align: center;
    }

    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    .feature-box {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 2px solid #e2e8f0;
        border-radius: 1rem;
        padding: 2rem 1.5rem;
        height: 100%;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .feature-description {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: #475569;
        line-height: 1.5;
    }
    
    .leaderboard-link {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 1rem 2rem;
        border-radius: 0.75rem;
        text-decoration: none;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        display: inline-block;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .leaderboard-section {
        text-align: center;
        margin: 3rem 0;
        padding: 2rem;
        background: linear-gradient(135deg, #fef7ff 0%, #f3e8ff 100%);
        border-radius: 1.5rem;
        border: 2px solid #e9d5ff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .leaderboard-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #581c87;
        margin-bottom: 1rem;
    }
    
    .leaderboard-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #7c3aed;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .hero-section {
        text-align: center;
        margin: 2rem 0 3rem 0;
        padding: 2rem;
    }
    
    .features-header {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        text-align: center;
        margin: 2rem 0 1.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Hero section
# --------------------------------------------------
st.markdown(
    """
    <div class="hero-section">
        <h1 class="gradient-text">CodeReviewBench</h1>
        <p class="subtitle">A lightweight, extensible benchmark suite for evaluating LLM-powered code reviewers</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Features header
# --------------------------------------------------

# --------------------------------------------------
# Key features grid - 4 squares in a row
# --------------------------------------------------
features = [
    ("⚙️", "Configurable Workflows", "Quickly tailor datasets, models and metrics to your needs."),
    ("📈", "Insightful Analytics", "Interactive dashboards to explore aggregate and per-sample results."),
    ("🧩", "Plugin Architecture", "Add new LLM back-ends, tasks or evaluation strategies in a few lines of code."),
    ("🚀", "Ready-to-Run", "Ships with curated sample dataset and sensible defaults – start benchmarking in seconds."),
]

cols = st.columns(4)
for idx, (icon, title, description) in enumerate(features):
    with cols[idx]:
        # Используем min-height для выравнивания высоты по всем карточкам
        st.markdown(
            f"""
            <div class='feature-box' style="min-height: 300px; display: flex; flex-direction: column; justify-content: center;">
                <span class='feature-icon'>{icon}</span>
                <div class='feature-title'>{title}</div>
                <div class='feature-description'>{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --------------------------------------------------
# Run Benchmark button
# --------------------------------------------------


st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Run Benchmark", key="run_bench_btn", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Configuration.py")