"""Unit tests for user schemas — no DB needed."""

import pytest
from pydantic import ValidationError

from app.modules.user.schemas import UserCreate, UserUpdate
from tests.factories.user import UserCreateFactory, UserUpdateFactory


class TestUserCreate:
    def test_valid_from_factory(self):
        schema = UserCreateFactory.build()
        assert schema.email is not None
        assert schema.first_name is not None
        assert schema.last_name is not None

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(email="not-an-email", password="pass", first_name="A", last_name="B")

    def test_missing_password_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", first_name="A", last_name="B")


class TestUserUpdate:
    def test_partial_first_name_only(self):
        schema = UserUpdate(first_name="New")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"first_name": "New"}

    def test_empty_update(self):
        schema = UserUpdate()
        data = schema.model_dump(exclude_unset=True)
        assert data == {}

    def test_factory_builds(self):
        schema = UserUpdateFactory.build()
        assert isinstance(schema, UserUpdate)
