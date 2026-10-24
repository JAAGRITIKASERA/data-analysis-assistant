# ⚡ Conversational Data Analysis Assistant (LLM + Pandas / SQL Sandbox)

> **Natural-Language Q&A over CSV & Excel Datasets with Autonomous Code Generation, AST-Guarded Execution Sandbox, and Self-Healing Error Recovery.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit%201.30+-red.svg)](https://streamlit.io/)
[![DuckDB](https://img.shields.io/badge/SQL-DuckDB-yellow.svg)](https://duckdb.org/)
[![Tests](https://img.shields.io/badge/tests-11%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Executive Summary

Traditional Natural Language Processing (NLP) solutions for tabular datasets pass raw data rows directly to an LLM context window. This approach suffers from:
1. **Context Window Overflow & High Latency**: Large datasets (>1,000 rows) exceed token limits or incur steep API fees.
2. **Data Privacy Risks**: Uploading entire customer, financial, or healthcare records to cloud providers violates privacy mandates (GDPR/HIPAA).
3. **Hallucination in Complex Arithmetic**: LLMs frequently calculate inaccurate sums, averages, or variances when generating free text.

### The Solution:
The **Conversational Data Analysis Assistant** replaces static text generation with **Deterministic Code Generation & Isolated Execution**:
- **Privacy-Safe Schema Context**: Only structural metadata (column names, data types, null counts, statistical min/max/mean, and top categorical values) is sent to the LLM (~300–800 tokens).
- **Dual Query Engines**: Supports both procedural data analysis (**Pandas / Plotly**) and declarative relational querying (**DuckDB ANSI SQL**).
- **AST Security Sandbox**: Pre-execution Abstract Syntax Tree (AST) validation blocks unauthorized system calls (`os`, `sys`, `subprocess`, `open`, `eval`) before executing code in memory.
- **Autonomous Self-Healing Loop**: If code encounters a runtime error (`KeyError`, `AttributeError`, `TypeError`), the engine intercepts the stack trace, diagnoses the fault, re-prompts the LLM with error context, and re-runs the repaired code seamlessly without interrupting the user.
- **One-Click Executive Report**: Generates and downloads a publication-ready HTML/PDF analysis report with embedded interactive charts, data health scorecards, and audit logs.

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        User Interface (Streamlit)                      │
│   • File Uploader (.csv, .xlsx)      • Interactive Chat Interface      │
│   • 4 Real-World Sample Datasets     • Suggested Questions Chips       │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│            Privacy-Preserving Schema Extraction (schema.py)            │
│   • Columns & Data Types             • Non-null counts & Missing %     │
│   • Top 5 Categorical Value Samples  • Numeric Min/Max/Mean/Median     │
│   • 3 Anonymized Sample Rows Preview (Token footprint < 800 tokens)   │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   LLM Provider Factory (src/llm/)                     │
│   • Google Gemini (3.8 Flash, 1.5 Pro)   • Groq (Llama-3.3-70b Free)   │
│   • OpenAI (GPT-4o, GPT-4o-mini)         • Anthropic (Claude 3.5 Sonnet)│
│   • Ollama (Local / Offline)             • Demo Mode (Zero API Key)    │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   AST Security Guard (sandbox.py)                      │
│   • Inspects Abstract Syntax Tree before running `exec()`             │
│   • BLOCKS: `os`, `sys`, `subprocess`, `shutil`, `open`, `eval`        │
│   • PERMITS: `df`, `pd`, `np`, `px`, `go`, `plt`, `sns`, safe math    │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │
                     ┌───────────────┴───────────────┐
                     ▼                               ▼
       [Execution Succeeded]             [Runtime Error Caught]
                     │                   (KeyError, TypeError, etc.)
                     │                               │
                     │                               ▼
                     │              Autonomous Self-Healing Loop
                     │              (Feeds traceback + schema to LLM)
                     │              [Up to 3 Retries - Autonomous]
                     │                               │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Unified Presentation                            │
│   • Interactive Plotly / Matplotlib Charts                             │
│   • Data Tables with CSV Download                                      │
│   • Self-Healing Badge ("Resolved on Attempt 2")                       │
│   • Expandable Code & Execution Telemetry Drawer                       │
│   • Executive HTML / PDF Report Generator                             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Features

| Feature | Description |
|---|---|
| **Natural Language Q&A** | Converts user queries into verified Pandas or DuckDB SQL code. |
| **Dynamic Visualizations** | Automatically selects and renders Plotly Express interactive charts (Bar, Line, Scatter, Box, Heatmap). |
| **Self-Healing Agent** | Intercepts runtime errors and automatically re-prompts the LLM with error context to heal the code. |
| **Deep Data Profiler** | 0–100% Data Health Scorecard, missing value distribution, duplicate checks, and Pearson correlation heatmaps. |
| **Multi-Provider Support** | Works with Google Gemini, Groq, OpenAI, Anthropic Claude, Local Ollama, or Offline Demo Mode. |
| **Benchmark Datasets** | Pre-loaded with E-Commerce Sales, Healthcare Patients, Student Performance, and Tech Stocks. |
| **Report Export** | Standalone HTML export with embedded charts, stats, and audit logs. |

---

## 📂 Project Structure

```
data_analysis_assistant/
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Python dependencies
├── .env.example                # API key template
├── .gitignore                  # Git ignore rules
├── README.md                   # Complete documentation & viva guide
├── create_sample_data.py       # Script generating 4 benchmark datasets
├── sample_datasets/            # Pre-populated datasets
│   ├── ecommerce_sales.csv     # 100 rows: Sales, profit, category, region
│   ├── healthcare_patients.csv # 100 rows: Age, BP, cholesterol, medical cost
│   ├── student_academics.csv   # 100 rows: Study hours, attendance, scores
│   └── financial_tech_stocks.csv # 80 rows: Stock prices, volume, returns
├── src/
│   ├── __init__.py
│   ├── config.py               # Constants, prompts, security whitelists
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── schema.py           # Token-safe schema extractor
│   │   ├── sandbox.py          # AST security validator & execution sandbox
│   │   ├── sql_engine.py       # DuckDB Text-to-SQL engine
│   │   ├── self_healing.py     # Autonomous self-correction retry loop
│   │   └── data_profiler.py    # Health scoring, EDA & question suggestions
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── provider_base.py    # Abstract base class for LLMs
│   │   ├── gemini_provider.py  # Google Gemini (google-genai SDK)
│   │   ├── openai_provider.py  # OpenAI (GPT-4o/mini)
│   │   ├── groq_provider.py    # Groq (Llama-3.3-70b free fast tier)
│   │   ├── anthropic_provider.py # Claude 3.5 Sonnet / Haiku
│   │   ├── ollama_provider.py  # Local Ollama REST client
│   │   ├── mock_provider.py    # Intelligent rule-based engine (zero API key)
│   │   └── factory.py          # Dynamic LLM provider factory
│   └── ui/
│       ├── __init__.py
│       ├── styles.py           # Custom modern CSS & design system
│       ├── components.py       # Reusable UI widgets & viva guide
│       └── export_report.py    # Standalone HTML report generator
└── tests/
    ├── test_schema.py          # 2 tests: Schema metadata & prompt formatting
    ├── test_sandbox.py         # 5 tests: AST security & execution capture
    ├── test_self_healing.py    # 2 tests: Error recovery & mock generation
    └── test_sql_engine.py      # 2 tests: DuckDB queries & keyword security
```

---

## 🛠️ Installation & Quickstart

### 1. Clone or Open the Workspace
```bash
git clone https://github.com/your-username/conversational-data-analysis-assistant.git
cd conversational-data-analysis-assistant
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Generate Benchmark Datasets (Optional)
```bash
python create_sample_data.py
```

### 4. Configure API Keys (Optional)
Copy `.env.example` to `.env` and insert your API key:
```env
GEMINI_API_KEY=your_gemini_key_here
# OR
GROQ_API_KEY=your_groq_key_here
```
> *Note:* You can also enter API keys directly in the web app sidebar, or select **"Demo Mode (Offline / Rule-Based)"** to test immediately without any API keys!

### 5. Launch the Streamlit App
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 🧪 Running Automated Unit Tests

The test suite validates schema generation, AST sandbox security, error recovery, and DuckDB SQL:

```bash
python -m pytest tests -v
```

Expected output:
```text
tests/test_sandbox.py .....                   [ 45%]
tests/test_schema.py ..                       [ 63%]
tests/test_self_healing.py ..                 [ 81%]
tests/test_sql_engine.py ..                   [100%]
====================== 11 passed in 1.52s ======================
```

---

## ☁️ Cloud Deployment Guide

### Option 1: Streamlit Community Cloud (Recommended & 100% Free)
1. Push your repository to GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Select your repository, branch (`main`), and set Main file path to `app.py`.
4. Under **Advanced Settings > Secrets**, paste your API keys:
   ```toml
   GEMINI_API_KEY = "your-api-key"
   GROQ_API_KEY = "your-api-key"
   ```
5. Click **Deploy!** Your app is live with a public HTTPS URL.

### Option 2: Hugging Face Spaces (Free)
1. Create a new Space on [huggingface.co/spaces](https://huggingface.co/spaces) and select the **Streamlit** SDK.
2. Upload the files or push via git.
3. Add your `GEMINI_API_KEY` under Space Settings > Secrets.

### Option 3: AWS / Render / Docker
A production `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 🎓 Viva & Project Presentation Guide

### Why is this project suitable for a Final Year CS / AI Degree?
1. **Solves Real-World Production Challenges**: Traditional RAG pipelines fail on tabular math. This project implements code generation, which is the industry standard (used by ChatGPT Advanced Data Analysis).
2. **Defensive Cybersecurity**: Prevents Remote Code Execution (RCE) via pre-runtime Abstract Syntax Tree (AST) validation.
3. **Agentic Self-Correction**: Implements an autonomous retry cycle that parses Python tracebacks, constructs diagnostic prompts, and repairs code dynamically.
4. **Data Science Integrity**: Includes automated Exploratory Data Analysis (EDA), Data Health Scoring, Pearson correlation heatmaps, and DuckDB in-memory SQL querying.

### Quick Q&A for Viva Defense:
- **Q: How does the system prevent LLMs from hallucinating column names?**
  *A: The `SchemaExtractor` dynamically passes exact column names, data types, and the top 5 unique values for categorical columns in the prompt.*
- **Q: How is security handled when using `exec()`?**
  *A: The `CodeSandbox` parses the code into an AST using Python's `ast` module. Any node attempting to import or call blacklisted modules (`os`, `sys`, `subprocess`, `open`, `eval`) is aborted before `exec()` is ever reached.*
- **Q: How does self-healing work?**
  *A: When Python raises an exception (`KeyError`, `ValueError`, etc.), the sandbox catches it, packages the error type and message into a `SELF_HEALING_PROMPT`, and asks the LLM to fix the code. This repeats up to 3 times.*

---

## 📚 Academic Deliverables (Synopsis, SRS & Presentation)

Comprehensive academic documentation has been generated in the [`docs/`](file:///d:/data%20analysis%20assistant/docs/) directory:

| Document | Format | Description | File Link |
|---|---|---|---|
| **Project Synopsis** | Markdown / Print | University-format project synopsis with problem statement, objectives, architecture, feasibility, and comparative tables. | [`docs/PROJECT_SYNOPSIS.md`](file:///d:/data%20analysis%20assistant/docs/PROJECT_SYNOPSIS.md) |
| **SRS Document** | Markdown / IEEE 830 | Complete IEEE 830 compliant Software Requirements Specification with DFD Level 0/1, Sequence, and Use-Case diagrams. | [`docs/SRS_DOCUMENT.md`](file:///d:/data%20analysis%20assistant/docs/SRS_DOCUMENT.md) |
| **PowerPoint Deck** | Microsoft PowerPoint (`.pptx`) | 16:9 widescreen presentation deck with dark executive theme, structured cards, and visual layout. | [`docs/project_presentation.pptx`](file:///d:/data%20analysis%20assistant/docs/project_presentation.pptx) |
| **Speaker Notes & Slides** | Markdown | Full 16-slide presentation script with word-for-word viva speaker notes. | [`docs/PRESENTATION_SLIDES.md`](file:///d:/data%20analysis%20assistant/docs/PRESENTATION_SLIDES.md) |
| **Interactive HTML Deck** | Web Browser (`.html`) | Modern presentation slide deck with arrow navigation, progress bar, fullscreen mode, and speaker notes panel. | [`docs/presentation_deck.html`](file:///d:/data%20analysis%20assistant/docs/presentation_deck.html) |

---

## 📜 License
This project is licensed under the MIT License — feel free to use and extend it for academic, research, and commercial purposes.
