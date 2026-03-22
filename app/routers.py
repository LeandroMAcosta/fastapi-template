from fastapi import APIRouter

from app.modules.auth.routers import router as auth_router
from app.modules.user.routers import router as user_router

api_router = APIRouter()

# Public routes (no auth required)
api_router.include_router(auth_router)

# Protected routes
api_router.include_router(user_router)
