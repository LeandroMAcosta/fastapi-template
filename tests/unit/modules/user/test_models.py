"""Unit tests for user model — no DB needed."""

from uuid import uuid4

from app.modules.user.models import User


class TestUserModel:
    def test_create_instance(self):
        user = User(email="test@test.com", hashed_password="hash", first_name="John", last_name="Doe")
        assert user.email == "test@test.com"
        assert user.first_name == "John"

    def test_create_with_id(self):
        user_id = uuid4()
        user = User(id=user_id, email="a@b.com", hashed_password="h", first_name="A", last_name="B")
        assert user.id == user_id

    def test_tablename(self):
        assert User.__tablename__ == "user"
