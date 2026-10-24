"""
Isolated and secure code execution sandbox for Pandas and dynamic visualizations.
Performs AST static security analysis, runs code in a guarded namespace,
and captures dataframes, scalar metrics, and Plotly/Matplotlib figures.
"""

import ast
import contextlib
import io
import re
import time
import traceback
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend safe for web apps/threads
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

from src.config import BANNED_BUILTINS, BANNED_MODULES


@dataclass
class ExecutionResult:
    """Holds the result and artifacts of a sandboxed execution."""
    success: bool
    code: str
    result_type: str  # 'dataframe', 'chart_plotly', 'chart_matplotlib', 'scalar', 'text', 'empty'
    data: Optional[Any] = None
    figure: Optional[Any] = None
    stdout: str = ""
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    traceback_str: Optional[str] = None
    execution_time_ms: float = 0.0


class SecurityViolationError(Exception):
    """Raised when generated code violates AST security policies."""
    pass


class CodeSandbox:
    """
    Safely executes LLM-generated Python/Pandas code.
    Enforces AST security inspection before running.
    """

    SAFE_BUILTINS = {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "dict": dict,
        "enumerate": enumerate,
        "filter": filter,
        "float": float,
        "format": format,
        "int": int,
        "isinstance": isinstance,
        "len": len,
        "list": list,
        "map": map,
        "max": max,
        "min": min,
        "print": print,
        "range": range,
        "reversed": reversed,
        "round": round,
        "set": set,
        "slice": slice,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "type": type,
        "zip": zip,
        "True": True,
        "False": False,
        "None": None,
    }

    @staticmethod
    def extract_python_code(raw_response: str) -> str:
        """
        Extracts executable Python code from an LLM response containing markdown.
        """
        if not raw_response or not isinstance(raw_response, str):
            return ""

        # Check for ```python ... ``` or ```py ... ```
        pattern = r"```(?:python|py)?\s*(.*?)\s*```"
        matches = re.findall(pattern, raw_response, re.DOTALL | re.IGNORECASE)

        if matches:
            # Join code blocks if multiple or take the primary one
            code = matches[0].strip()
        else:
            # If no markdown blocks, strip and check if entire string looks like code
            code = raw_response.strip()

        # Remove any stray interactive display commands like plt.show() or fig.show()
        # to prevent blocking or headless browser errors
        code_lines = []
        for line in code.splitlines():
            stripped = line.strip()
            if stripped in ["plt.show()", "fig.show()", "st.show()"]:
                continue
            code_lines.append(line)

        return "\n".join(code_lines).strip()

    @classmethod
    def validate_ast_security(cls, code: str) -> Tuple[bool, Optional[str]]:
        """
        Parses code into an Abstract Syntax Tree (AST) to verify that no banned
        system modules, file I/O calls, or reflection primitives are invoked.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"SyntaxError in generated code: {e}"

        for node in ast.walk(tree):
            # Check imports: import os, sys, etc.
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_pkg = alias.name.split(".")[0]
                    if root_pkg in BANNED_MODULES:
                        return False, f"Security Violation: Import of '{root_pkg}' is restricted."

            # Check from ... import ...
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_pkg = node.module.split(".")[0]
                    if root_pkg in BANNED_MODULES:
                        return False, f"Security Violation: Import from '{root_pkg}' is restricted."

            # Check banned function calls: open(), eval(), exec(), __import__()
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in BANNED_BUILTINS:
                        return False, f"Security Violation: Invocation of builtin '{func_name}' is restricted."
                elif isinstance(node.func, ast.Attribute):
                    attr_name = node.func.attr
                    if attr_name in ["__subclasses__", "__globals__", "__code__", "__bases__"]:
                        return False, f"Security Violation: Reflection attribute '{attr_name}' is restricted."

            # Check attribute access on dunders
            elif isinstance(node, ast.Attribute):
                if node.attr.startswith("__") and node.attr.endswith("__") and node.attr not in ["__name__", "__doc__"]:
                    return False, f"Security Violation: Access to dunder attribute '{node.attr}' is restricted."

        return True, None

    ALLOWED_MODULES = {
        "pandas", "numpy", "matplotlib", "plotly", "seaborn",
        "scipy", "sklearn", "math", "datetime", "re", "json"
    }

    @classmethod
    def _safe_import(cls, name, globals=None, locals=None, fromlist=(), level=0):
        root = name.split(".")[0]
        if root not in cls.ALLOWED_MODULES:
            raise ImportError(f"Import of module '{root}' is restricted in execution sandbox.")
        return __import__(name, globals, locals, fromlist, level)

    @classmethod
    def get_safe_builtins(cls) -> Dict[str, Any]:
        builtins_dict = cls.SAFE_BUILTINS.copy()
        builtins_dict["__import__"] = cls._safe_import
        return builtins_dict

    @classmethod
    def execute(cls, code: str, df: pd.DataFrame) -> ExecutionResult:
        """
        Executes verified Python code in a safe, controlled environment with `df`.
        Captures any resulting DataFrame, scalar calculation, or interactive Plotly/Matplotlib figure.
        """
        start_time = time.perf_counter()
        clean_code = cls.extract_python_code(code)

        if not clean_code:
            return ExecutionResult(
                success=False,
                code=code,
                result_type="empty",
                error_type="EmptyCodeError",
                error_message="No executable Python code found in the response."
            )

        # 1. AST Security Analysis
        is_safe, sec_reason = cls.validate_ast_security(clean_code)
        if not is_safe:
            return ExecutionResult(
                success=False,
                code=clean_code,
                result_type="security_violation",
                error_type="SecurityViolationError",
                error_message=sec_reason or "Code failed security inspection."
            )

        # 2. Prepare Sandbox Scope
        # Clear any existing matplotlib figures
        plt.close("all")

        # Isolated DataFrame copy to protect original dataset from accidental mutations
        df_copy = df.copy(deep=False)

        sandbox_globals: Dict[str, Any] = {
            "__builtins__": cls.get_safe_builtins(),
            "pd": pd,
            "np": np,
            "plt": plt,
            "px": px,
            "go": go,
            "sns": sns,
            "df": df_copy,
        }
        sandbox_locals: Dict[str, Any] = {}

        stdout_buffer = io.StringIO()

        # 3. Execution
        try:
            with contextlib.redirect_stdout(stdout_buffer):
                exec(clean_code, sandbox_globals, sandbox_locals)
            
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            stdout_content = stdout_buffer.getvalue().strip()

            # 4. Result Artifact Resolution
            # Check for figure first (Plotly or Matplotlib)
            fig_obj = None
            for f_key in ("fig", "chart", "figure", "plot"):
                if f_key in sandbox_locals and sandbox_locals[f_key] is not None:
                    fig_obj = sandbox_locals[f_key]
                    break
                elif f_key in sandbox_globals and sandbox_globals[f_key] is not None:
                    fig_obj = sandbox_globals[f_key]
                    break

            # Is it a Plotly figure?
            if fig_obj is not None and (hasattr(fig_obj, "to_plotly_json") or "plotly" in str(type(fig_obj)).lower()):
                return ExecutionResult(
                    success=True,
                    code=clean_code,
                    result_type="chart_plotly",
                    figure=fig_obj,
                    stdout=stdout_content,
                    execution_time_ms=elapsed_ms
                )
            # Matplotlib figure directly assigned
            elif fig_obj is not None and isinstance(fig_obj, (plt.Figure, matplotlib.figure.Figure)):
                return ExecutionResult(
                    success=True,
                    code=clean_code,
                    result_type="chart_matplotlib",
                    figure=fig_obj,
                    stdout=stdout_content,
                    execution_time_ms=elapsed_ms
                )
            # Check if any figure was plotted on global pyplot
            elif plt.get_fignums():
                current_fig = plt.gcf()
                return ExecutionResult(
                    success=True,
                    code=clean_code,
                    result_type="chart_matplotlib",
                    figure=current_fig,
                    stdout=stdout_content,
                    execution_time_ms=elapsed_ms
                )

            # Check for tabular or numerical result without using 'or' on DataFrames
            res_val = None
            for k in ("result", "summary", "ans", "output", "metrics"):
                if k in sandbox_locals and sandbox_locals[k] is not None:
                    res_val = sandbox_locals[k]
                    break
                elif k in sandbox_globals and sandbox_globals[k] is not None:
                    res_val = sandbox_globals[k]
                    break

            if isinstance(res_val, pd.DataFrame):
                return ExecutionResult(
                    success=True,
                    code=clean_code,
                    result_type="dataframe",
                    data=res_val,
                    stdout=stdout_content,
                    execution_time_ms=elapsed_ms
                )
            elif isinstance(res_val, pd.Series):
                return ExecutionResult(
                    success=True,
                    code=clean_code,
                    result_type="dataframe",
                    data=res_val.to_frame(),
                    stdout=stdout_content,
                    execution_time_ms=elapsed_ms
                )
            elif res_val is not None:
                return ExecutionResult(
                    success=True,
                    code=clean_code,
                    result_type="scalar",
                    data=res_val,
                    stdout=stdout_content,
                    execution_time_ms=elapsed_ms
                )
            elif stdout_content:
                return ExecutionResult(
                    success=True,
                    code=clean_code,
                    result_type="text",
                    data=stdout_content,
                    stdout=stdout_content,
                    execution_time_ms=elapsed_ms
                )
            else:
                # If neither result nor figure was assigned, look for any newly created DataFrame
                for var_name, var_val in sandbox_locals.items():
                    if isinstance(var_val, pd.DataFrame) and var_name != "df":
                        return ExecutionResult(
                            success=True,
                            code=clean_code,
                            result_type="dataframe",
                            data=var_val,
                            stdout=stdout_content,
                            execution_time_ms=elapsed_ms
                        )

                return ExecutionResult(
                    success=True,
                    code=clean_code,
                    result_type="empty",
                    stdout=stdout_content,
                    execution_time_ms=elapsed_ms
                )

        except Exception as err:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            err_type = type(err).__name__
            err_msg = str(err)
            tb = traceback.format_exc()
            return ExecutionResult(
                success=False,
                code=clean_code,
                result_type="error",
                error_type=err_type,
                error_message=err_msg,
                traceback_str=tb,
                stdout=stdout_buffer.getvalue().strip(),
                execution_time_ms=elapsed_ms
            )
        finally:
            stdout_buffer.close()
