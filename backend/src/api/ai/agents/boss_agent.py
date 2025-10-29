# backend/app/agents/boss_agent.py
from api.ai.agents.base_agent import BaseAgent, AgentResult
from typing import Optional

class BossAgent(BaseAgent):
    def __init__(self, llm: Optional[object] = None):
        super().__init__("Boss", llm=llm)

    async def run(self, input_text: str) -> AgentResult:
        """
        Transform raw user prompt into a structured project brief / goal.
        Use a short system prompt to tell the LLM the role.
        """
        system = "You are the Project Boss. Read a user idea and produce a concise project goal and high-level scope."
        prompt = (
            "User idea:\n"
            f"{input_text}\n\n"
            "Produce:\n- 1-2 sentence goal\n- key success criteria (3 bullets)\n- primary constraints (if any)\n"
        )
        out = await self._generate(prompt, system=system)
        return AgentResult(agent_name=self.name, content=out)
