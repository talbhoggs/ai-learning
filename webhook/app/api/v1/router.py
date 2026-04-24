"""API v1 router aggregation"""
from fastapi import APIRouter

from app.api.v1.endpoints import webhooks, health

api_router = APIRouter()

# Include health endpoints at root level
api_router.include_router(health.router, tags=["health"])

# Include webhook endpoints
api_router.include_router(
    webhooks.router,
    prefix="/webhook",
    tags=["webhooks"]
)

