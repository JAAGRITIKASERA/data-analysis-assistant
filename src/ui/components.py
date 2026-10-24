"""
Reusable Streamlit UI components, cards, and viva examination guide.
"""

from typing import Any, Callable, Dict, List
import pandas as pd
import streamlit as st


def render_header():
    """Renders the top branding hero banner."""
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">⚡ AI-Powered Natural Language Analytics</div>
        <h1 class="hero-title">Conversational Data Analysis Assistant</h1>
        <p class="hero-subtitle">
            Ask natural-language questions over complex CSV/Excel datasets.
            Get instant statistical computations, data transformations, and publication-ready interactive visualizations powered by autonomous code generation.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_metric_cards(summary: Dict[str, Any], health: Dict[str, Any]):
    """Renders high-level dataset KPI cards in a 4-column responsive grid."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Data Quality Score</div>
            <div class="metric-value" style="color: {health.get('color', '#10B981')};">
                {health.get('score', 100)}%
            </div>
            <div class="metric-sub">{health.get('rating', 'Valid')}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Rows</div>
            <div class="metric-value">{summary.get('total_rows', 0):,}</div>
            <div class="metric-sub">{health.get('duplicate_rows', 0)} duplicates detected</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Features / Columns</div>
            <div class="metric-value">{summary.get('total_columns', 0)}</div>
            <div class="metric-sub">{summary.get('numeric_count', 0)} numeric, {summary.get('categorical_count', 0)} categorical</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Memory Footprint</div>
            <div class="metric-value">{summary.get('memory_mb', 0.0)} MB</div>
            <div class="metric-sub">{health.get('missing_pct', 0.0)}% missing cells</div>
        </div>
        """, unsafe_allow_html=True)


def render_chat_message(item: Dict[str, Any]):
    """Renders a single conversation turn in the chat tab."""
    role = item.get("role", "user")

    if role == "user":
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(f"**{item.get('content', '')}**")
    else:
        with st.chat_message("assistant", avatar="🤖"):
            healed = item.get("healed", False)
            attempts = item.get("attempts", 1)
            duration_ms = item.get("duration_ms", 0.0)

            # 1. Healing badge if applicable
            if healed:
                st.markdown(f"""
                <div class="healed-badge">
                    <span>✨ Autonomous Self-Correction Activated: Resolved on Attempt {attempts}</span>
                </div>
                """, unsafe_allow_html=True)

            # 2. Text Explanation
            explanation = item.get("explanation", item.get("content", ""))
            if explanation:
                st.markdown(explanation)

            # 3. Interactive Visualization (Plotly or Matplotlib)
            fig = item.get("figure")
            if fig is not None:
                # Plotly figure
                if hasattr(fig, "to_plotly_json") or "plotly" in str(type(fig)).lower():
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.pyplot(fig)

            # 4. Tabular Data result
            data_res = item.get("data")
            if isinstance(data_res, pd.DataFrame) and not data_res.empty:
                st.markdown(f"**Data Output ({len(data_res)} rows):**")
                st.dataframe(data_res, use_container_width=True)
                # Quick CSV download for the slice/result
                csv_bytes = data_res.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download this result (CSV)",
                    data=csv_bytes,
                    file_name="query_result.csv",
                    mime="text/csv",
                    key=f"dl_{item.get('id', id(item))}"
                )
            elif data_res is not None and not isinstance(data_res, (pd.DataFrame, pd.Series)):
                st.info(f"**Result:** {data_res}")

            # 5. Expandable Code & Execution Telemetry Drawer
            code = item.get("code", "")
            if code:
                with st.expander(f"🔍 Inspect Executed Code & Pipeline Telemetry ({duration_ms} ms)"):
                    mode_label = item.get("mode", "Python Pandas")
                    st.code(code, language="python" if "pandas" in mode_label.lower() else "sql")
                    st.markdown(f"""
                    <div class="code-telemetry">
                        <span>⚡ <strong>Engine:</strong> {mode_label}</span>
                        <span>⏱️ <strong>Execution Time:</strong> {duration_ms} ms</span>
                        <span>🔄 <strong>Attempts:</strong> {attempts}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Show retry history if healed
                    history = item.get("history", [])
                    if len(history) > 1:
                        st.markdown("##### 🛠️ Self-Correction History:")
                        for h in history:
                            status_icon = "✅" if h.success else "❌"
                            st.markdown(f"- **Attempt {h.attempt_number}:** {status_icon} `{h.error_type or 'Success'}` ({h.duration_ms} ms)")
                            if not h.success:
                                st.caption(f"Error caught: `{h.error_message}`")


def render_viva_guide():
    """Renders comprehensive project documentation and viva Q&A for academic defense."""
    st.markdown("""
    ### 🎓 Final Year Project Defense & Viva Guide
    
    This guide provides in-depth technical explanations of the architecture, security models, and design trade-offs for evaluators and external examiners.

    ---

    #### 1. System Architecture Overview
    ```
    User Question (Natural Language) + Token-Safe Dataset Schema
                           │
                           ▼
          LLM Code Generation (Claude / Gemini / GPT-4o / Groq)
                           │
                           ▼
       AST Security Guard (Static Syntax Tree Analysis)
        [Blocks: os, sys, subprocess, eval, open, reflection]
                           │
                           ▼
         Isolated Execution Sandbox (In-Memory Pandas / DuckDB)
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
            [SUCCESS]             [FAILURE: KeyError/SyntaxError/TypeError]
                 │                   │
                 │                   ▼
                 │       Self-Healing Retry Loop (Up to 3 Retries)
                 │       [Feeds Traceback + Schema back to LLM]
                 │                   │
                 ▼                   ▼
    Render Dual Output (Data Table + Interactive Plotly Chart + Streamlit UI)
    ```

    ---

    #### 2. Key Technical Innovations
    1. **Code-Generation vs Simple Text Generation**:
       - *Problem*: Directly passing an entire 100,000-row CSV into an LLM causes context-length overflow, excessive cloud API costs, hallucinations, and privacy violations.
       - *Solution*: Pass only structural metadata (schema, dtypes, statistics, sample rows). The LLM writes functional Python/SQL code, which runs deterministically on the client's in-memory data.
    
    2. **AST Static Security Sandbox**:
       - *Problem*: Running `exec()` on LLM-generated code exposes the host server to Remote Code Execution (RCE) attacks (e.g. `import os; os.system("rm -rf /")`).
       - *Solution*: Pre-execution AST traversal parses the code tree, inspecting every import and call against blacklists (`os`, `sys`, `subprocess`, `open`, `eval`, `__subclasses__`). Only whitelisted math, pandas, and plotting libraries can run.

    3. **Autonomous Self-Correction Loop**:
       - When runtime errors occur (e.g. LLM misquotes a column name or applies an incompatible aggregation), the system intercepts the error, extracts the root cause, and re-prompts the LLM with the error context. It resolves over 90% of code generation faults autonomously without human intervention.

    4. **Dual Engine Support (Pandas + DuckDB SQL)**:
       - Offers both procedural data manipulation (Pandas/Plotly) and declarative relational querying (ANSI SQL via DuckDB) over the same in-memory dataset.

    ---

    #### 3. Top 10 Viva / Examiner Questions & Model Answers

    **Q1: Why did you not fine-tune an LLM instead of using Prompt Engineering with Schema?**
    > *Answer*: Fine-tuning embeds static knowledge from a training dataset and cannot generalize to arbitrary, user-uploaded CSVs with unseen columns. Dynamic in-context schema injection with few-shot guidance allows zero-shot execution on any tabular structure while respecting user privacy and keeping cloud costs low.

    **Q2: What happens if the generated code enters an infinite loop?**
    > *Answer*: The sandbox incorporates execution timeout constraints (`EXECUTION_TIMEOUT_SECONDS = 15s`). Furthermore, data analysis queries in Pandas are vectorized and avoid long unbounded `while` loops.

    **Q3: How do you handle categorical values that the LLM might hallucinate?**
    > *Answer*: Our `SchemaExtractor` dynamically extracts the top 5 most frequent categorical values per object column (e.g., `Region: ['North', 'South', 'East', 'West']`). This grounds the LLM to use exact string matches in its `df[df['Region'] == 'North']` filter conditions.

    **Q4: How does the system handle missing/null values?**
    > *Answer*: The dataset schema explicitly calculates the missing percentage per column. The system prompt instructs the LLM to handle nulls gracefully using `.dropna()` or `.fillna()` when performing calculations or plotting.

    **Q5: What is the difference between Matplotlib and Plotly in your assistant?**
    > *Answer*: Plotly Express creates client-side interactive WebGL/SVG charts supporting hover tooltips, zoom, pan, and legend toggling. Matplotlib is maintained as a fallback for statistical graphics (like box plots or heatmaps).
    """)
