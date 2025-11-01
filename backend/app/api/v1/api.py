"""
Main API router combining all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1 import chat

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(chat.router, prefix="/agent", tags=["Agent"])

