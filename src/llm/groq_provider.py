"""
Groq API Provider for ultra-fast, high-accuracy inference.
Runs Llama-3.3-70b-versatile with blazing speed.
"""

from typing import Dict, List, Optional
from src.llm.provider_base import BaseLLMProvider

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class GroqProvider(BaseLLMProvider):
    """Groq Cloud API provider using OpenAI-compatible SDK endpoint."""

    GROQ_BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(self, model_name: str = "llama-3.3-70b-versatile", api_key: Optional[str] = None):
        super().__init__(model_name=model_name, api_key=api_key, base_url=self.GROQ_BASE_URL)

    @property
    def provider_name(self) -> str:
        return "Groq"

    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.1
    ) -> str:
        if not OPENAI_AVAILABLE:
            raise RuntimeError("The 'openai' package is required for Groq. Run `pip install openai`.")

        if not self.api_key:
            raise ValueError("Groq API key is required. Free keys are available at https://console.groq.com/keys")

        client = openai.OpenAI(api_key=self.api_key, base_url=self.GROQ_BASE_URL)

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
