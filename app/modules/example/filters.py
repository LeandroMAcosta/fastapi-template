from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter

from app.modules.example.models import Example


class ExampleFilter(Filter):
    name: Optional[str] = None
    name__ilike: Optional[str] = None
    order_by: list[str] = ["-created_at"]

    class Constants(Filter.Constants):
        model = Example
