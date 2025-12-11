"""
Health check routes.
"""
from fastapi import APIRouter

from app.models.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns service status.
    """
    return HealthResponse()

