from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional

class AgentMessage(BaseModel):
    """
    Standardized message format for agent outputs and lifecycle events.
    """
    # This uses the new Pydantic V2 model_config dictionary
    model_config = ConfigDict(from_attributes=True)
    
    event_type: Literal["agent_result", "agent_start", "workflow_start", "workflow_end", "error"]
    agent_name: Optional[str] = None
    content: Optional[str] = None
    project_id: int