"""
Anthropic Claude API Provider using the anthropic SDK.
Supports Claude 3.5 Sonnet and Claude 3.5 Haiku.
"""

from typing import Dict, List, Optional
from src.llm.provider_base import BaseLLMProvider

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude inference provider."""

    @property
    def provider_name(self) -> str:
        return "Anthropic Claude"

    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.1
    ) -> str:
        if not ANTHROPIC_AVAILABLE:
            raise RuntimeError("The 'anthropic' package is not installed. Run `pip install anthropic`.")

        if not self.api_key:
            raise ValueError("Anthropic API key is required. Please set ANTHROPIC_API_KEY or provide it in the sidebar.")

        client = anthropic.Anthropic(api_key=self.api_key)

        messages = []
        if conversation_history:
            for msg in conversation_history[-6:]:
                role = "assistant" if msg.get("role") in ["assistant", "model"] else "user"
                messages.append({"role": role, "content": msg.get("content", "")})

        messages.append({"role": "user", "content": user_prompt})

        response = client.messages.create(
            model=self.model_name,
            system=system_prompt,
            messages=messages,
            max_tokens=2048,
            temperature=temperature,
        )

        # Extract text content
        text_blocks = [b.text for b in response.content if hasattr(b, "text")]
        return "\n".join(text_blocks)
