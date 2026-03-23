import bcrypt
from fastapi import Depends

from app.database.service import BaseService
from app.modules.user.exceptions import UserAlreadyExistsError
from app.modules.user.models import User
from app.modules.user.repository import UserRepository
from app.modules.user.schemas import UserCreate


class UserService(BaseService[User]):
    repository: UserRepository

    def __init__(self, repository: UserRepository = Depends()):
        super().__init__(repository)

    async def create_user(self, data: UserCreate) -> User:
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise UserAlreadyExistsError()

        user = User(
            email=data.email,
            hashed_password=self._hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
        )
        return await self.repository.save(user)

    async def get_by_email(self, email: str) -> User | None:
        return await self.repository.get_by_email(email)

    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
