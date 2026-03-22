"""Unit tests for user service — mocked repository, no DB."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions import DuplicateError
from app.modules.user.models import User
from app.modules.user.service import UserService
from tests.factories.user import UserCreateFactory


class TestUserServiceCreate:
    def setup_method(self):
        self.mock_repo = MagicMock()
        self.service = UserService(repository=self.mock_repo)

    def test_creates_user_with_hashed_password(self):
        data = UserCreateFactory.build()
        self.mock_repo.get_by_email.return_value = None
        self.mock_repo.save.side_effect = lambda user: user

        result = self.service.create_user(data)

        self.mock_repo.get_by_email.assert_called_once_with(data.email)
        self.mock_repo.save.assert_called_once()
        assert result.email == data.email
        assert result.hashed_password != data.password

    def test_duplicate_email_raises(self):
        data = UserCreateFactory.build()
        self.mock_repo.get_by_email.return_value = User(
            id=uuid4(), email=data.email, hashed_password="x", first_name="A", last_name="B",
        )

        with pytest.raises(DuplicateError):
            self.service.create_user(data)

        self.mock_repo.save.assert_not_called()


class TestUserServiceGet:
    def setup_method(self):
        self.mock_repo = MagicMock()
        self.service = UserService(repository=self.mock_repo)

    def test_get_by_id(self):
        user_id = uuid4()
        expected = User(id=user_id, email="test@test.com", hashed_password="x", first_name="A", last_name="B")
        self.mock_repo.get.return_value = expected

        result = self.service.get(user_id)

        self.mock_repo.get.assert_called_once_with(user_id)
        assert result.id == user_id

    def test_get_by_email(self):
        expected = User(id=uuid4(), email="test@test.com", hashed_password="x", first_name="A", last_name="B")
        self.mock_repo.get_by_email.return_value = expected

        result = self.service.get_by_email("test@test.com")

        assert result.email == "test@test.com"


class TestUserServicePassword:
    def test_verify_correct_password(self):
        hashed = UserService._hash_password("mypassword")
        assert UserService.verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self):
        hashed = UserService._hash_password("mypassword")
        assert UserService.verify_password("wrongpassword", hashed) is False
