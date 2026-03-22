"""Unit tests for auth schemas — no DB needed."""

import pytest
from pydantic import ValidationError

from app.modules.auth.schemas import LoginRequest, RegisterRequest
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
