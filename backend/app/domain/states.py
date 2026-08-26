from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.domain.observations import ObservationQuality

class AgentState(BaseModel):
    agent_id: str
    scenario_id: Optional[str] = None
    goal: str
    step_number: int = 0
    
    # Current Understanding
    crop: Optional[str] = None
    condition: Optional[str] = None
    severity: float = 0.0
    visible_damage: List[str] = []
    confidence: float = 0.0
    observation_quality: Optional[ObservationQuality] = None
    
    # History
    current_observation: Optional[str] = None
    previous_observation: Optional[str] = None
    previous_action: Optional[Dict[str, Any]] = None
    action_history: List[Dict[str, Any]] = []
    feedback_history: List[Dict[str, Any]] = []
    
    # Statistics
    failure_count: int = 0
    successful_action_count: int = 0
    trend: str = "UNKNOWN"
    
    # Lifecycle
    status: str = "IN_PROGRESS"
    termination_reason: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
