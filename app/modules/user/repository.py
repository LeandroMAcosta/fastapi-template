from sqlalchemy import select

from app.database.repository import SQLAlchemyRepository
from app.modules.user.models import User


class UserRepository(SQLAlchemyRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
