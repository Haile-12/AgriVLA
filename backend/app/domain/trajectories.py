from datetime import datetime
from typing import Dict, Any, Optional
import uuid
from pydantic import BaseModel, Field

class TrajectoryStep(BaseModel):
    model_config = {"populate_by_name": True}
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    agent_session_id: str
    user_id: str
    step_number: int
    
    state_before: Dict[str, Any]
    observation_ref: Optional[str] = None
    perception: Optional[Dict[str, Any]] = None
    retrieved_knowledge: Optional[Dict[str, Any]] = None
    action_proposal: Optional[Dict[str, Any]] = None
    validation_result: Optional[Dict[str, Any]] = None
    environment_result: Optional[Dict[str, Any]] = None
    feedback: Optional[Dict[str, Any]] = None
    state_after: Dict[str, Any]
    
    timing_ms: Dict[str, float] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
