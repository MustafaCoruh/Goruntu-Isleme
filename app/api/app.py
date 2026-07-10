"""FastAPI application factory and database dependencies."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from app.database.db import init_db

@asynccontextmanager
async def lifespan(api_app: FastAPI) -> AsyncIterator[None]:
    """Initialize application resources when the API starts."""

    init_db()
    yield


def create_app() -> FastAPI:
    """Create and configure the FTMC occupancy API application."""

    api_app = FastAPI(title="FTMC Occupancy API", lifespan=lifespan)

    from app.api.routes_health import router as health_router
    from app.api.routes_occupancy import router as occupancy_router
    from app.api.routes_tables import router as tables_router

    api_app.include_router(health_router)
    api_app.include_router(tables_router)
    api_app.include_router(occupancy_router)

    return api_app


app = create_app()
