from uuid import UUID

from app.database.service import BaseService
from app.modules.example.models import Example
from app.modules.example.repository import ExampleRepository
from app.modules.example.schemas import ExampleCreate


class ExampleService(BaseService[Example]):
    def __init__(self, repository: ExampleRepository):
        super().__init__(repository)

    def create_example(self, data: ExampleCreate, created_by_id: UUID) -> Example:
        entity = Example(
            name=data.name,
            description=data.description,
            created_by_id=created_by_id,
        )
        return self.repository.save(entity)
