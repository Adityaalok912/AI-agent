import pytest
from sqlalchemy.ext.asyncio import AsyncSession


from api.ai.core.message_bus import MessageBus
from api.ai.core.orchestrator import Orchestrator
from api.ai.agents.llm_client import MockLLMClient
from api.db import crud


@pytest.mark.asyncio
async def test_orchestrator_runs(session: AsyncSession):
    bus = MessageBus()
    orch = Orchestrator(message_bus=bus, llm=MockLLMClient())


    # Patch CRUD to use the async session fixture
    async def create_project(db, title, user_prompt):
        return await crud.create_project(session, title, user_prompt)


    async def add_agent_output(db, project_id, agent_name, content):
        return await crud.add_agent_output(session, project_id, agent_name, content)


    # Monkeypatch in lieu of DI (keeps orchestrator code untouched)
    import db.crud as crud_module
    crud_module.create_project = create_project
    crud_module.add_agent_output = add_agent_output


    results = await orch.run(prompt="Build an AI notes app", db=session, project_title="Test")
    assert len(results) >= 7 # Boss, PM, Arch, PM(refined), Arch(refined), PMgr, Arch(final), PMgr(refined), Eng, QA, Eng(final)