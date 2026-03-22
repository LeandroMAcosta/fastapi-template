from app.database.repository import SQLAlchemyRepository
from app.modules.example.models import Example


class ExampleRepository(SQLAlchemyRepository[Example]):
    model = Example
