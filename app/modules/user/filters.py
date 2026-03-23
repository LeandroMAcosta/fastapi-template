from fastapi_filter.contrib.sqlalchemy import Filter

from app.modules.user.models import User


class UserFilter(Filter):
    email: str | None = None
    email__ilike: str | None = None
    first_name__ilike: str | None = None
    last_name__ilike: str | None = None
    is_active: bool | None = None
    order_by: list[str] = ["-created_at"]

    class Constants(Filter.Constants):
        model = User
