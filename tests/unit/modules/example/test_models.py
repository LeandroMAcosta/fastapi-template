from uuid import uuid4

from app.modules.example.models import Example


class TestExampleModel:
    def test_create_instance(self):
        example = Example(name="Test", description="A description")
        assert example.name == "Test"
        assert example.description == "A description"

    def test_create_with_id(self):
        entity_id = uuid4()
        example = Example(id=entity_id, name="Test")
        assert example.id == entity_id

    def test_tablename(self):
        assert Example.__tablename__ == "example"
