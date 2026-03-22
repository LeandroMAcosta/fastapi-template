from uuid import UUID

from fastapi import APIRouter, Body, Depends
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params

from app.core.auth import get_current_user_id
from app.database.base import get_db
from app.modules.user.filters import UserFilter
from app.modules.user.repository import UserRepository
from app.modules.user.schemas import UserResponse, UserUpdate
from app.modules.user.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def get_service(db=Depends(get_db)) -> UserService:
    return UserService(repository=UserRepository(db=db))


@router.get("/me", response_model=UserResponse)
def get_me(
    user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(get_service),
) -> UserResponse:
    return service.get(user_id)


@router.get("", response_model=Page[UserResponse])
def list_users(
    user_filter: UserFilter = FilterDepends(UserFilter),
    pagination_params: Params = Depends(),
    service: UserService = Depends(get_service),
) -> Page[UserResponse]:
    return service.get_all(entity_filter=user_filter, pagination_params=pagination_params)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    service: UserService = Depends(get_service),
) -> UserResponse:
    return service.get(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    data: UserUpdate = Body(...),
    service: UserService = Depends(get_service),
) -> UserResponse:
    return service.update(user_id, data.model_dump(exclude_unset=True))
