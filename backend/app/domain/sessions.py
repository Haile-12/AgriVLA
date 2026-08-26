from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field

class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

class UserSession(BaseModel):
    session_id: str = Field(alias="_id")
    user_id: str
    token_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    revoked_at: Optional[datetime] = None
    user_agent: Optional[str] = None
    ip_address_hash: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE
