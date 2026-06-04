"""
BreachRadar WebUI — Health Router
======================================
Simple endpoint for Docker healthchecks.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health")
async def health_check() -> JSONResponse:
    """Healthcheck endpoint — used by Docker and load balancers."""
    return JSONResponse(content={"status": "ok", "service": "breachradar-api"})
