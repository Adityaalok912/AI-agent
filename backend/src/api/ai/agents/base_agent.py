# backend/app/agents/base_agent.py
from dataclasses import dataclass
from typing import Optional
import abc
import logging
from api.ai.core.utils import get_logger
from api.ai.agents.llm_client import LLMClient

logger = get_logger("base_agent")


@dataclass
class AgentResult:
    agent_name: str
    content: str


class BaseAgent(abc.ABC):
    """
    BaseAgent defines a consistent interface for all role agents.

    - name: agent identifier
    - llm: optional LLMClient injected for text generation
    """

    def __init__(self, name: str, llm: Optional[LLMClient] = None):
        self.name = name
        self.llm = llm
        self._logger = get_logger(f"agent:{self.name}")

    async def _generate(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Use injected LLM if present, else fallback to deterministic response.
        """
        if self.llm:
            try:
                self._logger.debug("Calling LLM for generation")
                return await self.llm.generate(prompt=prompt, system=system)
            except Exception as e:
                self._logger.exception("LLM generation failed, falling back to deterministic logic: %s", e)
                # continue to fallback below
        # fallback deterministic behavior
        return self.fallback(prompt)

    @abc.abstractmethod
    async def run(self, input_text: str) -> AgentResult:
        """
        Must be implemented by concrete agents. Should return AgentResult.
        """
        raise NotImplementedError

    def fallback(self, input_text: str) -> str:
        """Default fallback: simple templated response. Override in subclass if needed."""
        return f"{self.name} processed input: {input_text}"
