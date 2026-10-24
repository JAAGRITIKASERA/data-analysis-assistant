"""
Deep dataset profiler, automated exploratory data analysis (EDA),
and dynamic question generation module.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


class DatasetProfiler:
    """
    Computes statistical health metrics, data quality scores,
    and contextual query suggestions for uploaded datasets.
    """

    @classmethod
    def compute_health_score(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates a Data Quality / Health Score (0 - 100%) based on:
        - Missing values ratio (up to -40 pts)
        - Duplicate rows ratio (up to -30 pts)
        - Constant / zero-variance columns (up to -15 pts)
        - Column naming hygiene (up to -15 pts)
        """
        if df.empty:
            return {"score": 0, "rating": "Empty Dataset", "metrics": {}}

        total_cells = df.shape[0] * df.shape[1]
        missing_cells = int(df.isna().sum().sum())
        missing_ratio = (missing_cells / total_cells) if total_cells > 0 else 0.0

        duplicate_rows = int(df.duplicated().sum())
        duplicate_ratio = (duplicate_rows / len(df)) if len(df) > 0 else 0.0

        # Check for constant columns (1 unique value)
        constant_cols = [c for c in df.columns if df[c].nunique(dropna=False) <= 1]
        constant_penalty = min(15, len(constant_cols) * 5)

        # Check for awkward column names (leading/trailing whitespace or special symbols)
        bad_names = [c for c in df.columns if str(c).strip() != str(c) or "\n" in str(c)]
        naming_penalty = min(15, len(bad_names) * 3)

        missing_penalty = min(40, round(missing_ratio * 100 * 1.5, 1))
        duplicate_penalty = min(30, round(duplicate_ratio * 100 * 2.0, 1))

        score = max(5, round(100.0 - missing_penalty - duplicate_penalty - constant_penalty - naming_penalty, 1))

        if score >= 90:
            rating = "Excellent Quality"
            color = "#10B981"  # Emerald green
        elif score >= 75:
            rating = "Good Quality"
            color = "#3B82F6"  # Blue
        elif score >= 55:
            rating = "Moderate Quality"
            color = "#F59E0B"  # Amber
        else:
            rating = "Needs Cleaning"
            color = "#EF4444"  # Red

        return {
            "score": score,
            "rating": rating,
            "color": color,
            "missing_cells": missing_cells,
            "missing_pct": round(missing_ratio * 100, 2),
            "duplicate_rows": duplicate_rows,
            "duplicate_pct": round(duplicate_ratio * 100, 2),
            "constant_columns": constant_cols,
            "clean_columns_pct": round(((len(df.columns) - len(constant_cols)) / len(df.columns)) * 100, 1)
        }

    @classmethod
    def get_summary_metrics(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extracts high-level dataset metrics.
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
        datetime_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

        return {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_count": len(numeric_cols),
            "categorical_count": len(categorical_cols),
            "datetime_count": len(datetime_cols),
            "memory_mb": round(float(df.memory_usage(deep=True).sum()) / (1024 * 1024), 2),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "datetime_columns": datetime_cols
        }

    @classmethod
    def get_missing_values_table(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Returns a sorted DataFrame of columns and their missing values.
        """
        null_counts = df.isna().sum()
        null_pcts = (null_counts / len(df)) * 100
        
        report = pd.DataFrame({
            "Column": df.columns,
            "Data Type": [str(df[c].dtype) for c in df.columns],
            "Missing Count": null_counts.values,
            "Missing %": null_pcts.round(2).values,
            "Unique Values": [df[c].nunique(dropna=True) for c in df.columns]
        })
        return report.sort_values(by="Missing Count", ascending=False).reset_index(drop=True)

    @classmethod
    def get_correlation_matrix(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes the correlation matrix for numerical columns.
        """
        num_df = df.select_dtypes(include=[np.number])
        if num_df.shape[1] < 2:
            return pd.DataFrame()
        return num_df.corr().round(3)

    @classmethod
    def generate_suggested_questions(cls, df: pd.DataFrame) -> List[str]:
        """
        Dynamically generates smart, relevant questions tailored to the schema of the dataset.
        """
        questions: List[str] = []
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
        date_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

        # Try to detect date columns stored as string
        if not date_cols:
            for c in cat_cols:
                if any(k in c.lower() for k in ["date", "time", "year", "month", "day"]):
                    date_cols.append(c)

        # 1. Aggregation / Bar Chart
        if cat_cols and num_cols:
            cat = cat_cols[0]
            num = num_cols[0]
            questions.append(f"Show total {num} grouped by {cat} as an interactive bar chart.")
            if len(cat_cols) > 1 and len(num_cols) > 1:
                questions.append(f"What are the top 5 {cat_cols[1]} ranked by average {num_cols[1]}?")
            else:
                questions.append(f"Show the distribution of {num} across different {cat} categories.")

        # 2. Time series / Trend
        if date_cols and num_cols:
            d_col = date_cols[0]
            n_col = num_cols[0]
            questions.append(f"Plot the trend of {n_col} over {d_col} as a line chart.")

        # 3. Correlation / Scatter plot
        if len(num_cols) >= 2:
            questions.append(f"Create a scatter plot comparing {num_cols[0]} vs {num_cols[1]} to check correlation.")

        # 4. Outliers / Box plot
        if num_cols and cat_cols:
            questions.append(f"Generate a box plot of {num_cols[0]} to detect any outliers across {cat_cols[0]}.")

        # 5. Business / Statistical KPI Summary
        if num_cols:
            questions.append(f"Calculate key statistics (Mean, Median, Std Dev, Min, Max) for {num_cols[0]}.")

        # Default fallback questions if schema is unusual
        if len(questions) < 4:
            questions.append("Give me an executive summary of this dataset with key highlights.")
            questions.append("Which columns have the highest variance and missing values?")

        return questions[:5]
