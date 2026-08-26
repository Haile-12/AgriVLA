from enum import Enum
from typing import Optional
from pydantic import BaseModel

class FeedbackResultType(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    NO_CHANGE = "NO_CHANGE"
    UNCERTAIN = "UNCERTAIN"

class FeedbackResult(BaseModel):
    result: FeedbackResultType
    reward: float
    severity_change: float
    health_change: float
    goal_progress: float
    explanation: str
    recommended_next_step: Optional[str] = None
