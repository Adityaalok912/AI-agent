# backend/app/agents/project_manager_agent.py
from api.ai.agents.base_agent import BaseAgent, AgentResult

class ProjectManagerAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__("Project Manager", llm=llm)

    async def run(self, architecture_text: str) -> AgentResult:
        system = "You are a Project Manager. Convert architecture into an actionable task list with estimates."
        prompt = (
            "Architecture summary:\n"
            f"{architecture_text}\n\n"
            "Return a task breakdown (epics -> tasks) with rough estimates and priority ordering.\n"
        )
        out = await self._generate(prompt, system=system)
        return AgentResult(agent_name=self.name, content=out)
