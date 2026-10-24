"""
Local Ollama Provider for offline, self-hosted, and privacy-preserving inference.
Works with any model installed via Ollama (e.g. llama3, mistral, deepseek-coder).
"""

from typing import Dict, List, Optional
import requests
from src.llm.provider_base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Local Ollama REST API provider."""

    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(self, model_name: str = "llama3", base_url: Optional[str] = None):
        url = base_url or self.DEFAULT_BASE_URL
        super().__init__(model_name=model_name, api_key=None, base_url=url)

    @property
    def provider_name(self) -> str:
        return "Ollama Local"

    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.1
    ) -> str:
        endpoint = f"{self.base_url.rstrip('/')}/api/chat"

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            for msg in conversation_history[-6:]:
                role = "assistant" if msg.get("role") in ["assistant", "model"] else "user"
                messages.append({"role": role, "content": msg.get("content", "")})

        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature}
        }

        try:
            resp = requests.post(endpoint, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Could not connect to Ollama at {self.base_url}. Ensure Ollama is running (`ollama serve`)."
            )
        except Exception as e:
            raise RuntimeError(f"Ollama request error: {str(e)}")
