"""
Conversational Data Analysis Assistant — Streamlit Application
A complete LLM-powered natural-language data intelligence platform.
"""

import os
import time
import pandas as pd
import plotly.express as px
import streamlit as st

# Configure Streamlit page layout and metadata
st.set_page_config(
    page_title="LLM Conversational Data Analysis Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.config import (
    SAMPLE_DATASETS,
    SUPPORTED_PROVIDERS,
    MAX_SELF_HEALING_RETRIES,
    EXECUTION_TIMEOUT_SECONDS
)
from src.engine.data_profiler import DatasetProfiler
from src.engine.schema import SchemaExtractor
from src.engine.self_healing import SelfHealingEngine
from src.llm.factory import LLMFactory
from src.ui.components import (
    render_header,
    render_metric_cards,
    render_chat_message,
    render_viva_guide
)
from src.ui.export_report import ReportGenerator
from src.ui.styles import get_custom_css

# Inject custom design system CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


# ==========================================================
# Session State Initialization
# ==========================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "df" not in st.session_state:
    st.session_state.df = None

if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = ""

if "selected_query" not in st.session_state:
    st.session_state.selected_query = None


# ==========================================================
# Sidebar: Configuration, File Upload & Engine Controls
# ==========================================================
with st.sidebar:
    st.markdown("### ⚙️ Engine Configuration")

    # 1. LLM Provider Selector
    provider_choice = st.selectbox(
        "AI / LLM Provider",
        options=list(SUPPORTED_PROVIDERS.keys()),
        index=0,
        help="Select which LLM backend will synthesize the code and insights."
    )

    provider_info = SUPPORTED_PROVIDERS[provider_choice]
    available_models = provider_info.get("models", [])
    default_model = provider_info.get("default_model", available_models[0] if available_models else "")

    model_options = list(available_models) + ["Custom Model..."]
    default_index = available_models.index(default_model) if default_model in available_models else 0

    model_choice = st.selectbox(
        "Inference Model",
        options=model_options,
        index=default_index,
        help="Select the AI model. For Google Gemini, gemini-3.8-flash is the latest recommended standard."
    )

    if model_choice == "Custom Model...":
        selected_model = st.text_input("Enter Custom Model Identifier:", value="gemini-3.8-flash")
    else:
        selected_model = model_choice


    # API Key Input (if not Demo or Ollama)
    api_key = None
    env_key_name = provider_info.get("env_key")
    env_default = os.getenv(env_key_name, "") if env_key_name else ""

    if env_key_name:
        api_key = st.text_input(
            f"{provider_choice} API Key",
            value=env_default,
            type="password",
            help=f"Enter your API key or set the {env_key_name} environment variable."
        )
        if not api_key:
            doc_link = provider_info.get("doc_url", "")
            if doc_link:
                st.caption(f"🔑 [Get a {provider_choice} API Key]({doc_link})")
            if provider_choice == "Groq (Free & Ultra-Fast)":
                st.info("💡 Groq offers 100% free API tier with ultra-fast inference speed!")

    # Base URL for Ollama
    base_url = None
    if "Ollama" in provider_choice:
        base_url = st.text_input("Ollama Base URL", value="http://localhost:11434")

    st.markdown("---")
    st.markdown("### 📁 Dataset Source")

    data_source_mode = st.radio(
        "Choose Data Source:",
        options=["Use Sample Datasets", "Upload CSV / Excel File"],
        index=0
    )

    uploaded_df = None
    current_dataset_name = ""

    if data_source_mode == "Use Sample Datasets":
        sample_choice = st.selectbox("Select Benchmark Dataset:", options=list(SAMPLE_DATASETS.keys()))
        file_path = SAMPLE_DATASETS[sample_choice]
        if os.path.exists(file_path):
            try:
                uploaded_df = pd.read_csv(file_path)
                current_dataset_name = sample_choice
            except Exception as e:
                st.error(f"Error loading sample dataset: {e}")
    else:
        uploaded_file = st.file_uploader(
            "Upload your dataset (.csv, .xlsx, .xls)",
            type=["csv", "xlsx", "xls"],
            help="Your data is loaded securely into local memory and never transmitted to external storage."
        )
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    uploaded_df = pd.read_csv(uploaded_file)
                else:
                    uploaded_df = pd.read_excel(uploaded_file)
                current_dataset_name = uploaded_file.name
            except Exception as e:
                st.error(f"Failed to read file: {e}")

    # Update session dataframe if dataset changed
    if uploaded_df is not None:
        if st.session_state.df is None or st.session_state.dataset_name != current_dataset_name:
            st.session_state.df = uploaded_df
            st.session_state.dataset_name = current_dataset_name
            st.session_state.chat_history = []  # reset chat on new dataset

    st.markdown("---")
    st.markdown("### 🎛️ Execution Settings")

    execution_mode = st.radio(
        "Query Execution Engine:",
        options=["Pandas Engine (Python)", "DuckDB SQL Engine"],
        index=0,
        help="Pandas Engine supports interactive Plotly charts, data transformations, and math. DuckDB executes high-speed ANSI SQL."
    )

    max_retries = st.slider(
        "Max Self-Correction Retries",
        min_value=1,
        max_value=5,
        value=MAX_SELF_HEALING_RETRIES,
        help="Number of times the autonomous loop will re-prompt the LLM to fix syntax or runtime errors."
    )

    if st.button("🗑️ Clear Conversation History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.selected_query = None
        st.rerun()

    st.markdown("---")
    st.caption("Developed for Academic & Production Portfolio Evaluation &bull; v1.0.0")


# ==========================================================
# Main Content View
# ==========================================================
render_header()

df = st.session_state.df
dataset_name = st.session_state.dataset_name

if df is None:
    st.info("👋 **Welcome!** Please select a sample dataset or upload a CSV/Excel file from the sidebar to begin your analysis.")
    st.stop()

# Compute dataset summary and health score
summary_metrics = DatasetProfiler.get_summary_metrics(df)
health_metrics = DatasetProfiler.compute_health_score(df)
suggested_questions = DatasetProfiler.generate_suggested_questions(df)

# Render KPI cards
render_metric_cards(summary_metrics, health_metrics)

# Navigation Tabs
tab_chat, tab_profile, tab_data, tab_report, tab_viva = st.tabs([
    "💬 Conversational Q&A",
    "📊 Deep Data Profiling & Health",
    "🔍 Dataset Explorer & Scratchpad",
    "📑 Executive Report Export",
    "🎓 Architecture & Viva Guide"
])


# ==========================================================
# TAB 1: Conversational Q&A / Natural Language Assistant
# ==========================================================
with tab_chat:
    st.markdown(f"#### 💬 Active Dataset: `{dataset_name}`")

    # Suggested Prompts Row
    st.markdown("##### 💡 Suggested Questions (Click to Analyze):")
    cols = st.columns(len(suggested_questions))
    for idx, prompt_text in enumerate(suggested_questions):
        with cols[idx]:
            if st.button(prompt_text, key=f"sugg_{idx}", use_container_width=True):
                st.session_state.selected_query = prompt_text
                st.rerun()

    st.markdown("---")

    # Display past conversation turns
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history:
            render_chat_message(msg)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2.5rem 1rem; color: #64748B;">
            <h3>Ask anything about your data</h3>
            <p>Try questions like: <em>"Show total sales by category as a bar chart"</em>, <em>"What is the average profit?"</em>, or <em>"Find any outliers in patient cost"</em>.</p>
        </div>
        """, unsafe_allow_html=True)

    # Chat input box
    chat_input_val = st.chat_input("Ask a question about this dataset (e.g., 'Show total sales by region as an interactive bar chart')...")

    # Determine query to run (from text input or suggested chip)
    query_to_run = None
    if chat_input_val:
        query_to_run = chat_input_val
    elif st.session_state.selected_query:
        query_to_run = st.session_state.selected_query
        st.session_state.selected_query = None

    if query_to_run:
        # Append user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": query_to_run,
            "id": f"u_{len(st.session_state.chat_history)}"
        })

        # Display user message immediately
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(f"**{query_to_run}**")

        # Run Assistant Pipeline with Live Status Feedback
        with st.chat_message("assistant", avatar="🤖"):
            status_container = st.status("Initializing AI analysis pipeline...", expanded=True)

            def status_logger(msg: str):
                status_container.write(msg)

            try:
                # Instantiate LLM Client via Factory
                llm_provider = LLMFactory.get_provider(
                    provider_name=provider_choice,
                    model_name=selected_model,
                    api_key=api_key,
                    base_url=base_url
                )

                # Format conversation history
                conv_history = [
                    {"role": m.get("role"), "content": m.get("content", "")}
                    for m in st.session_state.chat_history[:-1]
                ]

                # Run Self-Healing Engine based on chosen mode
                if "duckdb" in execution_mode.lower():
                    pipeline_res = SelfHealingEngine.run_sql_pipeline(
                        provider=llm_provider,
                        df=df,
                        user_question=query_to_run,
                        conversation_history=conv_history,
                        max_retries=max_retries,
                        status_callback=status_logger
                    )
                else:
                    pipeline_res = SelfHealingEngine.run_pandas_pipeline(
                        provider=llm_provider,
                        df=df,
                        user_question=query_to_run,
                        conversation_history=conv_history,
                        max_retries=max_retries,
                        status_callback=status_logger
                    )

                if pipeline_res.success:
                    status_container.update(
                        label=f"✅ Analysis completed successfully in {pipeline_res.total_time_ms} ms!",
                        state="complete",
                        expanded=False
                    )
                else:
                    status_container.update(
                        label="⚠️ Execution failed after self-healing attempts",
                        state="error",
                        expanded=True
                    )

                # Build assistant turn payload
                exec_res = pipeline_res.final_result
                assistant_payload = {
                    "role": "assistant",
                    "explanation": pipeline_res.explanation,
                    "code": exec_res.code if hasattr(exec_res, "code") else getattr(exec_res, "sql", ""),
                    "data": exec_res.data if hasattr(exec_res, "data") else None,
                    "figure": getattr(exec_res, "figure", None),
                    "healed": pipeline_res.healed,
                    "attempts": pipeline_res.total_attempts,
                    "duration_ms": pipeline_res.total_time_ms,
                    "mode": execution_mode,
                    "history": pipeline_res.history,
                    "id": f"a_{len(st.session_state.chat_history)}"
                }

                # Save to history and render
                st.session_state.chat_history.append(assistant_payload)
                render_chat_message(assistant_payload)

            except Exception as e:
                status_container.update(label=f"❌ Error: {str(e)}", state="error", expanded=True)
                err_payload = {
                    "role": "assistant",
                    "explanation": f"Pipeline Error: {str(e)}",
                    "code": "",
                    "healed": False,
                    "attempts": 1,
                    "duration_ms": 0.0,
                    "mode": execution_mode,
                    "id": f"a_err_{len(st.session_state.chat_history)}"
                }
                st.session_state.chat_history.append(err_payload)
                st.error(f"Failed to complete request: {str(e)}")


# ==========================================================
# TAB 2: Deep Data Profiling & Health Assessment
# ==========================================================
with tab_profile:
    st.markdown("### 📊 Automated Exploratory Data Analysis (EDA) & Data Health")

    col_h1, col_h2 = st.columns([1, 2])

    with col_h1:
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 20px;">
            <h4 style="margin: 0; color: #94A3B8;">Dataset Health Scorecard</h4>
            <div style="font-size: 3rem; font-weight: 800; color: {health_metrics.get('color')}; margin: 10px 0;">
                {health_metrics.get('score')}%
            </div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC;">
                {health_metrics.get('rating')}
            </div>
            <hr style="border-color: rgba(255,255,255,0.1); margin: 15px 0;">
            <p style="margin: 5px 0; font-size: 0.85rem; color: #94A3B8;">
                <strong>Missing Cells:</strong> {health_metrics.get('missing_cells')} ({health_metrics.get('missing_pct')}%)
            </p>
            <p style="margin: 5px 0; font-size: 0.85rem; color: #94A3B8;">
                <strong>Duplicate Rows:</strong> {health_metrics.get('duplicate_rows')} ({health_metrics.get('duplicate_pct')}%)
            </p>
            <p style="margin: 5px 0; font-size: 0.85rem; color: #94A3B8;">
                <strong>Clean Dimensions:</strong> {health_metrics.get('clean_columns_pct')}%
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_h2:
        st.markdown("#### 🔍 Missing Values & Cardinality Analysis")
        missing_tbl = DatasetProfiler.get_missing_values_table(df)
        st.dataframe(missing_tbl, use_container_width=True, height=240)

    st.markdown("---")
    st.markdown("#### 📈 Numerical Correlation Matrix")
    corr_df = DatasetProfiler.get_correlation_matrix(df)
    if not corr_df.empty:
        fig_corr = px.imshow(
            corr_df,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Viridis",
            title="Pearson Correlation Heatmap (Numeric Dimensions)"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Fewer than 2 numerical columns found; correlation heatmap unavailable.")

    st.markdown("---")
    st.markdown("#### 📐 Statistical Summary (All Dimensions)")
    st.dataframe(df.describe(include="all").transpose(), use_container_width=True)


# ==========================================================
# TAB 3: Dataset Explorer & Interactive Scratchpad
# ==========================================================
with tab_data:
    st.markdown("### 🔍 Raw Dataset Explorer")
    st.dataframe(df, use_container_width=True, height=350)

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.markdown("#### 📑 Extracted Schema Context (Passed to LLM):")
        schema_md = SchemaExtractor.generate_prompt_context(df)
        st.markdown(schema_md)

    with col_meta2:
        st.markdown("#### 🧪 Interactive Sandbox Scratchpad")
        st.caption("Test the AST Sandbox security filter or run manual Pandas code directly:")
        user_scratch_code = st.text_area(
            "Enter Python / Pandas Code:",
            value='''# Example: Calculate average and store in 'result'
result = df.describe()''',
            height=180
        )
        if st.button("🚀 Execute Code in Sandbox"):
            from src.engine.sandbox import CodeSandbox
            res = CodeSandbox.execute(user_scratch_code, df)
            if res.success:
                st.success(f"Execution succeeded in {res.execution_time_ms} ms")
                if res.figure:
                    if hasattr(res.figure, "to_plotly_json"):
                        st.plotly_chart(res.figure, use_container_width=True)
                    else:
                        st.pyplot(res.figure)
                if isinstance(res.data, pd.DataFrame):
                    st.dataframe(res.data, use_container_width=True)
                elif res.data is not None:
                    st.write(res.data)
                if res.stdout:
                    st.code(res.stdout)
            else:
                st.error(f"Execution Failed: {res.error_type} - {res.error_message}")


# ==========================================================
# TAB 4: Executive Report Export
# ==========================================================
with tab_report:
    st.markdown("### 📑 Generate & Export Executive Analysis Report")
    st.markdown("""
    Generate an executive-ready HTML & PDF-compatible summary report containing all
    insights, visualizations, health metrics, and code audit logs generated during this session.
    """)

    if not st.session_state.chat_history:
        st.warning("⚠️ No conversational queries recorded yet. Ask a few questions in the Chat tab first to populate your report.")
    else:
        html_report = ReportGenerator.generate_html_report(
            dataset_name=dataset_name,
            df=df,
            health_metrics=health_metrics,
            chat_history=st.session_state.chat_history,
            project_title="LLM Conversational Data Analysis Assistant"
        )

        st.download_button(
            label="📥 Download Executive HTML Report",
            data=html_report,
            file_name=f"Data_Analysis_Report_{int(time.time())}.html",
            mime="text/html",
            use_container_width=True
        )

        st.markdown("#### 👁️ Report Preview:")
        st.components.v1.html(html_report, height=650, scrolling=True)


# ==========================================================
# TAB 5: Architecture & Project Viva Guide
# ==========================================================
with tab_viva:
    render_viva_guide()
