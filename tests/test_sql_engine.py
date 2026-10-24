"""
Unit tests for DuckDB SQLEngine.
"""

import pandas as pd
from src.engine.sql_engine import SQLEngine


def test_sql_engine_select_query():
    df = pd.DataFrame({
        "Department": ["Sales", "Engineering", "Marketing", "Sales"],
        "Salary": [50000, 90000, 60000, 55000]
    })

    sql = "SELECT Department, AVG(Salary) as avg_sal FROM dataset GROUP BY Department ORDER BY avg_sal DESC"
    res = SQLEngine.execute_query(sql, df)

    assert res.success is True
    assert res.row_count == 3
    assert "avg_sal" in res.data.columns
    assert res.data.iloc[0]["Department"] == "Engineering"


def test_sql_engine_blocks_dangerous_keywords():
    df = pd.DataFrame({"id": [1, 2, 3]})
    dangerous_queries = [
        "DROP TABLE dataset",
        "DELETE FROM dataset WHERE id = 1",
        "ALTER TABLE dataset ADD COLUMN x INT",
        "TRUNCATE TABLE dataset",
        "INSTALL 'httpfs'",
        "ATTACH 'db.duckdb'"
    ]

    for q in dangerous_queries:
        res = SQLEngine.execute_query(q, df)
        assert res.success is False
        assert res.error_type == "SecurityViolationError"
