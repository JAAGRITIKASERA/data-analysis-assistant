"""
Autonomous Self-Healing Agent Loop.
Executes code in the sandbox, intercepts runtime errors (KeyError, TypeError, SyntaxError),
and autonomously prompts the LLM to inspect the traceback and self-correct until resolved.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import pandas as pd

from src.config import (
    MAX_SELF_HEALING_RETRIES,
    PANDAS_SYSTEM_PROMPT,
    SELF_HEALING_PROMPT,
    SQL_SYSTEM_PROMPT
)
from src.engine.sandbox import CodeSandbox, ExecutionResult
from src.engine.schema import SchemaExtractor
from src.engine.sql_engine import SQLEngine, SQLExecutionResult
from src.llm.provider_base import BaseLLMProvider


@dataclass
class HealingAttempt:
    """Stores telemetry for each execution attempt."""
    attempt_number: int
    raw_response: str
    code: str
    result: Any  # ExecutionResult or SQLExecutionResult
    success: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: float = 0.0


@dataclass
class AgentPipelineResponse:
    """Final unified response from the conversational agent pipeline."""
    success: bool
    final_result: Any  # ExecutionResult or SQLExecutionResult
    explanation: str
    total_attempts: int
    healed: bool
    history: List[HealingAttempt] = field(default_factory=list)
    total_time_ms: float = 0.0


class SelfHealingEngine:
    """
    Orchestrates the generate -> execute -> catch error -> heal -> re-execute pipeline.
    """

    @classmethod
    def run_pandas_pipeline(
        cls,
        provider: BaseLLMProvider,
        df: pd.DataFrame,
        user_question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        max_retries: int = MAX_SELF_HEALING_RETRIES,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> AgentPipelineResponse:
        """
        Runs the conversational code-generation loop with automatic error self-correction.
        """
        start_overall = time.perf_counter()
        schema_context = SchemaExtractor.generate_prompt_context(df)

        system_prompt = PANDAS_SYSTEM_PROMPT.format(schema_context=schema_context)
        current_user_prompt = user_question

        history: List[HealingAttempt] = []
        final_result: Optional[ExecutionResult] = None
        explanation = ""

        for attempt_idx in range(1, max_retries + 1):
            if status_callback:
                if attempt_idx == 1:
                    status_callback("🧠 Analyzing schema & synthesizing Python Pandas code...")
                else:
                    status_callback(f"🛠️ Self-Correction Cycle {attempt_idx}/{max_retries}: Repairing code based on execution error...")

            step_start = time.perf_counter()

            # 1. LLM Code Generation
            try:
                raw_response = provider.generate_response(
                    system_prompt=system_prompt,
                    user_prompt=current_user_prompt,
                    conversation_history=conversation_history,
                    temperature=0.1
                )
            except Exception as e:
                return AgentPipelineResponse(
                    success=False,
                    final_result=ExecutionResult(
                        success=False,
                        code="",
                        result_type="error",
                        error_type="LLMInferenceError",
                        error_message=str(e)
                    ),
                    explanation=f"LLM Inference Failure: {str(e)}",
                    total_attempts=attempt_idx,
                    healed=False,
                    history=history,
                    total_time_ms=round((time.perf_counter() - start_overall) * 1000.0, 2)
                )

            # 2. Extract explanation and clean code
            clean_code = CodeSandbox.extract_python_code(raw_response)
            
            # Extract analytical explanation text outside markdown blocks
            text_outside = []
            for block in raw_response.split("```"):
                if not block.strip().startswith("python") and not block.strip().startswith("py"):
                    cleaned_block = block.strip()
                    if cleaned_block:
                        text_outside.append(cleaned_block)
            explanation = "\n\n".join(text_outside) if text_outside else "Code executed successfully."

            # 3. Sandbox Execution
            if status_callback:
                status_callback(f"⚡ Sandboxing Python execution in isolated environment (Attempt {attempt_idx})...")

            exec_result = CodeSandbox.execute(clean_code, df)
            step_duration = round((time.perf_counter() - step_start) * 1000.0, 2)

            attempt = HealingAttempt(
                attempt_number=attempt_idx,
                raw_response=raw_response,
                code=clean_code,
                result=exec_result,
                success=exec_result.success,
                error_type=exec_result.error_type,
                error_message=exec_result.error_message,
                duration_ms=step_duration
            )
            history.append(attempt)
            final_result = exec_result

            # 4. Check if execution succeeded
            if exec_result.success:
                total_duration = round((time.perf_counter() - start_overall) * 1000.0, 2)
                return AgentPipelineResponse(
                    success=True,
                    final_result=exec_result,
                    explanation=explanation,
                    total_attempts=attempt_idx,
                    healed=(attempt_idx > 1),
                    history=history,
                    total_time_ms=total_duration
                )

            # 5. Build Healing Prompt for Next Iteration
            if attempt_idx < max_retries:
                current_user_prompt = SELF_HEALING_PROMPT.format(
                    failed_code=clean_code,
                    error_type=exec_result.error_type or "RuntimeError",
                    error_message=exec_result.error_message or "Unknown execution error",
                    schema_context=schema_context,
                    user_question=user_question
                )

        # Reached max retries without success
        total_duration = round((time.perf_counter() - start_overall) * 1000.0, 2)
        return AgentPipelineResponse(
            success=False,
            final_result=final_result,
            explanation=f"Execution failed after {max_retries} automatic correction attempts.",
            total_attempts=max_retries,
            healed=False,
            history=history,
            total_time_ms=total_duration
        )

    @classmethod
    def run_sql_pipeline(
        cls,
        provider: BaseLLMProvider,
        df: pd.DataFrame,
        user_question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        max_retries: int = 2,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> AgentPipelineResponse:
        """
        Executes Text-to-SQL query pipeline using DuckDB with validation and retry loop.
        """
        start_overall = time.perf_counter()
        schema_context = SchemaExtractor.generate_prompt_context(df)

        system_prompt = SQL_SYSTEM_PROMPT.format(schema_context=schema_context)
        current_user_prompt = user_question

        history: List[HealingAttempt] = []
        final_result: Optional[SQLExecutionResult] = None
        explanation = ""

        for attempt_idx in range(1, max_retries + 1):
            if status_callback:
                status_callback(f"🐬 Synthesizing ANSI SQL query via DuckDB (Attempt {attempt_idx})...")

            step_start = time.perf_counter()

            try:
                raw_response = provider.generate_response(
                    system_prompt=system_prompt,
                    user_prompt=current_user_prompt,
                    conversation_history=conversation_history,
                    temperature=0.0
                )
            except Exception as e:
                return AgentPipelineResponse(
                    success=False,
                    final_result=SQLExecutionResult(
                        success=False,
                        sql="",
                        error_type="LLMInferenceError",
                        error_message=str(e)
                    ),
                    explanation=f"LLM Error: {str(e)}",
                    total_attempts=attempt_idx,
                    healed=False,
                    history=history,
                    total_time_ms=round((time.perf_counter() - start_overall) * 1000.0, 2)
                )

            clean_sql = SQLEngine.extract_sql_query(raw_response)
            
            # Extract non-code explanation
            text_outside = []
            for block in raw_response.split("```"):
                if not block.strip().startswith("sql"):
                    cleaned = block.strip()
                    if cleaned:
                        text_outside.append(cleaned)
            explanation = "\n\n".join(text_outside) if text_outside else "SQL Query executed successfully."

            sql_result = SQLEngine.execute_query(clean_sql, df)
            step_duration = round((time.perf_counter() - step_start) * 1000.0, 2)

            attempt = HealingAttempt(
                attempt_number=attempt_idx,
                raw_response=raw_response,
                code=clean_sql,
                result=sql_result,
                success=sql_result.success,
                error_type=sql_result.error_type,
                error_message=sql_result.error_message,
                duration_ms=step_duration
            )
            history.append(attempt)
            final_result = sql_result

            if sql_result.success:
                total_duration = round((time.perf_counter() - start_overall) * 1000.0, 2)
                return AgentPipelineResponse(
                    success=True,
                    final_result=sql_result,
                    explanation=explanation,
                    total_attempts=attempt_idx,
                    healed=(attempt_idx > 1),
                    history=history,
                    total_time_ms=total_duration
                )

            # Retry with SQL error
            if attempt_idx < max_retries:
                current_user_prompt = f"""Your SQL query failed with error: {sql_result.error_message}
Failed SQL:
```sql
{clean_sql}
```
Table Schema:
{schema_context}

Please fix the SQL query and return ONLY the corrected ```sql ... ``` block."""

        total_duration = round((time.perf_counter() - start_overall) * 1000.0, 2)
        return AgentPipelineResponse(
            success=False,
            final_result=final_result,
            explanation=f"SQL query failed after {max_retries} attempts.",
            total_attempts=max_retries,
            healed=False,
            history=history,
            total_time_ms=total_duration
        )
