"""Unit tests for JWT auth — no DB needed."""

from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.auth import create_access_token
from jose import jwt
from app.core.config import settings


class TestCreateAccessToken:
    def test_creates_valid_token(self):
        user_id = uuid4()
        token = create_access_token(user_id=user_id)
        payload = jwt.decode(token, settings.AUTH_JWT_SECRET, algorithms=[settings.AUTH_JWT_ALGORITHM])
        assert payload["sub"] == str(user_id)
        assert "exp" in payload
        assert "iat" in payload

    def test_includes_extra_claims(self):
        user_id = uuid4()
        token = create_access_token(user_id=user_id, extra_claims={"role": "admin"})
        payload = jwt.decode(token, settings.AUTH_JWT_SECRET, algorithms=[settings.AUTH_JWT_ALGORITHM])
        assert payload["role"] == "admin"
