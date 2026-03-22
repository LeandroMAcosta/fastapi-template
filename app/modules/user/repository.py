from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.repository import SQLAlchemyRepository
from app.modules.user.models import User


class UserRepository(SQLAlchemyRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        return self.db.execute(query).scalar_one_or_none()
