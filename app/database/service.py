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

    async def get(self, entity_id: UUID) -> T:
        return await self.repository.get(entity_id)

    async def get_all(
        self,
        entity_filter: Filter | None = None,
        pagination_params: Params | None = None,
    ) -> Page[T] | list[T]:
        return await self.repository.get_all(entity_filter=entity_filter, pagination_params=pagination_params)

    async def create(self, entity: T) -> T:
        return await self.repository.save(entity)

    async def update(self, entity_id: UUID, data: dict) -> T:
        return await self.repository.update(entity_id, data)

    async def delete(self, entity_id: UUID) -> None:
        return await self.repository.delete(entity_id)

    async def count(self, entity_filter: Filter | None = None) -> int:
        return await self.repository.count(entity_filter)
