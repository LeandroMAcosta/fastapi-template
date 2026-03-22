from fastapi import APIRouter

from app.modules.example.routers import router as example_router

api_router = APIRouter()

# Mount module routers here
api_router.include_router(example_router)
