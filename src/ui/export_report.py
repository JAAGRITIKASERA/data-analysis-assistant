"""
Executive Analytics Report Generator.
Exports conversational insights, charts, and dataset health scores into a
standalone, beautifully styled HTML document suitable for PDF export and executive presentation.
"""

import base64
import datetime
import io
from typing import Any, Dict, List
import matplotlib.pyplot as plt
import pandas as pd
import plotly.io as pio


class ReportGenerator:
    """Compiles session chat history, dataset health, and generated charts into an executive report."""

    @staticmethod
    def figure_to_base64_img(fig: Any) -> str:
        """Converts Plotly or Matplotlib figure into a base64 encoded PNG or SVG for HTML embedding."""
        if fig is None:
            return ""

        # Matplotlib figure
        if isinstance(fig, plt.Figure):
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", dpi=130)
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode("utf-8")
            return f'<img src="data:image/png;base64,{encoded}" style="max-width:100%; border-radius:8px; margin: 12px 0;" />'

        # Plotly figure
        try:
            # Check if Plotly figure can be exported as interactive div
            html_div = pio.to_html(fig, include_plotlyjs="cdn", full_html=False)
            return f'<div class="chart-embed">{html_div}</div>'
        except Exception:
            return "<p><em>[Chart could not be embedded]</em></p>"

    @classmethod
    def generate_html_report(
        cls,
        dataset_name: str,
        df: pd.DataFrame,
        health_metrics: Dict[str, Any],
        chat_history: List[Dict[str, Any]],
        project_title: str = "Conversational Data Analysis Assistant"
    ) -> str:
        """
        Builds a comprehensive, self-contained HTML report.
        """
        now_str = datetime.datetime.now().strftime("%B %d, %Y - %H:%M:%S")
        total_rows = len(df)
        total_cols = len(df.columns)
        health_score = health_metrics.get("score", 100)
        health_rating = health_metrics.get("rating", "Good")

        # Build Q&A Cards HTML
        qa_cards_html = []
        for i, item in enumerate(chat_history, 1):
            if item.get("role") != "user":
                continue

            # Find matching assistant response
            idx = chat_history.index(item)
            assistant_item = chat_history[idx + 1] if idx + 1 < len(chat_history) else {}

            user_query = item.get("content", "")
            explanation = assistant_item.get("explanation", assistant_item.get("content", ""))
            code = assistant_item.get("code", "")
            fig = assistant_item.get("figure", None)
            res_df = assistant_item.get("data", None)
            healed = assistant_item.get("healed", False)
            attempts = assistant_item.get("attempts", 1)

            fig_html = cls.figure_to_base64_img(fig) if fig is not None else ""

            table_html = ""
            if isinstance(res_df, pd.DataFrame) and not res_df.empty:
                table_html = f"""
                <div class="table-container">
                    <h4>Result Preview ({len(res_df)} rows):</h4>
                    {res_df.head(10).to_html(classes="report-table", index=False)}
                </div>
                """

            healing_badge = ""
            if healed:
                healing_badge = f'<span class="badge badge-success">✨ Auto-Corrected on Attempt {attempts}</span>'

            qa_cards_html.append(f"""
            <div class="qa-card">
                <div class="query-header">
                    <span class="query-num">Q{i}</span>
                    <h3 class="query-text">{user_query}</h3>
                    {healing_badge}
                </div>
                <div class="query-body">
                    <div class="insight-text">
                        <strong>Key Insight:</strong>
                        <p>{explanation}</p>
                    </div>
                    {fig_html}
                    {table_html}
                    <details class="code-details">
                        <summary>View Executed Code</summary>
                        <pre><code>{code}</code></pre>
                    </details>
                </div>
            </div>
            """)

        qa_content = "\n".join(qa_cards_html) if qa_cards_html else "<p>No questions recorded yet.</p>"

        # Complete HTML document
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_title} - Executive Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
        
        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #F8FAFC;
            color: #1E293B;
            margin: 0;
            padding: 40px;
            line-height: 1.6;
        }}
        .report-wrapper {{
            max-width: 960px;
            margin: 0 auto;
            background: #FFFFFF;
            padding: 48px;
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06);
            border: 1px solid #E2E8F0;
        }}
        .header {{
            border-bottom: 2px solid #E2E8F0;
            padding-bottom: 24px;
            margin-bottom: 32px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .badge-primary {{ background: #EEF2FF; color: #4F46E5; }}
        .badge-success {{ background: #ECFDF5; color: #059669; }}
        h1 {{ margin: 12px 0 6px 0; color: #0F172A; font-size: 2rem; font-weight: 800; }}
        .meta-line {{ color: #64748B; font-size: 0.9rem; }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 36px;
        }}
        .kpi-card {{
            background: #F1F5F9;
            padding: 16px;
            border-radius: 10px;
            border: 1px solid #E2E8F0;
        }}
        .kpi-title {{ font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 600; }}
        .kpi-val {{ font-size: 1.6rem; font-weight: 800; color: #0F172A; margin-top: 4px; }}
        
        .qa-card {{
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            margin-bottom: 28px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
            overflow: hidden;
        }}
        .query-header {{
            background: #F8FAFC;
            padding: 16px 20px;
            border-bottom: 1px solid #E2E8F0;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .query-num {{
            background: #4F46E5;
            color: #FFF;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
        }}
        .query-text {{ margin: 0; font-size: 1.1rem; color: #0F172A; font-weight: 700; flex: 1; }}
        .query-body {{ padding: 24px; }}
        
        .report-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
            font-size: 0.85rem;
        }}
        .report-table th, .report-table td {{
            padding: 8px 12px;
            border: 1px solid #E2E8F0;
            text-align: left;
        }}
        .report-table th {{ background: #F8FAFC; color: #475569; }}
        
        .code-details {{
            margin-top: 16px;
            background: #0F172A;
            color: #F8FAFC;
            border-radius: 8px;
            padding: 12px;
        }}
        .code-details summary {{ cursor: pointer; color: #94A3B8; font-size: 0.85rem; }}
        pre {{ margin: 10px 0 0 0; overflow-x: auto; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }}
        
        .footer {{
            border-top: 2px solid #E2E8F0;
            padding-top: 20px;
            margin-top: 40px;
            font-size: 0.85rem;
            color: #94A3B8;
            text-align: center;
        }}
        @media print {{
            body {{ padding: 0; background: #FFF; }}
            .report-wrapper {{ box-shadow: none; border: none; padding: 20px; }}
            .code-details {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="report-wrapper">
        <div class="header">
            <span class="badge badge-primary">Data Intelligence & Analysis Report</span>
            <h1>{project_title}</h1>
            <div class="meta-line">
                <span><strong>Dataset:</strong> {dataset_name}</span> &bull; 
                <span><strong>Generated:</strong> {now_str}</span>
            </div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Data Quality Score</div>
                <div class="kpi-val" style="color: {health_metrics.get('color', '#10B981')};">{health_score}%</div>
                <span style="font-size: 0.72rem; color: #64748B;">{health_rating}</span>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Total Records</div>
                <div class="kpi-val">{total_rows:,}</div>
                <span style="font-size: 0.72rem; color: #64748B;">Validated rows</span>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Total Features</div>
                <div class="kpi-val">{total_cols}</div>
                <span style="font-size: 0.72rem; color: #64748B;">Dimensions analyzed</span>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Q&A Queries</div>
                <div class="kpi-val">{len(qa_cards_html)}</div>
                <span style="font-size: 0.72rem; color: #64748B;">Insights generated</span>
            </div>
        </div>

        <h2>Executive Analytical Insights & Visualizations</h2>
        {qa_content}

        <div class="footer">
            <p>Generated autonomously by <strong>Conversational Data Analysis Assistant</strong></p>
            <p>Powered by LLM Code Synthesis &bull; AST-Inspected Isolated Execution Sandbox &bull; Self-Correcting Engine</p>
        </div>
    </div>
</body>
</html>
"""
        return html
