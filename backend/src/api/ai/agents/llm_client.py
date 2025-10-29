"""
Simple abstracted LLM client interface with a minimal implementation for Gemini API.
Export LLMClient class with method: async generate(prompt: str, system: str | None = None) -> str

Supports:
- Gemini (production default)
- Mock (for local/dev)
- OpenAI (commented out example)
"""

from typing import Optional, Dict, Any
import abc
import asyncio
import os
from api.ai.core.utils import get_logger

logger = get_logger("llm_client")


class LLMClient(abc.ABC):
    """Abstract base class for LLM providers."""

    @abc.abstractmethod
    async def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        raise NotImplementedError


# ============================
# ✅ MOCK CLIENT (for testing)
# ============================
class MockLLMClient(LLMClient):
    async def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        await asyncio.sleep(0.05)
        return f"[MOCK LLM RESPONSE] system={system or 'none'} prompt_summary={prompt[:200]}"


# =======================================
# ✅ GEMINI CLIENT (Production Default)
# =======================================
class OpenAIClient(LLMClient):
    """
    Async Gemini API client using google-generativeai SDK.
    Make sure to install:
        pip install google-generativeai
    And set:
        export GEMINI_API_KEY="your_api_key"
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        import google.generativeai as genai

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GEMINI_API_KEY environment variable or provided api_key")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        logger.info(f"GeminiClient initialized with model: {model}")

    async def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        """
        Generate content using Gemini asynchronously.
        Wraps blocking SDK calls in executor for non-blocking behavior.
        """
        loop = asyncio.get_event_loop()

        def _call() -> str:
            sys_prefix = f"System: {system}\n\n" if system else ""
            full_prompt = f"{sys_prefix}{prompt}"
            try:
                response = self.model.generate_content(full_prompt)
                return response.text or "[Empty Gemini response]"
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                return f"[ERROR] Gemini API failed: {str(e)}"

        return await loop.run_in_executor(None, _call)


# =======================================================
# ❌ COMMENTED OUT: OPENAI CLIENT (LEGACY / OPTIONAL USE)
# =======================================================
"""
class OpenAIClient(LLMClient):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        import openai
        self._openai = openai
        self._openai.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

    async def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        loop = asyncio.get_event_loop()

        def _call():
            msgs = []
            if system:
                msgs.append({"role": "system", "content": system})
            msgs.append({"role": "user", "content": prompt})
            resp = self._openai.ChatCompletion.create(model=self.model, messages=msgs, **kwargs)
            return resp["choices"][0]["message"]["content"]

        return await loop.run_in_executor(None, _call)
"""

# ============================
# Factory helper
# ============================
def get_llm_client(provider: str = "gemini") -> LLMClient:
    """
    Helper to select the correct LLM provider.
    provider: "gemini" | "mock" | "openai"
    """
    if provider == "mock":
        return MockLLMClient()
    elif provider == "gemini":
        return GeminiClient()
    # elif provider == "openai":
    #     return OpenAIClient()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
