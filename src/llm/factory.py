"""
LLM Provider Factory to instantiate the appropriate AI engine.
"""

from typing import Optional
from src.llm.anthropic_provider import AnthropicProvider
from src.llm.gemini_provider import GeminiProvider
from src.llm.groq_provider import GroqProvider
from src.llm.mock_provider import MockProvider
from src.llm.ollama_provider import OllamaProvider
from src.llm.openai_provider import OpenAIProvider
from src.llm.provider_base import BaseLLMProvider


class LLMFactory:
    """Factory creating LLM client instances."""

    @staticmethod
    def get_provider(
        provider_name: str,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> BaseLLMProvider:
        """
        Returns configured LLM provider instance based on user selection.
        """
        p_name = provider_name.strip()

        if "Gemini" in p_name:
            return GeminiProvider(model_name=model_name, api_key=api_key)

        elif "Groq" in p_name:
            return GroqProvider(model_name=model_name, api_key=api_key)

        elif "OpenAI" in p_name:
            return OpenAIProvider(model_name=model_name, api_key=api_key, base_url=base_url)

        elif "Anthropic" in p_name or "Claude" in p_name:
            return AnthropicProvider(model_name=model_name, api_key=api_key)

        elif "Ollama" in p_name:
            return OllamaProvider(model_name=model_name, base_url=base_url)

        elif "Demo" in p_name or "Offline" in p_name:
            return MockProvider(model_name=model_name)

        else:
            # Fallback to OpenAI compatible or Mock
            if api_key:
                return OpenAIProvider(model_name=model_name, api_key=api_key, base_url=base_url)
            return MockProvider(model_name=model_name)
