from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.modules.auth.exceptions import InvalidTokenError, TokenExpiredError

security = HTTPBearer()


def create_access_token(user_id: UUID, extra_claims: dict | None = None) -> str:
    claims = {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.now(UTC) + timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRATION_MINUTES),
        "iat": datetime.now(UTC),
    }
    if extra_claims:
        claims.update(extra_claims)
    return jwt.encode(claims, settings.AUTH_JWT_SECRET, algorithm=settings.AUTH_JWT_ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    claims = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.now(UTC) + timedelta(days=settings.AUTH_REFRESH_TOKEN_EXPIRATION_DAYS),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(claims, settings.AUTH_JWT_SECRET, algorithm=settings.AUTH_JWT_ALGORITHM)


def _decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, settings.AUTH_JWT_SECRET, algorithms=[settings.AUTH_JWT_ALGORITHM])
        if payload.get("type") != expected_type:
            raise InvalidTokenError("Invalid token type")
        if payload.get("sub") is None:
            raise InvalidTokenError()
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UUID:
    payload = _decode_token(credentials.credentials, expected_type="access")
    return UUID(payload["sub"])


def decode_refresh_token(token: str) -> UUID:
    payload = _decode_token(token, expected_type="refresh")
    return UUID(payload["sub"])
