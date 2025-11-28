def get_common_styles():
    """Returns the common CSS styles as a string."""
    return """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #e2e8f0;
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        color: #64748b;
        margin: 0;
    }
    
    .config-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .config-panel {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
        height: fit-content;
    }
    
    .panel-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .compact-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .compact-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        color: #4a5568;
        min-width: 80px;
        flex-shrink: 0;
    }
    
    .compact-control {
        flex: 1;
    }
    
    .metrics-panel {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 0.75rem;
        margin-top: 1rem;
    }
    
    .metric-checkbox {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        transition: all 0.2s ease;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #4a5568;
    }
    
    .metric-checkbox:hover {
        border-color: #cbd5e0;
        background: #f7fafc;
    }
    
    .metric-checkbox.selected {
        border-color: #4a5568;
        background: #f7fafc;
    }
    
    .generation-panel {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .generation-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin-top: 1rem;
    }
    
    .param-group {
        text-align: center;
    }
    
    .param-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 500;
        color: #4a5568;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .param-value {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .param-slider {
        width: 100%;
    }
    
    .run-panel {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        color: #2d3748;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .run-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #222222;
        letter-spacing: -0.01em;
        margin-bottom: 0.5rem;
    }

    .run-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #4a5568;
        opacity: 1;
        margin-bottom: 1.5rem;
    }
    
    .stButton > button {
        background: white !important;
        color: #2d3748 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.75rem 2rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: #f7fafc !important;
        transform: translateY(-1px) !important;
    }
    
    .alert {
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
    }
    
    .alert-info {
        background: #ebf8ff;
        border: 1px solid #bee3f8;
        color: #2c5282;
    }
    
    .alert-warning {
        background: #fffbeb;
        border: 1px solid #fed7aa;
        color: #c05621;
    }
    
    .alert-success {
        background: #f0fff4;
        border: 1px solid #9ae6b4;
        color: #22543d;
    }
    
    /* Streamlit component overrides */
    .stSelectbox > div > div {
        border-radius: 6px !important;
        font-size: 0.9rem !important;
    }
    
    .stTextInput > div > div {
        border-radius: 6px !important;
        font-size: 0.9rem !important;
    }
    
    .stNumberInput > div > div {
        border-radius: 6px !important;
        font-size: 0.9rem !important;
    }
    
    .stSlider > div > div > div {
        height: 4px !important;
    }
    
    .stSlider > div > div > div > div {
        height: 16px !important;
        width: 16px !important;
    }
    
    .stDataFrame {
        border-radius: 8px !important;
    }
    </style>
    """

