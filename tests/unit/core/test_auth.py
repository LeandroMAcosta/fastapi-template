"""Unit tests for JWT auth — no DB needed."""

from uuid import uuid4

import jwt

from app.core.auth import create_access_token, create_refresh_token, decode_refresh_token
from app.core.config import settings


class TestCreateAccessToken:
    def test_creates_valid_token(self):
        user_id = uuid4()
        token = create_access_token(user_id=user_id, permissions=["user:read"])
        payload = jwt.decode(token, settings.AUTH_JWT_SECRET, algorithms=[settings.AUTH_JWT_ALGORITHM])
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"
        assert payload["permissions"] == ["user:read"]
        assert "exp" in payload
        assert "iat" in payload

    def test_includes_extra_claims(self):
        user_id = uuid4()
        token = create_access_token(user_id=user_id, permissions=[], extra_claims={"custom": "value"})
        payload = jwt.decode(token, settings.AUTH_JWT_SECRET, algorithms=[settings.AUTH_JWT_ALGORITHM])
        assert payload["custom"] == "value"


class TestCreateRefreshToken:
    def test_creates_valid_refresh_token(self):
        user_id = uuid4()
        token = create_refresh_token(user_id=user_id)
        payload = jwt.decode(token, settings.AUTH_JWT_SECRET, algorithms=[settings.AUTH_JWT_ALGORITHM])
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

    def test_decode_refresh_token(self):
        user_id = uuid4()
        token = create_refresh_token(user_id=user_id)
        decoded_id = decode_refresh_token(token)
        assert decoded_id == user_id
