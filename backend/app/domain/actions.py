from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel

class ActionType(str, Enum):
    OBSERVE = "OBSERVE"
    REQUEST_NEW_IMAGE = "REQUEST_NEW_IMAGE"
    MONITOR = "MONITOR"
    WATER = "WATER"
    RECOMMEND_TREATMENT = "RECOMMEND_TREATMENT"
    CHANGE_TREATMENT = "CHANGE_TREATMENT"
    ESCALATE = "ESCALATE"
    STOP = "STOP"

class ActionProposal(BaseModel):
    action_type: ActionType
    target: Optional[str] = None
    reason: str
    confidence: float
    expected_outcome: str
    requires_follow_up_observation: bool = False
    parameters: Dict[str, Any] = {}

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ActionValidationResult(BaseModel):
    approved: bool
    reason: str
    risk_level: RiskLevel
    corrective_action: Optional[ActionType] = None
