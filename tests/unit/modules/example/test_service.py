from unittest.mock import MagicMock
from uuid import uuid4

from app.modules.example.models import Example
from app.modules.example.schemas import ExampleCreate
from app.modules.example.service import ExampleService


class TestExampleService:
    def setup_method(self):
        self.mock_repository = MagicMock()
        self.service = ExampleService(repository=self.mock_repository)

    def test_create_example(self):
        user_id = uuid4()
        data = ExampleCreate(name="Test", description="Desc")
        expected = Example(id=uuid4(), name="Test", description="Desc", created_by_id=user_id)
        self.mock_repository.save.return_value = expected

        result = self.service.create_example(data, created_by_id=user_id)

        self.mock_repository.save.assert_called_once()
        assert result == expected

    def test_get_by_id(self):
        entity_id = uuid4()
        expected = Example(id=entity_id, name="Test")
        self.mock_repository.get.return_value = expected

        result = self.service.get(entity_id)

        self.mock_repository.get.assert_called_once_with(entity_id)
        assert result == expected

    def test_delete(self):
        entity_id = uuid4()

        self.service.delete(entity_id)

        self.mock_repository.delete.assert_called_once_with(entity_id)

    def test_update(self):
        entity_id = uuid4()
        update_data = {"name": "Updated"}
        expected = Example(id=entity_id, name="Updated")
        self.mock_repository.update.return_value = expected

        result = self.service.update(entity_id, update_data)

        self.mock_repository.update.assert_called_once_with(entity_id, update_data)
        assert result.name == "Updated"
