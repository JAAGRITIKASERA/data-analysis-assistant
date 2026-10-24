"""
Unit tests for Schema Extractor.
"""

import pandas as pd
import pytest
from src.engine.schema import SchemaExtractor


def test_schema_metadata_extraction():
    df = pd.DataFrame({
        "Age": [25, 30, 35, 40, None],
        "Department": ["Sales", "Engineering", "Marketing", "Sales", "Sales"],
        "Salary": [50000.0, 75000.0, 62000.0, 91000.0, 48000.0]
    })

    meta = SchemaExtractor.extract_metadata(df)
    assert meta["total_rows"] == 5
    assert meta["total_columns"] == 3

    col_names = [c["name"] for c in meta["columns"]]
    assert "Age" in col_names
    assert "Department" in col_names
    assert "Salary" in col_names

    # Check null stats
    age_col = next(c for c in meta["columns"] if c["name"] == "Age")
    assert age_col["null_count"] == 1
    assert age_col["null_pct"] == 20.0

    # Check categorical categories
    dept_col = next(c for c in meta["columns"] if c["name"] == "Department")
    assert "Sales" in dept_col["sample_categories"]


def test_schema_prompt_generation():
    df = pd.DataFrame({
        "Region": ["North", "South", "East", "West"],
        "Sales": [1200, 3400, 2100, 5600]
    })
    prompt_str = SchemaExtractor.generate_prompt_context(df)
    assert "Dataset Summary:" in prompt_str
    assert "`Region`" in prompt_str
    assert "`Sales`" in prompt_str
    assert "Sample Rows Preview:" in prompt_str
