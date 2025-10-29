from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select


from api.db.database import AsyncSessionLocal
from api.db.models import Project
from api.db import crud as crud_async
from api.ai.schemas.project_request import ProjectCreate, ProjectResponse


router = APIRouter()


async def _get_session():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/", response_model=dict, summary="Create a new project (metadata only)")
async def create_project(body: ProjectCreate, session = Depends(_get_session)):
    pid = await crud_async.create_project(session, title=body.title or "Untitled", user_prompt=body.prompt)
    return {"id": pid, "title": body.title or "Untitled"}


@router.get("/{project_id}", summary="Fetch single project metadata")
async def get_project(project_id: int, session = Depends(_get_session)) -> Optional[ProjectResponse]:
    res = await session.execute(select(Project).where(Project.id == project_id))
    proj = res.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "id": proj.id,
        "title": proj.title,
        "prompt": proj.user_prompt,
    }


@router.get("/", summary="List recent projects")
async def list_projects(limit: int = 20, session = Depends(_get_session)):
    res = await session.execute(select(Project).order_by(Project.created_at.desc()).limit(limit))
    items = list(res.scalars().all())
    return [
        {"id": p.id, "title": p.title, "prompt": p.user_prompt, "created_at": p.created_at.isoformat()}
        for p in items
    ]