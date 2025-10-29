from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from api.db.database import AsyncSessionLocal
from api.db.models import AgentOutput


router = APIRouter()


async def _get_session():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/{project_id}", summary="List all agent outputs for a project")
async def list_results(project_id: int, session = Depends(_get_session)) -> List[dict]:
    res = await session.execute(
        select(AgentOutput).where(AgentOutput.project_id == project_id).order_by(AgentOutput.created_at)
    )
    rows = list(res.scalars().all())
    if not rows:
        # Not necessarily an error; could be running
        return []
    return [
        {
            "id": r.id,
            "project_id": r.project_id,
            "agent_name": r.agent_name,
            "content": r.content,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]