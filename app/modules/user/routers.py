from uuid import UUID

from fastapi import APIRouter, Body, Depends
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params

from app.modules.auth.dependencies import get_current_user, get_current_user_id, require_permissions
from app.modules.user.filters import UserFilter
from app.modules.user.models import User
from app.modules.user.schemas import UserResponse, UserUpdate
from app.modules.user.service import UserService

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(get_current_user_id)])


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    return user


@router.get(
    "",
    response_model=Page[UserResponse],
    summary="List users",
    dependencies=[Depends(require_permissions("user:read"))],
)
async def list_users(
    user_filter: UserFilter = FilterDepends(UserFilter),
    pagination_params: Params = Depends(),
    service: UserService = Depends(),
) -> Page[UserResponse]:
    return await service.get_all(entity_filter=user_filter, pagination_params=pagination_params)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    dependencies=[Depends(require_permissions("user:read"))],
)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(),
) -> UserResponse:
    return await service.get(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    dependencies=[Depends(require_permissions("user:update"))],
)
async def update_user(
    user_id: UUID,
    data: UserUpdate = Body(...),
    service: UserService = Depends(),
) -> UserResponse:
    return await service.update(user_id, data.model_dump(exclude_unset=True))


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Delete user",
    dependencies=[Depends(require_permissions("user:delete"))],
)
async def delete_user(
    user_id: UUID,
    service: UserService = Depends(),
) -> None:
    await service.delete(user_id)
