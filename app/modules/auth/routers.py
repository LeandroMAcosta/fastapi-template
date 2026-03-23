from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.auth import create_access_token, create_refresh_token, decode_refresh_token
from app.modules.auth.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.modules.user.schemas import UserResponse
from app.modules.user.service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register",
    status_code=201,
    response_model=UserResponse,
    summary="Register a new user",
    description="Create a new user account with email and password.",
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: RegisterRequest,
    service: UserService = Depends(),
) -> UserResponse:
    return await service.create_user(data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate with email and password. Returns access and refresh tokens.",
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: LoginRequest,
    service: UserService = Depends(),
) -> TokenResponse:
    user = await service.get_by_email(data.email)
    if not user or not service.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")

    return TokenResponse(
        access_token=create_access_token(user_id=user.id),
        refresh_token=create_refresh_token(user_id=user.id),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh tokens",
    description="Exchange a valid refresh token for a new access/refresh token pair.",
)
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    data: RefreshRequest,
    service: UserService = Depends(),
) -> TokenResponse:
    user_id = decode_refresh_token(data.refresh_token)
    user = await service.get(user_id)
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")

    return TokenResponse(
        access_token=create_access_token(user_id=user.id),
        refresh_token=create_refresh_token(user_id=user.id),
    )
