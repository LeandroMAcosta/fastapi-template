from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from app.core.config import settings
from app.modules.auth.exceptions import InvalidTokenError, TokenExpiredError


def create_access_token(user_id: UUID, role: str, permissions: list[str], extra_claims: dict | None = None) -> str:
    claims = {
        "sub": str(user_id),
        "type": "access",
        "role": role,
        "permissions": permissions,
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


def decode_token(token: str, expected_type: str) -> dict:
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


def decode_refresh_token(token: str) -> UUID:
    payload = decode_token(token, expected_type="refresh")
    return UUID(payload["sub"])
