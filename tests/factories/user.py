from polyfactory.factories.pydantic_factory import ModelFactory

from app.modules.auth.schemas import RegisterRequest
from app.modules.user.schemas import UserCreate, UserUpdate


class UserCreateFactory(ModelFactory):
    __model__ = UserCreate
    password = "SecureP@ss123"


class UserUpdateFactory(ModelFactory):
    __model__ = UserUpdate


class RegisterRequestFactory(ModelFactory):
    __model__ = RegisterRequest
    password = "SecureP@ss123"
