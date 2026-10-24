"""
Schema extraction module for token-efficient and privacy-preserving LLM context.
Extracts column names, data types, sample values, unique counts, and stats
without transmitting the full raw dataset.
"""

from typing import Any, Dict, List
import numpy as np
import pandas as pd
from src.config import MAX_SAMPLE_ROWS_IN_SCHEMA, MAX_CATEGORICAL_EXAMPLES


class SchemaExtractor:
    """
    Extracts rich structural metadata and statistical summaries from a pandas DataFrame
    to build a token-compact prompt context for LLMs.
    """

    @staticmethod
    def extract_metadata(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract detailed metadata for each column in the DataFrame.
        """
        metadata: Dict[str, Any] = {
            "total_rows": int(len(df)),
            "total_columns": int(len(df.columns)),
            "memory_usage_kb": round(float(df.memory_usage(deep=True).sum()) / 1024.0, 2),
            "columns": []
        }

        for col in df.columns:
            series = df[col]
            dtype_str = str(series.dtype)
            null_count = int(series.isna().sum())
            null_pct = round((null_count / len(df)) * 100, 2) if len(df) > 0 else 0.0
            n_unique = int(series.nunique(dropna=True))

            col_info: Dict[str, Any] = {
                "name": str(col),
                "dtype": dtype_str,
                "null_count": null_count,
                "null_pct": null_pct,
                "unique_values_count": n_unique,
            }

            # Statistical analysis based on type
            if pd.api.types.is_numeric_dtype(series):
                cleaned_numeric = series.dropna()
                if not cleaned_numeric.empty:
                    col_info["min"] = round(float(cleaned_numeric.min()), 2)
                    col_info["max"] = round(float(cleaned_numeric.max()), 2)
                    col_info["mean"] = round(float(cleaned_numeric.mean()), 2)
                    col_info["median"] = round(float(cleaned_numeric.median()), 2)
                else:
                    col_info["min"] = col_info["max"] = col_info["mean"] = col_info["median"] = None
            elif pd.api.types.is_datetime64_any_dtype(series):
                cleaned_dates = series.dropna()
                if not cleaned_dates.empty:
                    col_info["min_date"] = str(cleaned_dates.min())
                    col_info["max_date"] = str(cleaned_dates.max())
            else:
                # Categorical / string / object column: sample top frequent values
                value_counts = series.value_counts(dropna=True).head(MAX_CATEGORICAL_EXAMPLES)
                col_info["sample_categories"] = [str(val) for val in value_counts.index.tolist()]

            metadata["columns"].append(col_info)

        return metadata

    @classmethod
    def generate_prompt_context(cls, df: pd.DataFrame) -> str:
        """
        Constructs a clean, Markdown-formatted schema text string to inject into LLM prompts.
        Keeps token count compact while providing high fidelity context.
        """
        meta = cls.extract_metadata(df)
        lines: List[str] = [
            f"### Dataset Summary: {meta['total_rows']} rows × {meta['total_columns']} columns ({meta['memory_usage_kb']} KB)",
            "",
            "#### Columns Specification:",
            "| Column Name | Data Type | Missing % | Unique Count | Details / Sample Values |",
            "|---|---|---|---|---|"
        ]

        for col in meta["columns"]:
            name = col["name"]
            dtype = col["dtype"]
            null_pct = f"{col['null_pct']}%"
            unique_cnt = col["unique_values_count"]

            if "mean" in col and col["mean"] is not None:
                details = f"Min: {col['min']}, Max: {col['max']}, Mean: {col['mean']}, Median: {col['median']}"
            elif "sample_categories" in col:
                cats = ", ".join([f"'{c}'" for c in col["sample_categories"][:4]])
                details = f"Examples: [{cats}]"
            elif "min_date" in col:
                details = f"Range: {col['min_date']} to {col['max_date']}"
            else:
                details = "N/A"

            lines.append(f"| `{name}` | `{dtype}` | {null_pct} | {unique_cnt} | {details} |")

        # Include first 3 anonymized sample rows
        lines.append("")
        lines.append(f"#### First {min(MAX_SAMPLE_ROWS_IN_SCHEMA, len(df))} Sample Rows Preview:")
        try:
            sample_df = df.head(MAX_SAMPLE_ROWS_IN_SCHEMA).copy()
            # Clean display formatting for table
            sample_md = sample_df.to_markdown(index=False)
            lines.append(sample_md)
        except Exception:
            lines.append(sample_df.to_string(index=False))

        return "\n".join(lines)
