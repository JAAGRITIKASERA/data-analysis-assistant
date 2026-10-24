"""
Intelligent Mock / Heuristic Provider for zero-API-key demonstrations and offline testing.
Interprets questions and generates functional Pandas & Plotly code using schema introspection.
Ensures students and evaluators can experience the full app without an external API subscription.
"""

import re
from typing import Dict, List, Optional
from src.llm.provider_base import BaseLLMProvider


class MockProvider(BaseLLMProvider):
    """
    Simulates an LLM code generator by parsing dataset columns from the prompt
    and constructing valid Pandas / Plotly analysis scripts.
    """

    def __init__(self, model_name: str = "demo-analytical-engine"):
        super().__init__(model_name=model_name, api_key=None)

    @property
    def provider_name(self) -> str:
        return "Demo Analytical Engine (Offline)"

    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.1
    ) -> str:
        q_lower = user_prompt.lower()

        # Extract column names from system_prompt schema table
        col_names = re.findall(r"\|\s*`([^`]+)`\s*\|\s*`([^`]+)`", system_prompt)
        numeric_cols = []
        categorical_cols = []
        date_cols = []

        for col, dtype in col_names:
            dtype_l = dtype.lower()
            if any(n in dtype_l for n in ["int", "float", "double", "num"]):
                numeric_cols.append(col)
            elif any(d in dtype_l for d in ["date", "time"]):
                date_cols.append(col)
            else:
                if any(k in col.lower() for k in ["date", "time", "day", "month", "year"]):
                    date_cols.append(col)
                else:
                    categorical_cols.append(col)

        # Detect target columns mentioned in question
        matched_num = [c for c in numeric_cols if c.lower() in q_lower]
        matched_cat = [c for c in categorical_cols if c.lower() in q_lower]
        matched_date = [c for c in date_cols if c.lower() in q_lower]

        target_num = matched_num[0] if matched_num else (numeric_cols[0] if numeric_cols else None)
        target_cat = matched_cat[0] if matched_cat else (categorical_cols[0] if categorical_cols else None)
        target_date = matched_date[0] if matched_date else (date_cols[0] if date_cols else None)

        # 1. Bar Chart / Group By
        if any(w in q_lower for w in ["bar", "group", "by category", "total", "sum", "sales by", "profit by", "breakdown"]):
            if target_cat and target_num:
                return f"""```python
import pandas as pd
import plotly.express as px

# Group by {target_cat} and sum {target_num}
summary_df = df.groupby("{target_cat}")["{target_num}"].sum().reset_index()
summary_df = summary_df.sort_values(by="{target_num}", ascending=False)

fig = px.bar(
    summary_df,
    x="{target_cat}",
    y="{target_num}",
    title="Total {target_num} by {target_cat}",
    color="{target_cat}",
    template="plotly_white",
    text_auto=".2s"
)
fig.update_layout(xaxis_title="{target_cat}", yaxis_title="Total {target_num}")
result = summary_df
```

The analysis aggregates total **{target_num}** across all distinct **{target_cat}** categories. The category with the highest concentration is **{target_cat}** with top performance, as visualized in the interactive chart above."""

        # 2. Line Chart / Trend
        elif any(w in q_lower for w in ["line", "trend", "over time", "date", "monthly", "daily", "timeline"]):
            x_col = target_date if target_date else (target_cat if target_cat else df_cols_fallback(col_names))
            if target_num:
                return f"""```python
import pandas as pd
import plotly.express as px

# Sort and aggregate trend
trend_df = df.groupby("{x_col}")["{target_num}"].mean().reset_index()

fig = px.line(
    trend_df,
    x="{x_col}",
    y="{target_num}",
    title="Trend of {target_num} over {x_col}",
    markers=True,
    template="plotly_white"
)
fig.update_layout(xaxis_title="{x_col}", yaxis_title="Average {target_num}")
result = trend_df
```

The time-series line chart illustrates the trajectory and variance of **{target_num}** over **{x_col}**."""

        # 3. Scatter Plot / Correlation
        elif any(w in q_lower for w in ["scatter", "correlation", "relationship", "versus", "vs", "compare"]):
            if len(numeric_cols) >= 2:
                x_num = matched_num[0] if len(matched_num) >= 2 else numeric_cols[0]
                y_num = matched_num[1] if len(matched_num) >= 2 else numeric_cols[1]
                color_arg = f', color="{target_cat}"' if target_cat else ""
                return f"""```python
import pandas as pd
import plotly.express as px

fig = px.scatter(
    df,
    x="{x_num}",
    y="{y_num}"{color_arg},
    title="Correlation Analysis: {x_num} vs {y_num}",
    template="plotly_white",
    trendline="ols"
)
fig.update_layout(xaxis_title="{x_num}", yaxis_title="{y_num}")
result = df[["{x_num}", "{y_num}"]].describe()
```

The scatter plot evaluates the distribution and linear correlation between **{x_num}** and **{y_num}**."""

        # 4. Box Plot / Outliers / Distribution
        elif any(w in q_lower for w in ["box", "outlier", "distribution", "spread", "range"]):
            if target_num:
                cat_arg = f', x="{target_cat}"' if target_cat else ""
                return f"""```python
import pandas as pd
import plotly.express as px

fig = px.box(
    df,
    y="{target_num}"{cat_arg},
    title="Distribution and Outlier Analysis for {target_num}",
    template="plotly_white",
    points="all"
)
result = df["{target_num}"].describe().to_frame()
```

The box plot highlights median, quartiles, and potential outlier data points for **{target_num}**."""

        # 5. Top 5 / Top 10 / Ranking
        elif any(w in q_lower for w in ["top", "highest", "lowest", "rank", "best"]):
            cat = target_cat if target_cat else (categorical_cols[0] if categorical_cols else df_cols_fallback(col_names))
            num = target_num if target_num else (numeric_cols[0] if numeric_cols else df_cols_fallback(col_names))
            return f"""```python
import pandas as pd
import plotly.express as px

top_records = df.groupby("{cat}")["{num}"].sum().nlargest(5).reset_index()

fig = px.bar(
    top_records,
    x="{num}",
    y="{cat}",
    orientation="h",
    title="Top 5 {cat} by {num}",
    color="{num}",
    template="plotly_white"
)
fig.update_layout(yaxis=dict(autorange="reversed"))
result = top_records
```

Here are the top 5 leaders in **{cat}** based on total **{num}**."""

        # 6. Default Statistical Summary
        else:
            return f"""```python
import pandas as pd

# Comprehensive statistical overview
result = df.describe(include="all").transpose()
```

Here is the comprehensive statistical summary across all numerical and categorical dimensions in the active dataset."""


def df_cols_fallback(col_names):
    return col_names[0][0] if col_names else "Column"
