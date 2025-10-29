import asyncio
from typing import AsyncGenerator, List
from fastapi import APIRouter, HTTPException, Depends
from sse_starlette.sse import EventSourceResponse
from api.ai.core.message_bus import MessageBus
from api.ai.core.orchestrator import Orchestrator
from api.ai.agents.llm_client import MockLLMClient, OpenAIClient
from api.config.settings import get_settings
from api.db.database import AsyncSessionLocal
from api.db import crud 
from api.ai.schemas.project_request import ProjectCreate
router = APIRouter()


# # --- Compatibility shim: orchestrator expects sync-style crud.*
# # We monkeypatch the imported db.crud module with sync wrappers that call our 
# # async CRUD.
# import api.db.crud as crud_module
# async def _create_project_async(db, title, user_prompt):
#     return await crud_async.create_project(db, title, user_prompt)
# async def _add_agent_output_async(db, project_id, agent_name, content):
#     return await crud_async.add_agent_output(db, project_id, agent_name,
# content)
# # Expose sync-looking functions that actually await in the current loop
# # Orchestrator never awaits crud.*, but we can still bind coroutines here and
# # call them explicitly from our API before/after orchestrator where needed.
# crud_module.create_project = _create_project_async # type: ignore
# crud_module.add_agent_output = _add_agent_output_async # type: ignore
# # Shared singletons
_settings = get_settings()
_message_bus = MessageBus()
def _get_llm_client():
# Choose real provider if key present; fall back to Mock
    if _settings.OPENAI_API_KEY:
        return OpenAIClient(api_key=_settings.OPENAI_API_KEY,
model=_settings.OPENAI_MODEL)
    return MockLLMClient()


async def _get_session():
    async with AsyncSessionLocal() as session:
        yield session


# ---------- Run full pipeline and return final results ---------
@router.post("/run", summary="Run the multi-agent workflow and return all results")
async def run_pipeline(body: ProjectCreate, session = Depends(_get_session)):
    if not body.prompt or len(body.prompt) < 3:
        raise HTTPException(status_code=422, detail="Prompt must be at least 3 characters")
    llm = _get_llm_client()
    orch = Orchestrator(message_bus=_message_bus, llm=llm)
# The orchestrator will internally create the project and stream outputs via the message bus

# It expects `crud.*` to be available; we've monkeypatched async wrappers above.
    project_id = await crud.create_project(
        session, title=body.title or "AutoTeamAI Project", user_prompt=body.prompt
    )


    results = await orch.run(prompt=body.prompt, db=session,
project_title=body.title)
# Normalize response
    return {
         "project_id": project_id,
        "project_title": body.title or "AutoTeamAI Project",
        "results": [
            {"agent": r.agent_name, "content": r.content}
            for r in results
        ],
    }
# ---------- Live SSE stream of a project’s agent outputs ---------
@router.get("/stream/{project_id}", summary="SSE stream for live agent outputs")
async def stream_results(project_id: int):
    async def event_generator()-> AsyncGenerator[str, None]:
        async for msg in _message_bus.subscribe(project_id):
            yield {"event": "agent_output", "data": msg}
    return EventSourceResponse(event_generator())