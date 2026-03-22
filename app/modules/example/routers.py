from uuid import UUID

from fastapi import APIRouter, Body, Depends
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, Params

from app.core.auth import get_current_user_id
from app.database.base import get_db
from app.modules.example.filters import ExampleFilter
from app.modules.example.repository import ExampleRepository
from app.modules.example.schemas import ExampleCreate, ExampleResponse, ExampleUpdate
from app.modules.example.service import ExampleService

router = APIRouter(prefix="/examples", tags=["Examples"])


def get_service(db=Depends(get_db)) -> ExampleService:
    return ExampleService(repository=ExampleRepository(db=db))


@router.post("", status_code=201, response_model=ExampleResponse)
def create(
    data: ExampleCreate = Body(...),
    user_id: UUID = Depends(get_current_user_id),
    service: ExampleService = Depends(get_service),
) -> ExampleResponse:
    entity = service.create_example(data, created_by_id=user_id)
    return entity


@router.get("", response_model=Page[ExampleResponse])
def list_all(
    example_filter: ExampleFilter = FilterDepends(ExampleFilter),
    pagination_params: Params = Depends(),
    service: ExampleService = Depends(get_service),
) -> Page[ExampleResponse]:
    return service.get_all(entity_filter=example_filter, pagination_params=pagination_params)


@router.get("/{example_id}", response_model=ExampleResponse)
def get(
    example_id: UUID,
    service: ExampleService = Depends(get_service),
) -> ExampleResponse:
    return service.get(example_id)


@router.patch("/{example_id}", response_model=ExampleResponse)
def update(
    example_id: UUID,
    data: ExampleUpdate = Body(...),
    service: ExampleService = Depends(get_service),
) -> ExampleResponse:
    return service.update(example_id, data.model_dump(exclude_unset=True))


@router.delete("/{example_id}", status_code=204)
def delete(
    example_id: UUID,
    service: ExampleService = Depends(get_service),
) -> None:
    service.delete(example_id)
