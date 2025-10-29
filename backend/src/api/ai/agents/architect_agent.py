# backend/app/agents/architect_agent.py
from api.ai.agents.base_agent import BaseAgent, AgentResult

class ArchitectAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__("Architect", llm=llm)

    async def run(self, prd_text: str) -> AgentResult:
        system = "You are a system architect. Produce a concise architecture diagram description, component list, and data flow."
        prompt = (
            "Product requirements:\n"
            f"{prd_text}\n\n"
            "Return:\n- High-level components\n- Data flow between components\n- Tech stack recommendations (brief)\n"
        )
        out = await self._generate(prompt, system=system)
        return AgentResult(agent_name=self.name, content=out)
