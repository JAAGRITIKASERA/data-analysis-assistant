"""
Configuration and constants for the Conversational Data Analysis Assistant.
"""

import os
from typing import Dict, List

# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_DATA_DIR = os.path.join(BASE_DIR, "sample_datasets")

# Available sample datasets for quick testing/evaluation
SAMPLE_DATASETS: Dict[str, str] = {
    "🛒 E-Commerce Sales & Profit": os.path.join(SAMPLE_DATA_DIR, "ecommerce_sales.csv"),
    "🏥 Healthcare Patient Risk & Costs": os.path.join(SAMPLE_DATA_DIR, "healthcare_patients.csv"),
    "🎓 Student Academic Performance": os.path.join(SAMPLE_DATA_DIR, "student_academics.csv"),
    "📈 Tech Stocks Market Data": os.path.join(SAMPLE_DATA_DIR, "financial_tech_stocks.csv"),
}

# LLM Providers and available models
SUPPORTED_PROVIDERS = {
    "Google Gemini": {
        "models": ["gemini-3.8-flash", "gemini-3.8-pro", "gemini-1.5-flash", "gemini-1.5-pro"],
        "default_model": "gemini-3.8-flash",
        "env_key": "GEMINI_API_KEY",
        "doc_url": "https://aistudio.google.com/apikey"
    },
    "Groq (Free & Ultra-Fast)": {
        "models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "llama-3.1-8b-instant"],
        "default_model": "llama-3.3-70b-versatile",
        "env_key": "GROQ_API_KEY",
        "doc_url": "https://console.groq.com/keys"
    },
    "OpenAI": {
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
        "default_model": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
        "doc_url": "https://platform.openai.com/api-keys"
    },
    "Anthropic Claude": {
        "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
        "default_model": "claude-3-5-haiku-20241022",
        "env_key": "ANTHROPIC_API_KEY",
        "doc_url": "https://console.anthropic.com/"
    },
    "Ollama (Local / Privacy-First)": {
        "models": ["llama3", "mistral", "codellama", "deepseek-coder", "phi3"],
        "default_model": "llama3",
        "env_key": None,
        "default_base_url": "http://localhost:11434"
    },
    "Demo Mode (Offline / Rule-Based)": {
        "models": ["demo-analytical-engine"],
        "default_model": "demo-analytical-engine",
        "env_key": None,
        "description": "Zero API keys needed! Great for testing offline demonstrations & evaluators."
    }
}

# Execution Sandbox Security Configuration
BANNED_MODULES: List[str] = [
    "os", "sys", "subprocess", "shutil", "socket", "urllib", "requests",
    "http", "posix", "nt", "pty", "commands", "ctypes", "winreg",
    "msvcrt", "platform", "signal", "multiprocessing", "threading"
]

BANNED_BUILTINS: List[str] = [
    "exec", "eval", "compile", "open", "__import__", "globals",
    "locals", "input", "breakpoint", "memoryview", "exit", "quit"
]

# Max execution timeouts & retry limits
EXECUTION_TIMEOUT_SECONDS: int = 15
MAX_SELF_HEALING_RETRIES: int = 3
MAX_SAMPLE_ROWS_IN_SCHEMA: int = 3
MAX_CATEGORICAL_EXAMPLES: int = 5

# System Prompt Templates
PANDAS_SYSTEM_PROMPT = """You are an expert Senior Data Analyst & Python Specialist.
Your task is to translate the user's natural language question into valid, executable Python Pandas/Plotly code to analyze an in-memory DataFrame named `df`.

DATASET SCHEMA & METADATA:
{schema_context}

RULES FOR GENERATING CODE:
1. Always assume the dataset is already loaded in variable `df` as a pandas DataFrame.
2. Store the final numerical/tabular answer or summary DataFrame in variable `result`.
3. If the user asks for a chart or visualization:
   - Prioritize Plotly Express (`px`) or Plotly Graph Objects (`go`) for interactive modern charts.
   - Assign the chart to variable `fig` (e.g., `fig = px.bar(...)`).
   - Use clean modern templates (e.g., `template="plotly_white"` or `template="plotly_dark"`).
   - If using Matplotlib/Seaborn, ensure `plt.figure(...)` is called and do NOT call `plt.show()`.
4. If the query asks for a calculation or key performance metric:
   - Print or assign a clean summary, dictionary, or single metric to `result`.
5. NEVER attempt file I/O (`open`, `to_csv`, `read_csv`), network calls, or system imports (`os`, `sys`, `subprocess`).
6. Format column names strictly as shown in the schema above. Watch out for exact casing and spaces.
7. Wrap your entire code inside a single ```python and ``` markdown block.
8. Include a brief 1-2 sentence analytical explanation at the end outside the code block explaining the key findings or what the code computes.
"""

SQL_SYSTEM_PROMPT = """You are an expert Database Administrator and SQL Data Analyst.
Your task is to write a clean, standard SQL query (compatible with DuckDB / SQLite) to answer the user's question over a table named `dataset`.

TABLE SCHEMA:
{schema_context}

RULES FOR SQL:
1. The table name is `dataset`.
2. Write ONLY a valid SELECT query. NEVER write DROP, DELETE, ALTER, INSERT, UPDATE, or file operations.
3. Use standard aggregate functions (`SUM`, `AVG`, `COUNT`, `MAX`, `MIN`), `GROUP BY`, `ORDER BY`, and `LIMIT` where appropriate.
4. If column names contain spaces or special characters, quote them with double quotes (e.g., `"Order ID"`).
5. Wrap your query inside a ```sql and ``` block.
6. Provide a concise 1-2 sentence explanation of the query's business insight after the code block.
"""

SELF_HEALING_PROMPT = """Your previous Python code failed during execution with an error.

PREVIOUS FAILED CODE:
```python
{failed_code}
```

ERROR ENCOUNTERED:
Type: {error_type}
Message: {error_message}

DATASET SCHEMA REMINDER:
{schema_context}

ORIGINAL USER QUESTION:
{user_question}

INSTRUCTIONS TO FIX:
1. Analyze the exact error message (e.g. KeyError indicates wrong column name, TypeError indicates wrong data type or aggregation, AttributeError indicates invalid method).
2. Look at the schema above to ensure exact column names, data types, and available categories.
3. Provide the corrected, fully working Python code wrapped in a ```python ... ``` block.
4. Ensure the output is assigned to `result` (for data/numbers) or `fig` (for plots).
"""
