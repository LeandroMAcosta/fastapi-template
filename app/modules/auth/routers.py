from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import create_access_token
from app.database.base import get_db
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.modules.user.repository import UserRepository
from app.modules.user.schemas import UserCreate, UserResponse
from app.modules.user.service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_user_service(db=Depends(get_db)) -> UserService:
    return UserService(repository=UserRepository(db=db))


@router.post("/register", status_code=201, response_model=UserResponse)
def register(
    data: RegisterRequest,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    user_data = UserCreate(
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    return service.create_user(user_data)


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    service: UserService = Depends(get_user_service),
) -> TokenResponse:
    user = service.get_by_email(data.email)
    if not user or not service.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")

    token = create_access_token(user_id=user.id)
    return TokenResponse(access_token=token)
