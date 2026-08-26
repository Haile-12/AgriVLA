from fastapi import HTTPException, status
from typing import Tuple, Optional
from datetime import datetime, timedelta
import uuid
from app.domain.users import UserInDB, UserCreate
from app.domain.sessions import UserSession, SessionStatus
from app.persistence.mongodb.repositories.users import UserRepository
from app.persistence.mongodb.repositories.sessions import SessionRepository
from app.auth.password import get_password_hash, verify_password
from app.auth.jwt import create_access_token
from app.config.settings import settings

class AuthService:
    def __init__(self, user_repo: UserRepository, session_repo: SessionRepository):
        self.user_repo = user_repo
        self.session_repo = session_repo

    async def register_user(self, user_create: UserCreate) -> Tuple[UserInDB, str]:
        existing_user = await self.user_repo.get_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # In a real app, validate password strength here
        hashed_password = get_password_hash(user_create.password)
        new_user = await self.user_repo.create(user_create, hashed_password)
        
        # Create session
        token_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        await self.session_repo.create(
            user_id=new_user.id,
            token_id=token_id,
            expires_at=expires_at
        )
        
        access_token = create_access_token(
            data={"sub": new_user.id, "tid": token_id}
        )
        
        return new_user, access_token

    async def authenticate_user(self, email: str, password: str) -> Tuple[UserInDB, str]:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
        await self.user_repo.update_last_login(user.id)
        
        # Create new session
        token_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        await self.session_repo.create(
            user_id=user.id,
            token_id=token_id,
            expires_at=expires_at
        )
        
        access_token = create_access_token(
            data={"sub": user.id, "tid": token_id}
        )
        
        return user, access_token

    async def logout(self, token_id: str) -> None:
        await self.session_repo.revoke_session(token_id)
