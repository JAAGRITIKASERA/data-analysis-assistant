"""
Base abstract class for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseLLMProvider(ABC):
    """
    Abstract Interface for all LLM inference endpoints.
    Ensures uniform code generation behavior across Gemini, OpenAI, Claude, Groq, and Ollama.
    """

    def __init__(self, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the user-friendly name of the provider."""
        pass

    @abstractmethod
    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.1
    ) -> str:
        """
        Generates text completion from the LLM given system instructions and user request.
        """
        pass
