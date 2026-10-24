"""
OpenAI LLM provider using the modern openai Python SDK.
Supports GPT-4o, GPT-4o-mini, o3-mini.
"""

from typing import Dict, List, Optional
from src.llm.provider_base import BaseLLMProvider

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API Provider."""

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.1
    ) -> str:
        if not OPENAI_AVAILABLE:
            raise RuntimeError("The 'openai' package is not installed. Run `pip install openai`.")

        if not self.api_key:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY or provide it in the sidebar.")

        client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            for msg in conversation_history[-6:]:
                role = "assistant" if msg.get("role") in ["assistant", "model"] else "user"
                messages.append({"role": role, "content": msg.get("content", "")})

        messages.append({"role": "user", "content": user_prompt})

        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
        )

        return response.choices[0].message.content or ""
