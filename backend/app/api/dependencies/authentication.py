from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt import decode_access_token
from app.domain.users import UserInDB
from app.domain.sessions import SessionStatus
from app.api.dependencies.database import get_user_repository, get_session_repository
from app.persistence.mongodb.repositories.users import UserRepository
from app.persistence.mongodb.repositories.sessions import SessionRepository
from datetime import datetime

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
) -> UserInDB:
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id: str = payload.get("sub")
    token_id: str = payload.get("tid")
    
    if user_id is None or token_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    session = await session_repo.get_by_token_id(token_id)
    if not session or session.status != SessionStatus.ACTIVE or session.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Optionally update session activity
    # await session_repo.update_activity(token_id)
    
    # Attach token_id to user object temporarily for logout purposes
    user.token_id = token_id 
    return user
