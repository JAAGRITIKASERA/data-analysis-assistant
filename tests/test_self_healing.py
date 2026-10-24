"""
Unit tests for Self-Healing Loop and Mock Provider.
"""

import pandas as pd
from src.engine.self_healing import SelfHealingEngine
from src.llm.mock_provider import MockProvider
from src.llm.provider_base import BaseLLMProvider


class FailingThenSucceedingMockProvider(BaseLLMProvider):
    """Simulates an LLM that makes a KeyError on attempt 1, and heals on attempt 2."""

    def __init__(self):
        super().__init__(model_name="test-healer")
        self.call_count = 0

    @property
    def provider_name(self) -> str:
        return "TestHealer"

    def generate_response(self, system_prompt, user_prompt, conversation_history=None, temperature=0.1):
        self.call_count += 1
        if self.call_count == 1:
            # First attempt fails with KeyError: 'InvalidCol'
            return """```python
result = df["InvalidCol"].sum()
```
Attempting sum of InvalidCol."""
        else:
            # Second attempt fixes the column name
            return """```python
result = df["Sales"].sum()
```
Fixed: calculated sum of Sales."""


def test_self_healing_recovers_from_error():
    df = pd.DataFrame({"Sales": [10, 20, 30]})
    provider = FailingThenSucceedingMockProvider()

    res = SelfHealingEngine.run_pandas_pipeline(
        provider=provider,
        df=df,
        user_question="What is total sales?",
        max_retries=3
    )

    assert res.success is True
    assert res.healed is True
    assert res.total_attempts == 2
    assert res.final_result.data == 60


def test_mock_provider_generates_functional_code():
    df = pd.DataFrame({
        "Region": ["North", "South"],
        "Sales": [100, 200]
    })
    mock = MockProvider()
    response = mock.generate_response(
        system_prompt="| `Region` | `object` |\n| `Sales` | `int64` |",
        user_prompt="Show total sales by region as a bar chart"
    )

    assert "```python" in response
    assert "Region" in response
    assert "Sales" in response
