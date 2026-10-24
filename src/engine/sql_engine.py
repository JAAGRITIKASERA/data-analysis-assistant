"""
In-memory DuckDB SQL execution engine for Text-to-SQL queries over uploaded datasets.
Allows querying datasets directly with standard SQL without setting up a database server.
"""

import re
import time
from dataclasses import dataclass
from typing import Any, Optional, Tuple
import pandas as pd

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False


@dataclass
class SQLExecutionResult:
    """Holds the result of a DuckDB SQL query execution."""
    success: bool
    sql: str
    data: Optional[pd.DataFrame] = None
    row_count: int = 0
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0


class SQLEngine:
    """
    Executes validated SQL queries against in-memory pandas DataFrames using DuckDB.
    """

    BANNED_SQL_KEYWORDS = [
        r"\bDROP\b", r"\bDELETE\b", r"\bALTER\b", r"\bTRUNCATE\b",
        r"\bINSERT\b", r"\bUPDATE\b", r"\bCREATE\b", r"\bATTACH\b",
        r"\bDETACH\b", r"\bINSTALL\b", r"\bLOAD\b", r"\bCOPY\b",
        r"\bEXPORT\b", r"\bIMPORT\b", r"\bPRAGMA\b"
    ]

    @staticmethod
    def extract_sql_query(raw_text: str) -> str:
        """
        Extracts SQL query from LLM markdown response.
        """
        if not raw_text:
            return ""

        pattern = r"```(?:sql)?\s*(.*?)\s*```"
        matches = re.findall(pattern, raw_text, re.DOTALL | re.IGNORECASE)
        if matches:
            query = matches[0].strip()
        else:
            query = raw_text.strip()

        return query

    @classmethod
    def validate_sql_safety(cls, sql: str) -> Tuple[bool, Optional[str]]:
        """
        Verifies that the SQL query is strictly read-only and does not invoke
        system or file operations.
        """
        for pattern in cls.BANNED_SQL_KEYWORDS:
            if re.search(pattern, sql, re.IGNORECASE):
                keyword = pattern.replace(r"\b", "")
                return False, f"Security Violation: SQL keyword '{keyword}' is forbidden in read-only mode."

        # Must start with SELECT or WITH
        clean_stripped = sql.strip().upper()
        if not (clean_stripped.startswith("SELECT") or clean_stripped.startswith("WITH")):
            return False, "Security Violation: Only SELECT or WITH queries are permitted."

        return True, None

    @classmethod
    def execute_query(cls, sql_query: str, df: pd.DataFrame) -> SQLExecutionResult:
        """
        Executes a SQL query against the provided DataFrame registered as 'dataset' and 'data'.
        """
        start = time.perf_counter()
        clean_sql = cls.extract_sql_query(sql_query)

        if not clean_sql:
            return SQLExecutionResult(
                success=False,
                sql=sql_query,
                error_type="EmptySQLError",
                error_message="No executable SQL query found in the response."
            )

        is_safe, sec_reason = cls.validate_sql_safety(clean_sql)
        if not is_safe:
            return SQLExecutionResult(
                success=False,
                sql=clean_sql,
                error_type="SecurityViolationError",
                error_message=sec_reason
            )

        if not DUCKDB_AVAILABLE:
            # Fallback to pandasql or error
            return SQLExecutionResult(
                success=False,
                sql=clean_sql,
                error_type="ModuleNotFoundError",
                error_message="DuckDB is not installed in the current environment."
            )

        try:
            # Create a localized DuckDB connection
            con = duckdb.connect(database=":memory:")
            # Register dataframe in connection
            con.register("dataset", df)
            con.register("data", df)
            con.register("df", df)

            result_df = con.execute(clean_sql).df()
            elapsed_ms = round((time.perf_counter() - start) * 1000.0, 2)
            con.close()

            return SQLExecutionResult(
                success=True,
                sql=clean_sql,
                data=result_df,
                row_count=len(result_df),
                execution_time_ms=elapsed_ms
            )

        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start) * 1000.0, 2)
            return SQLExecutionResult(
                success=False,
                sql=clean_sql,
                error_type=type(e).__name__,
                error_message=str(e),
                execution_time_ms=elapsed_ms
            )
