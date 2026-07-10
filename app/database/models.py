"""SQLAlchemy ORM models for FTMC occupancy."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


def utc_now() -> datetime:
    """Return the current UTC datetime for timestamp defaults."""

    return datetime.utcnow()


class Utym(Base):
    """A UTYM/FTMC location that contains cameras and tables."""

    __tablename__ = "utym"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    cameras: Mapped[list[Camera]] = relationship(
        back_populates="utym",
        cascade="all, delete-orphan",
    )
    tables: Mapped[list[Table]] = relationship(
        back_populates="utym",
        cascade="all, delete-orphan",
    )
    occupancy_events: Mapped[list[OccupancyEvent]] = relationship(
        back_populates="utym",
        cascade="all, delete-orphan",
    )


class Camera(Base):
    """A camera source configured for a UTYM location."""

    __tablename__ = "camera"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    utym_id: Mapped[int] = mapped_column(ForeignKey("utym.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    stream_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    utym: Mapped[Utym] = relationship(back_populates="cameras")
    tables: Mapped[list[Table]] = relationship(back_populates="camera")
    occupancy_events: Mapped[list[OccupancyEvent]] = relationship(back_populates="camera")


class Table(Base):
    """A calibrated table area observed by a camera."""

    __tablename__ = "table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    utym_id: Mapped[int] = mapped_column(ForeignKey("utym.id"), nullable=False, index=True)
    camera_id: Mapped[int] = mapped_column(ForeignKey("camera.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    polygon_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    utym: Mapped[Utym] = relationship(back_populates="tables")
    camera: Mapped[Camera] = relationship(back_populates="tables")
    occupancy_events: Mapped[list[OccupancyEvent]] = relationship(back_populates="table")


class OccupancyEvent(Base):
    """A detected occupancy state for a table at a point in time."""

    __tablename__ = "occupancy_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    utym_id: Mapped[int] = mapped_column(ForeignKey("utym.id"), nullable=False, index=True)
    camera_id: Mapped[int] = mapped_column(ForeignKey("camera.id"), nullable=False, index=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("table.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False, index=True)

    utym: Mapped[Utym] = relationship(back_populates="occupancy_events")
    camera: Mapped[Camera] = relationship(back_populates="occupancy_events")
    table: Mapped[Table] = relationship(back_populates="occupancy_events")
