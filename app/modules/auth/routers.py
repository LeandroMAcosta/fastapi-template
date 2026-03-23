from fastapi import APIRouter, Depends, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.modules.auth.exceptions import InvalidCredentialsError, UserDisabledError
from app.modules.auth.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.modules.auth.service import create_access_token, create_refresh_token, decode_refresh_token
from app.modules.user.schemas import UserResponse
from app.modules.user.service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)


def _get_user_permissions(user) -> list[str]:
    return [p.codename for p in user.role.permissions]


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    cookie_kwargs = {
        "httponly": True,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
    }
    if settings.COOKIE_DOMAIN:
        cookie_kwargs["domain"] = settings.COOKIE_DOMAIN

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.AUTH_ACCESS_TOKEN_EXPIRATION_MINUTES * 60,
        path="/",
        **cookie_kwargs,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.AUTH_REFRESH_TOKEN_EXPIRATION_DAYS * 86400,
        path="/api/v1/auth",
        **cookie_kwargs,
    )


def _clear_auth_cookies(response: Response) -> None:
    cookie_kwargs = {
        "httponly": True,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
    }
    if settings.COOKIE_DOMAIN:
        cookie_kwargs["domain"] = settings.COOKIE_DOMAIN

    response.delete_cookie(key="access_token", path="/", **cookie_kwargs)
    response.delete_cookie(key="refresh_token", path="/api/v1/auth", **cookie_kwargs)


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
    description="Authenticate with email and password. Returns tokens (also set as httpOnly cookies).",
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    data: LoginRequest,
    service: UserService = Depends(),
) -> TokenResponse:
    user = await service.get_by_email(data.email)
    if not user or not service.verify_password(data.password, user.hashed_password):
        raise InvalidCredentialsError()
    if not user.is_active:
        raise UserDisabledError()

    permissions = _get_user_permissions(user)
    access_token = create_access_token(user_id=user.id, role=user.role.name, permissions=permissions)
    refresh_token = create_refresh_token(user_id=user.id)

    _set_auth_cookies(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
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
    response: Response,
    data: RefreshRequest = Depends(),
    service: UserService = Depends(),
) -> TokenResponse:
    token = data.refresh_token or request.cookies.get("refresh_token")
    if not token:
        raise InvalidCredentialsError()

    user_id = decode_refresh_token(token)
    user = await service.get(user_id)
    if not user.is_active:
        raise UserDisabledError()

    permissions = _get_user_permissions(user)
    access_token = create_access_token(user_id=user.id, role=user.role.name, permissions=permissions)
    new_refresh_token = create_refresh_token(user_id=user.id)

    _set_auth_cookies(response, access_token, new_refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.post(
    "/logout",
    status_code=204,
    summary="Logout",
    description="Clear authentication cookies.",
)
async def logout(response: Response) -> None:
    _clear_auth_cookies(response)
