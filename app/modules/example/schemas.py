from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExampleCreate(BaseModel):
    name: str
    description: str | None = None


class ExampleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ExampleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    created_by_id: UUID | None
