"""
Custom CSS styles and modern glassmorphism design system for Streamlit.
"""

def get_custom_css() -> str:
    """Returns CSS rules for a sleek modern data analytics interface."""
    return """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Typography & Background */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Top App Header Hero */
    .hero-container {
        padding: 1.6rem 2rem;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        background: linear-gradient(90deg, #6366F1 0%, #A855F7 100%);
        color: #FFFFFF;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #FFFFFF 30%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }

    .hero-subtitle {
        color: #94A3B8;
        font-size: 0.98rem;
        margin-top: 0.4rem;
        line-height: 1.5;
    }

    /* Metric Cards Grid */
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        transition: all 0.25s ease;
        backdrop-filter: blur(8px);
    }

    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 8px 24px -6px rgba(99, 102, 241, 0.25);
    }

    .metric-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0.25rem 0 0.15rem 0;
    }

    .metric-sub {
        font-size: 0.75rem;
        color: #64748B;
    }

    /* Health Score Pill */
    .health-pill {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 700;
        margin-left: 6px;
    }

    /* Healing Badge */
    .healed-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .healed-badge.warning {
        background: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border-color: rgba(245, 158, 11, 0.35);
    }

    /* Prompt Suggestion Buttons */
    .suggestion-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 0.75rem 0 1.5rem 0;
    }

    .suggestion-chip {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #E2E8F0;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .suggestion-chip:hover {
        background: rgba(99, 102, 241, 0.2);
        border-color: #818CF8;
        color: #FFFFFF;
        transform: translateY(-1px);
    }

    /* Clean Streamlit elements */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
    }

    /* Code block drawer */
    .code-telemetry {
        font-size: 0.75rem;
        color: #94A3B8;
        display: flex;
        gap: 14px;
        margin-top: 6px;
    }
    </style>
    """
