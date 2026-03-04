"""Health check route."""

from fastapi import APIRouter

from app.models.schemas import HealthResponse

router = APIRouter()

VERSION = "0.1.0"


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="ok", version=VERSION)
