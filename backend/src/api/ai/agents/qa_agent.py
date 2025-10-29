# backend/app/agents/qa_agent.py
from api.ai.agents.base_agent import BaseAgent, AgentResult

class QAAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__("QA", llm=llm)

    async def run(self, engineer_output: str) -> AgentResult:
        system = "You are a QA engineer. Review the engineer output, suggest tests, and produce a short QA report with risks and fixes."
        prompt = (
            "Implementation output / code snippets:\n"
            f"{engineer_output}\n\n"
            "Return:\n- Quick QA checklist\n- Suggested unit/e2e tests (code outline)\n- Risks and recommended fixes\n"
        )
        out = await self._generate(prompt, system=system)
        return AgentResult(agent_name=self.name, content=out)
