

## `db/crud.py`

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Project, AgentOutput

async def create_project(db: AsyncSession, title: str, user_prompt: str) -> int:
    proj = Project(title=title, user_prompt=user_prompt)
    db.add(proj)
    await db.commit()
    await db.refresh(proj)
    return proj.id

async def add_agent_output(db: AsyncSession, project_id: int, agent_name: str, content: str) -> int:
    rec = AgentOutput(project_id=project_id, agent_name=agent_name, content=content)
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec.id

async def get_project(db: AsyncSession, project_id: int) -> Optional[Project]:
    res = await db.execute(select(Project).where(Project.id == project_id))
    return res.scalar_one_or_none()

async def list_agent_outputs(db: AsyncSession, project_id: int) -> List[AgentOutput]:
    res = await db.execute(select(AgentOutput).where(AgentOutput.project_id == project_id).order_by(AgentOutput.created_at))
    return list(res.scalars().all())


