# backend/app/agents/product_manager_agent.py
from api.ai.agents.base_agent import BaseAgent, AgentResult
from typing import Optional

class ProductManagerAgent(BaseAgent):
    def __init__(self, llm: Optional[object] = None):
        super().__init__("Product Manager", llm=llm)

    async def run(self, boss_output: str) -> AgentResult:
        system = "You are a Product Manager. Convert a project brief into a short PRD (scope, features, non-goals, success metrics)."
        prompt = (
            "Project brief (from Boss):\n"
            f"{boss_output}\n\n"
            "Return a small PRD containing:\n- Objective\n- Key features (bullet list)\n- Non-goals\n- Acceptance criteria / success metrics\n"
        )
        out = await self._generate(prompt, system=system)
        return AgentResult(agent_name=self.name, content=out)
