# backend/app/agents/engineer_agent.py
from api.ai.agents.base_agent import BaseAgent, AgentResult

class EngineerAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__("Engineer", llm=llm)

    async def run(self, task_list_text: str) -> AgentResult:
        system = "You are a software engineer. Produce starter code, file structure, and short README for the tasks."
        prompt = (
            "Task list / plan:\n"
            f"{task_list_text}\n\n"
            "Produce:\n- A minimal file tree\n- core code files (only include short, runnable snippets)\n- steps to run locally\n"
        )
        out = await self._generate(prompt, system=system)
        return AgentResult(agent_name=self.name, content=out)
