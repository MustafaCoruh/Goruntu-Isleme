"""Shared FastAPI dependencies for API route modules."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for request handlers."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
