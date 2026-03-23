from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.auth.exceptions import InsufficientPermissionsError, InvalidTokenError
from app.modules.auth.service import decode_token
from app.modules.user.models import User
from app.modules.user.service import UserService

security = HTTPBearer(auto_error=False)


def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UUID:
    token = request.cookies.get("access_token")
    if not token and credentials:
        token = credentials.credentials
    if not token:
        raise InvalidTokenError()

    payload = decode_token(token, expected_type="access")
    return UUID(payload["sub"])


async def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(),
) -> User:
    return await service.get(user_id)


def _get_current_token_payload(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    token = request.cookies.get("access_token")
    if not token and credentials:
        token = credentials.credentials
    if not token:
        raise InvalidTokenError()

    return decode_token(token, expected_type="access")


def require_permissions(*required: str):
    """Dependency factory: checks that the JWT contains all required permissions."""

    def checker(payload: dict = Depends(_get_current_token_payload)) -> dict:
        if payload.get("role") == "admin":
            return payload
        user_permissions = set(payload.get("permissions", []))
        missing = set(required) - user_permissions
        if missing:
            raise InsufficientPermissionsError()
        return payload

    return checker
