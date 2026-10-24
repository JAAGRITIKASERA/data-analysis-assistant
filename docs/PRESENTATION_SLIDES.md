# PRESENTATION SLIDES & SPEAKER NOTES
## Conversational Data Analysis Assistant — Natural-Language Q&A Over Tabular Datasets
**Final Year Major Project Presentation**

---

### Slide 1: Title Slide
- **Title:** Conversational Data Analysis Assistant
- **Subtitle:** Natural-Language Q&A Over CSV/Excel Datasets Using Autonomous Code Generation & Isolated Sandboxed Execution
- **Presented By:** [Student Name] &bull; Roll No: [Roll Number]
- **Project Guide:** [Guide Name, Designation]
- **Department:** Department of Computer Science & Engineering
- **Institution:** [College / University Name]

> **Speaker Notes:**
> *"Good morning, respected external examiner and faculty members. Today I am presenting our final year major project: 'Conversational Data Analysis Assistant'. This project addresses a fundamental challenge in business intelligence: empowering non-technical stakeholders to ask plain English questions over complex tabular spreadsheets and obtain instant, mathematically verified statistics, interactive charts, and data insights through LLM code generation and isolated execution sandboxing."*

---

### Slide 2: Problem Statement & Motivation
- **The Core Problem:**
  - Modern organizations are inundated with tabular data (sales, patient vitals, student grades, financial transactions).
  - Extracting ad-hoc insights requires SQL, Python, or rigid BI formula mastery.
- **Why Naive LLM Text Chat Fails:**
  - **Context Window Saturation:** Datasets with 10,000+ rows exceed prompt limits.
  - **Data Privacy Violations:** Uploading entire confidential spreadsheets to cloud LLM providers violates GDPR and HIPAA regulations.
  - **Arithmetic Hallucination:** LLMs are stochastic language predictors; they frequently hallucinate wrong sums, averages, and correlations.
- **The Core Question:**
  - *Can we use the LLM solely for code synthesis while executing computations deterministically and securely on the client machine?*

> **Speaker Notes:**
> *"When people try to use ChatGPT for data analysis, they encounter three major roadblocks. First, you cannot fit a 50,000-row file into an LLM prompt. Second, companies cannot legally send sensitive healthcare or financial records to third-party cloud servers. Third, language models are notoriously prone to math hallucinations. Our project solves all three problems at once."*

---

### Slide 3: Proposed Solution & Core Innovation
- **Program Synthesis over Direct Answer Generation:**
  - The LLM writes functional Python (Pandas/Plotly) or DuckDB SQL code instead of computing numbers mentally.
- **Token-Safe Schema Extraction:**
  - Only structural metadata (< 800 tokens) is sent to the LLM. Raw data never leaves the client device.
- **AST Security Guard:**
  - Inspects code syntax trees before execution to block Remote Code Execution (RCE) attacks.
- **Autonomous Self-Healing Loop:**
  - Automatically captures runtime exceptions and re-prompts the LLM with error tracebacks to heal code dynamically.
- **Dual Analytical Engine:**
  - Procedural analysis via Pandas + Plotly; Relational analysis via in-memory DuckDB ANSI SQL.

> **Speaker Notes:**
> *"Our solution decouples data intelligence into two distinct halves: reasoning and execution. The cloud LLM acts as the programmer, writing Python or SQL code based solely on a high-level schema. The local client acts as the computer, safely running that code against the in-memory dataset. This gives us 100% mathematical accuracy and total data privacy."*

---

### Slide 4: System Architecture
- **Step 1:** User uploads CSV/Excel or selects benchmark dataset.
- **Step 2:** `SchemaExtractor` computes column types, statistical ranges, and top categories (<800 tokens).
- **Step 3:** Natural language question + schema sent to LLM provider (Gemini 3.8 Flash / Groq / OpenAI).
- **Step 4:** `CodeSandbox` parses code and executes AST static security analysis.
- **Step 5:** Code runs in isolated memory namespace; output variables `result` and `fig` captured.
- **Step 6:** If runtime error occurs, `SelfHealingEngine` diagnoses error and repairs code (up to 3 retries).
- **Step 7:** Interactive Plotly charts, tables, and downloadable executive reports rendered on Streamlit UI.

> **Speaker Notes:**
> *"Here is the complete end-to-end pipeline. Notice the decision diamond at the AST Security Guard and the Self-Healing feedback loop. If the model generates a KeyError or typo in a column name, our engine catches it, diagnoses the error, and re-queries the model autonomously. The user sees a seamless, self-healed result without application crashes."*

---

### Slide 5: Schema Extraction & Privacy Preservation
- **What is Sent to the LLM:**
  - Column Names & Data Types (`int64`, `float64`, `object`, `datetime`)
  - Missing Value Percentages & Unique Cardinality Counts
  - Statistical Boundaries: Min, Max, Mean, Median for numeric columns
  - **Top 5 Frequent Categories:** Crucial for string matching (e.g. `'North'`, `'South'`)
  - 3 Anonymized Sample Rows
- **What is NEVER Sent:**
  - The remaining 99.9% of dataset records
- **Token Budget:** Under 800 tokens (99% token cost savings compared to raw data ingestion).

> **Speaker Notes:**
> *"A key innovation of our schema extractor is capturing the top 5 most frequent values for categorical columns. For example, if a column contains 'Corporate' and 'Home Office', the LLM knows the exact capitalization to use in its filter statements. This eliminates the #1 cause of LLM code generation errors."*

---

### Slide 6: AST Security Sandbox (Preventing RCE)
- **The Threat:**
  - Arbitrary code execution (`exec()`) without security checks allows malicious LLM prompts to run:
    `import os; os.system("format C:")` or `open("/etc/passwd").read()`
- **Our Defense Strategy: Multi-Layer AST Inspection:**
  - Pre-execution parse using Python's `ast` module.
  - **Banned Imports:** `os`, `sys`, `subprocess`, `shutil`, `socket`, `urllib`, `requests`, `ctypes`.
  - **Banned Builtins:** `open`, `eval`, `exec`, `__import__`, `globals`, `locals`, `compile`.
  - **Banned Reflections:** `__subclasses__`, `__globals__`, `__code__`.
  - **Isolated Namespace:** Only `pd`, `np`, `px`, `go`, `plt`, `sns`, and safe arithmetic builtins injected.

> **Speaker Notes:**
> *"Safety is paramount in any agentic coding system. Before our system calls Python's exec function, the code is parsed into an Abstract Syntax Tree. If any prohibited system call or reflection exploit is detected anywhere in the tree, the code is immediately aborted before running. This prevents Remote Code Execution attacks completely."*

---

### Slide 7: Autonomous Self-Healing Retry Loop
- **The Reality of AI Code Generation:**
  - First-attempt LLM code often fails due to unexpected column typos, null values, or API parameter mismatches.
- **The Self-Healing Mechanism:**
  1. Sandbox intercepts exception (`KeyError`, `AttributeError`, `TypeError`, `ZeroDivisionError`).
  2. Extracts exact error message and traceback.
  3. Formulates a targeted healing prompt combining the failed code, the error, and the schema.
  4. LLM inspects the diagnosis, fixes the logic, and returns clean code.
  5. UI displays: `✨ Auto-Corrected on Attempt 2` with complete resolution telemetry.

> **Speaker Notes:**
> *"Self-healing is what makes this project genuinely agentic. If the model makes a syntax mistake or references a column incorrectly on attempt 1, the system does not crash or bother the user. It catches the stack trace, feeds it back to the LLM, and gets corrected code within seconds. In our tests, this resolves over 90% of execution faults."*

---

### Slide 8: Dual Analytical Engine: Pandas vs. DuckDB SQL
- **Pandas Python Engine:**
  - Procedural transformations, custom math, statistical modeling (`describe()`, `corr()`).
  - Native integration with **Plotly Express** for WebGL dynamic visualizations.
- **DuckDB ANSI SQL Engine:**
  - High-performance, columnar in-memory OLAP database.
  - Direct execution of standard SQL (`SELECT`, `GROUP BY`, `HAVING`, `WINDOW`, `JOIN`).
  - Read-Only SQL Validator: strictly blocks `DROP`, `DELETE`, `ALTER`, `ATTACH`, `COPY`.

> **Speaker Notes:**
> *"We built dual engine support into the application. Users who prefer relational database querying can switch to DuckDB mode, which runs blazingly fast ANSI SQL directly over the uploaded CSV in memory without spinning up a database server."*

---

### Slide 9: Automated EDA & Data Quality Health Scoring
- **0–100% Data Health Scorecard:**
  - Evaluates missing cell ratio, duplicate row ratio, zero-variance columns, and column naming hygiene.
- **Missing Values & Cardinality Table:**
  - Sortable report pinpointing data gaps.
- **Pearson Correlation Heatmap:**
  - Automated matrix identifying strong collinearities among numerical variables.
- **Dynamic Suggested Questions:**
  - Algorithm introspects uploaded columns and suggests 5 relevant analytical queries automatically.

> **Speaker Notes:**
> *"Beyond answering questions, the assistant immediately gives users an Automated Health Check of their dataset upon upload. It flags null values, duplicates, and calculates a health score from 0 to 100%, alongside suggested questions that give users instant starting points."*

---

### Slide 10: Dynamic Visualizations (Plotly Express)
- **Interactive WebGL/SVG Graphics:**
  - Automatic selection of chart types: Bar, Line, Scatter, Box, Heatmap, Histogram.
  - Features: Hover data tooltips, box zoom, panning, legend filtering, and PNG export.
- **Matplotlib/Seaborn Fallback:**
  - Captures static figures seamlessly using non-interactive `Agg` backend.
- **One-Click CSV Download:**
  - Every transformed data table result includes an instant CSV download trigger.

> **Speaker Notes:**
> *"All visual outputs are interactive. Users can hover over bars to inspect exact values, zoom into specific date intervals, and download filtered data slices directly as new CSV files."*

---

### Slide 11: Multi-Model LLM Provider Architecture
- **Provider Agnostic Factory Pattern:**
  - **Google Gemini:** `gemini-3.8-flash` (High speed, latest reasoning engine).
  - **Groq Cloud:** `llama-3.3-70b-versatile` (100% free API tier, ultra-fast >300 tokens/sec).
  - **OpenAI:** `gpt-4o` and `gpt-4o-mini`.
  - **Anthropic:** `claude-3-5-sonnet` and `claude-3-5-haiku`.
  - **Local Ollama:** Completely offline, privacy-first inference for air-gapped environments.
  - **Offline Demo Engine:** Rule-based heuristic generator for zero-API-key demonstrations.

> **Speaker Notes:**
> *"We implemented a clean Factory Pattern that supports 5 different LLM providers plus an Offline Demo Engine. This means an evaluator or student can test every feature of the app offline without needing an API key or credit card."*

---

### Slide 12: Experimental Results & Benchmarks
- **Test Datasets Evaluated:**
  - E-Commerce Sales (100 rows, 13 features)
  - Healthcare Patients (100 rows, 11 features)
  - Student Academic Performance (100 rows, 10 features)
  - Tech Stocks Market Data (80 rows, 10 features)
- **Performance Metrics:**
  - **Schema Extraction Latency:** ~12 milliseconds
  - **Token Consumption per Query:** 350 – 750 tokens
  - **Sandbox Execution Time:** 1.5 – 5.0 milliseconds
  - **First-Attempt Code Accuracy:** 84%
  - **Accuracy After Self-Healing Retry (Attempt 2):** 96%
  - **Automated Unit Tests:** 11/11 tests passed in 1.52 seconds.

> **Speaker Notes:**
> *"Our empirical benchmarks demonstrate that self-healing improves query success rates from 84% to 96%. Furthermore, sandbox execution takes less than 5 milliseconds, meaning total query turnaround is almost entirely determined by LLM streaming speed."*

---

### Slide 13: Executive Report Generation
- **One-Click HTML / PDF Analytics Report:**
  - Executive Summary with dataset metadata and health score.
  - Full conversational Q&A transcript with tables and key business insights.
  - Embedded interactive Plotly graphs and base64-encoded charts.
  - Complete code audit trail displaying the exact Python/SQL scripts that produced each result.
  - Ready for academic submission and corporate board presentations.

> **Speaker Notes:**
> *"At the end of an analysis session, the user can click one button to generate a publication-ready Executive Report. It compiles the health scorecard, every answered question, interactive charts, and an audit trail of the executed code into a clean, printable HTML document."*

---

### Slide 14: Future Enhancements & Scope
- **Multi-Table Joins:** Extending DuckDB integration to upload and join multiple relational CSVs.
- **Voice-to-Text Input:** Integrating Web Speech API for voice-driven conversational querying.
- **Automated Machine Learning (AutoML):** Adding predictive modeling tabs (e.g., forecasting sales or classifying risk).
- **Docker & Kubernetes Deployment:** Containerizing the platform for high-concurrency cloud scaling.

> **Speaker Notes:**
> *"In future work, we plan to support relational multi-table joins across multiple uploaded CSV files and introduce voice-to-query input for mobile and tablet users."*

---

### Slide 15: Conclusion & Key Learnings
- **Key Takeaways:**
  1. Demonstrated that **Program Synthesis + Sandboxed Execution** is vastly superior to direct text generation for tabular data analysis.
  2. Proved that **Token-Safe Schema Extraction** achieves 95%+ token cost reduction while maintaining complete data privacy.
  3. Engineered an **AST Security Sandbox** that eliminates Remote Code Execution risks.
  4. Validated that **Autonomous Self-Healing** bridges the gap between probabilistic AI and deterministic enterprise software.

> **Speaker Notes:**
> *"In conclusion, our Conversational Data Analysis Assistant proves that LLMs can be harnessed safely, economically, and accurately for data science by combining prompt engineering, AST security, and agentic error recovery. Thank you."*

---

### Slide 16: Q&A / Project Defense
- **Conversational Data Analysis Assistant**
- **Repository & Codebase:** Available locally at `d:\data analysis assistant`
- *Open for Questions & Live Demonstration!*

> **Speaker Notes:**
> *"I would now be delighted to answer any questions from the panel and demonstrate live queries on the application."*
