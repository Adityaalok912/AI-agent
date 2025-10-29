from typing import Optional
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    title: Optional[str] = Field(default=None, description="Optional project title")
    prompt: str = Field(..., min_length=3, description="User idea / request")


class ProjectResponse(BaseModel):
    id: int
    title: str
    prompt: str