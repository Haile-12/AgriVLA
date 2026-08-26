from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field

class AgentSessionStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ESCALATED = "ESCALATED"
    FAILED = "FAILED"

class AgentSession(BaseModel):
    agent_session_id: str = Field(alias="_id")
    user_id: str
    title: str
    goal: str
    scenario_id: Optional[str] = None
    status: AgentSessionStatus = AgentSessionStatus.INITIALIZED
    current_step: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    termination_reason: Optional[str] = None
