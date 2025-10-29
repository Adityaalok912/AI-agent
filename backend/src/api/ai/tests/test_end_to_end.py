import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


from api.ai.core.message_bus import MessageBus
from api.ai.core.orchestrator import Orchestrator
from api.ai.agents.llm_client import MockLLMClient
from api.db import crud


@pytest.mark.asyncio
async def test_end_to_end_message_bus_and_db(session: AsyncSession):
    bus = MessageBus()
    orch = Orchestrator(message_bus=bus, llm=MockLLMClient())


    # Monkeypatch CRUD to always use our fixture session
    async def create_project(db, title, user_prompt):
        return await crud.create_project(session, title, user_prompt)


    async def add_agent_output(db, project_id, agent_name, content):
        return await crud.add_agent_output(session, project_id, agent_name, content)


    import db.crud as crud_module
    crud_module.create_project = create_project
    crud_module.add_agent_output = add_agent_output


    # Subscribe to the message stream concurrently
    messages = []
    async def consume(project_id):
    # consume a fixed number of messages then cancel
        async for msg in bus.subscribe(project_id):
            messages.append(msg)
            if len(messages) >= 5:
                break


    # Run pipeline
    project_id = await crud.create_project(session, "E2E", "Make an AI notes app")


    consumer_task = asyncio.create_task(consume(project_id))
    results = await orch.run(prompt="Make an AI notes app", db=session, project_title="E2E")
    await consumer_task


    assert results, "Pipeline should return agent results"
    assert messages, "Should stream messages via MessageBus"