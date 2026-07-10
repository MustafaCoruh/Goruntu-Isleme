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
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )

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
    utym_sessions: Mapped[list[UtymSession]] = relationship(
        back_populates="utym",
        cascade="all, delete-orphan",
    )


class Camera(Base):
    """A camera source configured for a UTYM location."""

    __tablename__ = "camera"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    utym_id: Mapped[int] = mapped_column(
        ForeignKey("utym.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    stream_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )

    utym: Mapped[Utym] = relationship(back_populates="cameras")
    tables: Mapped[list[Table]] = relationship(back_populates="camera")
    occupancy_events: Mapped[list[OccupancyEvent]] = relationship(
        back_populates="camera"
    )


class Table(Base):
    """A calibrated table area observed by a camera."""

    __tablename__ = "table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    utym_id: Mapped[int] = mapped_column(
        ForeignKey("utym.id"), nullable=False, index=True
    )
    camera_id: Mapped[int] = mapped_column(
        ForeignKey("camera.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    polygon_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )

    utym: Mapped[Utym] = relationship(back_populates="tables")
    camera: Mapped[Camera] = relationship(back_populates="tables")
    occupancy_events: Mapped[list[OccupancyEvent]] = relationship(
        back_populates="table"
    )
    expected_session_participants: Mapped[list[SessionParticipant]] = relationship(
        back_populates="expected_table",
        foreign_keys="SessionParticipant.expected_table_id",
    )
    actual_session_participants: Mapped[list[SessionParticipant]] = relationship(
        back_populates="actual_table",
        foreign_keys="SessionParticipant.actual_table_id",
    )


class FlightTest(Base):
    """A planned flight test that may contain one or more UTYM sessions."""

    __tablename__ = "flight_test"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    aircraft_name: Mapped[str] = mapped_column(String(255), nullable=False)
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    test_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    planned_start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    planned_end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    external_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    utym_sessions: Mapped[list[UtymSession]] = relationship(
        back_populates="flight_test",
        cascade="all, delete-orphan",
    )


class UtymSession(Base):
    """A UTYM session recorded during a flight test."""

    __tablename__ = "utym_session"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    flight_test_id: Mapped[int] = mapped_column(
        ForeignKey("flight_test.id"), nullable=False, index=True
    )
    utym_id: Mapped[int] = mapped_column(
        ForeignKey("utym.id"), nullable=False, index=True
    )
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    flight_test: Mapped[FlightTest] = relationship(back_populates="utym_sessions")
    utym: Mapped[Utym] = relationship(back_populates="utym_sessions")
    session_participants: Mapped[list[SessionParticipant]] = relationship(
        back_populates="utym_session",
        cascade="all, delete-orphan",
    )


class Participant(Base):
    """A person or organization representative expected in UTYM sessions."""

    __tablename__ = "participant"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    organization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    session_participants: Mapped[list[SessionParticipant]] = relationship(
        back_populates="participant",
        cascade="all, delete-orphan",
    )


class SessionParticipant(Base):
    """A participant assignment and detected table match for a UTYM session."""

    __tablename__ = "session_participant"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    utym_session_id: Mapped[int] = mapped_column(
        ForeignKey("utym_session.id"), nullable=False, index=True
    )
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participant.id"), nullable=False, index=True
    )
    expected_table_id: Mapped[int | None] = mapped_column(
        ForeignKey("table.id"), nullable=True, index=True
    )
    actual_table_id: Mapped[int | None] = mapped_column(
        ForeignKey("table.id"), nullable=True, index=True
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    utym_session: Mapped[UtymSession] = relationship(
        back_populates="session_participants"
    )
    participant: Mapped[Participant] = relationship(
        back_populates="session_participants"
    )
    expected_table: Mapped[Table | None] = relationship(
        back_populates="expected_session_participants",
        foreign_keys=[expected_table_id],
    )
    actual_table: Mapped[Table | None] = relationship(
        back_populates="actual_session_participants",
        foreign_keys=[actual_table_id],
    )


class OccupancyEvent(Base):
    """A detected occupancy state for a table at a point in time."""

    __tablename__ = "occupancy_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    utym_id: Mapped[int] = mapped_column(
        ForeignKey("utym.id"), nullable=False, index=True
    )
    camera_id: Mapped[int] = mapped_column(
        ForeignKey("camera.id"), nullable=False, index=True
    )
    table_id: Mapped[int] = mapped_column(
        ForeignKey("table.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False, index=True
    )

    utym: Mapped[Utym] = relationship(back_populates="occupancy_events")
    camera: Mapped[Camera] = relationship(back_populates="occupancy_events")
    table: Mapped[Table] = relationship(back_populates="occupancy_events")
