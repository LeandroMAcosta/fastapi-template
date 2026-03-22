from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter

from app.modules.user.models import User


class UserFilter(Filter):
    email: Optional[str] = None
    email__ilike: Optional[str] = None
    first_name__ilike: Optional[str] = None
    last_name__ilike: Optional[str] = None
    is_active: Optional[bool] = None
    order_by: list[str] = ["-created_at"]

    class Constants(Filter.Constants):
        model = User
