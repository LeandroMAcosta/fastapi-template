from pydantic import BaseModel, EmailStr

from app.modules.user.schemas import UserCreate


class RegisterRequest(UserCreate):
    """Registration request — inherits email, password, first_name, last_name from UserCreate."""

    pass


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
