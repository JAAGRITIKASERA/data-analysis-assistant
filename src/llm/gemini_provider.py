"""
Google Gemini provider using official google-genai SDK.
Supports gemini-2.5-flash, gemini-1.5-pro, gemini-1.5-flash.
"""

from typing import Dict, List, Optional
from src.llm.provider_base import BaseLLMProvider

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM inference provider."""

    @property
    def provider_name(self) -> str:
        return "Google Gemini"

    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.1
    ) -> str:
        if not GEMINI_AVAILABLE:
            raise RuntimeError("The 'google-genai' package is not installed. Run `pip install google-genai`.")

        if not self.api_key:
            raise ValueError("Google Gemini API key is required. Please set GEMINI_API_KEY or provide it in the sidebar.")

        client = genai.Client(api_key=self.api_key)

        # Build contents incorporating conversation history if available
        contents = []
        if conversation_history:
            for msg in conversation_history[-6:]:  # Keep recent context
                role = "user" if msg.get("role") == "user" else "model"
                contents.append(f"{role.upper()}: {msg.get('content', '')}")

        contents.append(f"USER: {user_prompt}")
        full_content = "\n\n".join(contents)

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
        )

        model_to_use = self.model_name
        # Auto-map deprecated versions to newest gemini-3.8-flash
        if "gemini-2.5" in model_to_use:
            model_to_use = "gemini-3.8-flash"

        try:
            response = client.models.generate_content(
                model=model_to_use,
                contents=full_content,
                config=config,
            )
            return response.text or ""
        except Exception as e:
            err_str = str(e)
            # If 404 or model unavailable, attempt fallback to gemini-3.8-flash or gemini-1.5-flash
            if ("404" in err_str or "NOT_FOUND" in err_str or "no longer available" in err_str) and model_to_use != "gemini-3.8-flash":
                try:
                    fallback_response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=full_content,
                        config=config,
                    )
                    return fallback_response.text or ""
                except Exception:
                    # Try gemini-1.5-flash as secondary fallback
                    fallback_response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=full_content,
                        config=config,
                    )
                    return fallback_response.text or ""
            raise e

