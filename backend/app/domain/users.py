from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    display_name: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str = Field(alias="_id")
    password_hash: str
    is_active: bool = True
    token_id: Optional[str] = None  # Transient: injected by auth dependency
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None

    model_config = {"populate_by_name": True}

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
