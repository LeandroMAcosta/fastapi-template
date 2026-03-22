from typing import Generic, TypeVar
from uuid import UUID

from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateError, NotFoundError
from app.database.base import Base

T = TypeVar("T", bound=Base)


class SQLAlchemyRepository(Generic[T]):
    """Generic repository implementing CRUD operations with SQLAlchemy."""

    model: type[T]

    def __init__(self, db: Session):
        self.db = db

    def get(self, entity_id: UUID) -> T:
        entity = self.db.get(self.model, entity_id)
        if not entity:
            raise NotFoundError(f"{self.model.__name__} with id {entity_id} not found")
        return entity

    def get_all(
        self,
        entity_filter: Filter | None = None,
        pagination_params: Params | None = None,
    ) -> Page[T] | list[T]:
        query = select(self.model)
        if entity_filter:
            query = entity_filter.filter(query)
            query = entity_filter.sort(query)
        if pagination_params:
            return paginate(self.db, query, params=pagination_params)
        return list(self.db.execute(query).scalars().all())

    def save(self, entity: T) -> T:
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except IntegrityError as e:
            self.db.rollback()
            if "unique" in str(e.orig).lower():
                raise DuplicateError(f"{self.model.__name__} already exists")
            raise

    def save_many(self, entities: list[T]) -> list[T]:
        try:
            self.db.add_all(entities)
            self.db.commit()
            for entity in entities:
                self.db.refresh(entity)
            return entities
        except IntegrityError as e:
            self.db.rollback()
            if "unique" in str(e.orig).lower():
                raise DuplicateError(f"Duplicate {self.model.__name__} found")
            raise

    def update(self, entity_id: UUID, data: dict) -> T:
        entity = self.get(entity_id)
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity_id: UUID) -> None:
        entity = self.get(entity_id)
        self.db.delete(entity)
        self.db.commit()

    def count(self, entity_filter: Filter | None = None) -> int:
        query = select(func.count()).select_from(self.model)
        if entity_filter:
            query = entity_filter.filter(query)
        return self.db.execute(query).scalar_one()
