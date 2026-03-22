from typing import Generic, TypeVar
from uuid import UUID

from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Page, Params

from app.database.base import Base
from app.database.repository import SQLAlchemyRepository

T = TypeVar("T", bound=Base)


class BaseService(Generic[T]):
    """Base service that delegates CRUD operations to a repository."""

    def __init__(self, repository: SQLAlchemyRepository[T]):
        self.repository = repository

    def get(self, entity_id: UUID) -> T:
        return self.repository.get(entity_id)

    def get_all(
        self,
        entity_filter: Filter | None = None,
        pagination_params: Params | None = None,
    ) -> Page[T] | list[T]:
        return self.repository.get_all(entity_filter=entity_filter, pagination_params=pagination_params)

    def create(self, entity: T) -> T:
        return self.repository.save(entity)

    def update(self, entity_id: UUID, data: dict) -> T:
        return self.repository.update(entity_id, data)

    def delete(self, entity_id: UUID) -> None:
        return self.repository.delete(entity_id)

    def count(self, entity_filter: Filter | None = None) -> int:
        return self.repository.count(entity_filter)
