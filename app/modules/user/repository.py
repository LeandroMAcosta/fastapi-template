from sqlalchemy import select

from app.database.repository import SQLAlchemyRepository
from app.modules.role.models import Role
from app.modules.user.models import User


class UserRepository(SQLAlchemyRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_default_role(self) -> Role:
        query = select(Role).where(Role.name == "user")
        result = await self.db.execute(query)
        return result.scalar_one()
