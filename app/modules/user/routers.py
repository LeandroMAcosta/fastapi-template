from uuid import UUID

from fastapi import APIRouter, Body, Depends
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params

from app.core.auth import get_current_user_id
from app.modules.user.filters import UserFilter
from app.modules.user.schemas import UserResponse, UserUpdate
from app.modules.user.service import UserService

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(get_current_user_id)])


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_me(
    user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(),
) -> UserResponse:
    return await service.get(user_id)


@router.get("", response_model=Page[UserResponse], summary="List users")
async def list_users(
    user_filter: UserFilter = FilterDepends(UserFilter),
    pagination_params: Params = Depends(),
    service: UserService = Depends(),
) -> Page[UserResponse]:
    return await service.get_all(entity_filter=user_filter, pagination_params=pagination_params)


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID")
async def get_user(
    user_id: UUID,
    service: UserService = Depends(),
) -> UserResponse:
    return await service.get(user_id)


@router.patch("/{user_id}", response_model=UserResponse, summary="Update user")
async def update_user(
    user_id: UUID,
    data: UserUpdate = Body(...),
    service: UserService = Depends(),
) -> UserResponse:
    return await service.update(user_id, data.model_dump(exclude_unset=True))
