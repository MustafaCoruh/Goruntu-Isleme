"""Health check routes for the FastAPI application."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def get_health() -> dict[str, str]:
    """Return a simple application health response."""

    return {"status": "ok"}
