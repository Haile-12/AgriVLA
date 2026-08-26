from fastapi import APIRouter, Depends, status
from app.api.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.domain.users import UserResponse, UserInDB, UserCreate
from app.auth.service import AuthService
from app.api.dependencies.database import get_user_repository, get_session_repository
from app.api.dependencies.authentication import get_current_user
from app.persistence.mongodb.repositories.users import UserRepository
from app.persistence.mongodb.repositories.sessions import SessionRepository

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
) -> AuthService:
    return AuthService(user_repo, session_repo)

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    user_create = UserCreate(email=request.email, password=request.password, display_name=request.display_name)
    user, token = await auth_service.register_user(user_create)
    return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    user, token = await auth_service.authenticate_user(request.email, request.password)
    return TokenResponse(access_token=token)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserInDB = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: UserInDB = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    if current_user.token_id:
        await auth_service.logout(current_user.token_id)
