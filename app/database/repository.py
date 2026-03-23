from typing import Generic, TypeVar
from uuid import UUID

from fastapi import Depends
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateError, NotFoundError
from app.database.base import Base, get_db

T = TypeVar("T", bound=Base)


class SQLAlchemyRepository(Generic[T]):
    """Generic repository implementing CRUD operations with async SQLAlchemy."""

    model: type[T]

    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get(self, entity_id: UUID, *, raise_if_not_found: bool = True) -> T | None:
        entity = await self.db.get(self.model, entity_id)
        if not entity and raise_if_not_found:
            raise NotFoundError(f"{self.model.__name__} with id {entity_id} not found")
        return entity

    async def get_all(
        self,
        entity_filter: Filter | None = None,
        pagination_params: Params | None = None,
    ) -> Page[T] | list[T]:
        query = select(self.model)
        if entity_filter:
            query = entity_filter.filter(query)
            query = entity_filter.sort(query)
        if pagination_params:
            return await paginate(self.db, query, params=pagination_params)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def save(self, entity: T) -> T:
        try:
            self.db.add(entity)
            await self.db.commit()
            await self.db.refresh(entity)
            return entity
        except IntegrityError as e:
            await self.db.rollback()
            if "unique" in str(e.orig).lower():
                raise DuplicateError(f"{self.model.__name__} already exists")
            raise

    async def save_many(self, entities: list[T]) -> list[T]:
        try:
            self.db.add_all(entities)
            await self.db.commit()
            for entity in entities:
                await self.db.refresh(entity)
            return entities
        except IntegrityError as e:
            await self.db.rollback()
            if "unique" in str(e.orig).lower():
                raise DuplicateError(f"Duplicate {self.model.__name__} found")
            raise

    async def update(self, entity_id: UUID, data: BaseModel) -> T:
        entity = await self.get(entity_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def delete(self, entity_id: UUID) -> None:
        entity = await self.get(entity_id)
        await self.db.delete(entity)
        await self.db.commit()

    async def count(self, entity_filter: Filter | None = None) -> int:
        query = select(func.count()).select_from(self.model)
        if entity_filter:
            query = entity_filter.filter(query)
        result = await self.db.execute(query)
        return result.scalar_one()
