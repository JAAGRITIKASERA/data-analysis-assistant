"""
Unit tests for Safe Sandbox Code Execution and AST Security Guard.
"""

import pandas as pd
from src.engine.sandbox import CodeSandbox


def test_sandbox_security_blocks_banned_modules():
    malicious_scripts = [
        "import os\nos.system('dir')",
        "import sys\nprint(sys.version)",
        "from subprocess import Popen\nPopen(['cmd'])",
        "import shutil\nshutil.rmtree('.')",
        "f = open('secret.txt', 'w')\nf.write('data')",
        "eval('__import__(\"os\").system(\"echo hacked\")')",
        "exec('print(123)')",
    ]

    df = pd.DataFrame({"a": [1, 2, 3]})

    for script in malicious_scripts:
        is_safe, reason = CodeSandbox.validate_ast_security(script)
        assert not is_safe, f"Expected security check to fail for: {script}"
        assert "Security Violation" in reason

        # Also verify execute() returns failure without running
        res = CodeSandbox.execute(script, df)
        assert not res.success
        assert res.error_type == "SecurityViolationError"


def test_sandbox_executes_valid_pandas():
    df = pd.DataFrame({
        "Product": ["A", "B", "C"],
        "Sales": [100, 200, 300]
    })

    code = """
result = df["Sales"].sum()
"""
    res = CodeSandbox.execute(code, df)
    assert res.success
    assert res.result_type == "scalar"
    assert res.data == 600


def test_sandbox_captures_dataframe_aggregation():
    df = pd.DataFrame({
        "Category": ["Tech", "Tech", "Furniture"],
        "Revenue": [500, 700, 300]
    })

    code = """
result = df.groupby("Category")["Revenue"].sum().reset_index()
"""
    res = CodeSandbox.execute(code, df)
    assert res.success
    assert res.result_type == "dataframe"
    assert len(res.data) == 2


def test_sandbox_captures_plotly_chart():
    df = pd.DataFrame({
        "Category": ["Tech", "Furniture"],
        "Revenue": [1200, 300]
    })

    code = """
import plotly.express as px
fig = px.bar(df, x="Category", y="Revenue")
"""
    res = CodeSandbox.execute(code, df)
    assert res.success
    assert res.result_type == "chart_plotly"
    assert res.figure is not None


def test_sandbox_catches_runtime_errors():
    df = pd.DataFrame({"A": [1, 2, 3]})
    code = "result = df['NonExistentColumn'].mean()"

    res = CodeSandbox.execute(code, df)
    assert not res.success
    assert res.error_type == "KeyError"
    assert "NonExistentColumn" in res.error_message
