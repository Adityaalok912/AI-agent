import pytest
from api.ai.agents.llm_client import MockLLMClient
from api.ai.agents.boss_agent import BossAgent
from api.ai.agents.product_manager_agent import ProductManagerAgent
from api.ai.agents.architect_agent import ArchitectAgent
from api.ai.agents.project_manager_agent import ProjectManagerAgent
from api.ai.agents.engineer_agent import EngineerAgent
from api.ai.agents.qa_agent import QAAgent


@pytest.mark.asyncio
async def test_boss_agent():
    llm = MockLLMClient()
    agent = BossAgent(llm=llm)
    res = await agent.run("Build a notes app")
    assert res.agent_name == "Boss"
    assert "MOCK LLM RESPONSE" in res.content


@pytest.mark.asyncio
async def test_pm_agent():
    llm = MockLLMClient()
    agent = ProductManagerAgent(llm=llm)
    res = await agent.run("Goal: notes app")
    assert res.agent_name.startswith("Product Manager")


@pytest.mark.asyncio
async def test_architect_and_pm_project_manager_agents():
    llm = MockLLMClient()
    arch = ArchitectAgent(llm=llm)
    projmgr = ProjectManagerAgent(llm=llm)
    arch_res = await arch.run("PRD for notes app")
    assert arch_res.agent_name == "Architect"
    pmg_res = await projmgr.run(arch_res.content)
    assert pmg_res.agent_name == "Project Manager"


@pytest.mark.asyncio
async def test_engineer_and_qa_agents():
    llm = MockLLMClient()
    eng = EngineerAgent(llm=llm)
    qa = QAAgent(llm=llm)
    eng_res = await eng.run("Task list: build CLI & API")
    assert eng_res.agent_name == "Engineer"
    qa_res = await qa.run(eng_res.content)
    assert qa_res.agent_name == "QA"