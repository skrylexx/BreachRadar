"""
BreachRadar WebUI — Routeur Health
====================================
Endpoint simple pour les healthchecks Docker.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health")
async def health_check() -> JSONResponse:
    """Healthcheck endpoint — utilisé par Docker et les load balancers."""
    return JSONResponse(content={"status": "ok", "service": "breachradar-api"})
