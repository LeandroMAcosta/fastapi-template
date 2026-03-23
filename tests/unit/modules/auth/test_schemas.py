"""Unit tests for auth schemas — no DB needed."""

import pytest
from pydantic import ValidationError

from app.modules.auth.schemas import LoginRequest, RefreshRequest, RegisterRequest
from tests.factories.user import RegisterRequestFactory


class TestLoginRequest:
    def test_valid(self):
        schema = LoginRequest(email="test@example.com", password="pass123")
        assert schema.email == "test@example.com"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="not-email", password="pass")


class TestRegisterRequest:
    def test_valid(self):
        schema = RegisterRequestFactory.build()
        assert schema.email is not None
        assert schema.password == "SecureP@ss123"

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            RegisterRequest(email="test@example.com")

    def test_inherits_from_user_create(self):
        from app.modules.user.schemas import UserCreate

        assert issubclass(RegisterRequest, UserCreate)


class TestRefreshRequest:
    def test_valid(self):
        schema = RefreshRequest(refresh_token="some-token")
        assert schema.refresh_token == "some-token"

    def test_missing_token_defaults_to_none(self):
        schema = RefreshRequest()
        assert schema.refresh_token is None
