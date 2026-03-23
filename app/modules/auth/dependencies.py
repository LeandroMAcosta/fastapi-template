from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.auth.exceptions import InsufficientPermissionsError
from app.modules.auth.service import decode_token
from app.modules.user.models import User
from app.modules.user.service import UserService

security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UUID:
    payload = decode_token(credentials.credentials, expected_type="access")
    return UUID(payload["sub"])


async def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(),
) -> User:
    return await service.get(user_id)


def _get_current_token_payload(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    return decode_token(credentials.credentials, expected_type="access")


def require_permissions(*required: str):
    """Dependency factory: checks that the JWT contains all required permissions."""

    def checker(payload: dict = Depends(_get_current_token_payload)) -> dict:
        user_permissions = set(payload.get("permissions", []))
        missing = set(required) - user_permissions
        if missing:
            raise InsufficientPermissionsError()
        return payload

    return checker
