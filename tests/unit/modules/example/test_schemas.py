"""Unit tests for Pydantic schemas — no DB needed."""

import pytest
from pydantic import ValidationError

from app.modules.example.schemas import ExampleCreate, ExampleUpdate


class TestExampleCreate:
    def test_valid(self):
        schema = ExampleCreate(name="Test", description="Desc")
        assert schema.name == "Test"
        assert schema.description == "Desc"

    def test_without_description(self):
        schema = ExampleCreate(name="Test")
        assert schema.description is None

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            ExampleCreate()


class TestExampleUpdate:
    def test_partial_update_name_only(self):
        schema = ExampleUpdate(name="Updated")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"name": "Updated"}
        assert "description" not in data

    def test_partial_update_description_only(self):
        schema = ExampleUpdate(description="New desc")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"description": "New desc"}

    def test_empty_update(self):
        schema = ExampleUpdate()
        data = schema.model_dump(exclude_unset=True)
        assert data == {}
