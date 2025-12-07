"""
API Router Configuration

This module centralizes all API routers and provides a single point
to register routes with the main FastAPI application.
"""
from fastapi import APIRouter

from api.routers import notes, health

api_router = APIRouter()

# Include all sub-routers with appropriate prefixes and tags
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    notes.router,
    prefix="/notes",
    tags=["notes"]
)
