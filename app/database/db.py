"""Database connection helpers for the FTMC occupancy application."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
from urllib.parse import unquote, urlparse

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_DATABASE_URL = "sqlite:///data/ftmc.sqlite"


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


def get_database_url(config: Mapping[str, Any] | None = None) -> str:
    """Return the configured SQLAlchemy database URL.

    Expected configuration example::

        {"database_url": "sqlite:///data/ftmc.sqlite"}
    """

    if config is None:
        return DEFAULT_DATABASE_URL

    database_url = config.get("database_url", DEFAULT_DATABASE_URL)
    if not isinstance(database_url, str) or not database_url.strip():
        raise ValueError("database_url must be a non-empty string")

    return database_url


def _sqlite_connect_args(database_url: str) -> dict[str, bool]:
    if database_url.startswith("sqlite:"):
        return {"check_same_thread": False}

    return {}


def create_database_engine(config: Mapping[str, Any] | None = None) -> Engine:
    """Create a SQLAlchemy engine from application configuration."""

    database_url = get_database_url(config)
    return create_engine(database_url, connect_args=_sqlite_connect_args(database_url))


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create the application session factory for the supplied engine."""

    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


engine = create_database_engine()
SessionLocal = create_session_factory(engine)


def _sqlite_database_path(database_url: str) -> Path | None:
    """Return the filesystem path for file-backed SQLite URLs, if any."""

    parsed_url = urlparse(database_url)
    if parsed_url.scheme != "sqlite" or database_url in {"sqlite://", "sqlite:///:memory:"}:
        return None

    if parsed_url.netloc:
        return Path(unquote(f"//{parsed_url.netloc}{parsed_url.path}"))

    if parsed_url.path in {"", "/:memory:"}:
        return None

    raw_path = unquote(parsed_url.path)
    if raw_path.startswith("/") and not raw_path.startswith("//"):
        raw_path = raw_path[1:]

    return Path(raw_path)


def init_db(config: Mapping[str, Any] | None = None, db_engine: Engine | None = None) -> None:
    """Create the SQLite database directory when needed and initialize all ORM tables."""

    active_engine = db_engine or (create_database_engine(config) if config is not None else engine)
    database_url = str(active_engine.url)
    database_path = _sqlite_database_path(database_url)
    if database_path is not None:
        database_path.parent.mkdir(parents=True, exist_ok=True)

    # Import models so SQLAlchemy registers all mapped tables on Base.metadata.
    from app.database import models  # noqa: F401

    Base.metadata.create_all(bind=active_engine)
