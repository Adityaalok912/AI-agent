from datetime import datetime
from pydantic import BaseModel


class AgentOutputOut(BaseModel):
    id: int
    project_id: int
    agent_name: str
    content: str
    created_at: datetime