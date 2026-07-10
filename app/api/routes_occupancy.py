"""Occupancy routes for current states and historical events."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.database.models import OccupancyEvent

router = APIRouter(prefix="/occupancy", tags=["occupancy"])

# In-memory current occupancy snapshot until live inference or storage is wired in.
CURRENT_OCCUPANCY_SNAPSHOT: dict[str, Any] = {
    "utym_id": "UTYM-001",
    "camera_id": "CAM-001",
    "timestamp": "2026-07-09T10:05:21Z",
    "tables": [
        {
            "table_id": "T-001",
            "name": "Masa 1",
            "status": "occupied",
            "confidence": 0.91,
        },
        {
            "table_id": "T-002",
            "name": "Masa 2",
            "status": "empty",
            "confidence": 0.83,
        },
    ],
}


def _format_detected_at(detected_at: datetime) -> str:
    """Serialize event timestamps with a UTC suffix for API responses."""

    if detected_at.tzinfo is not None:
        detected_at = detected_at.astimezone(UTC).replace(tzinfo=None)
    return f"{detected_at.isoformat()}Z"


def _event_to_dict(event: OccupancyEvent) -> dict[str, Any]:
    return {
        "table_id": event.table_id,
        "status": event.status,
        "confidence": event.confidence,
        "detected_at": _format_detected_at(event.detected_at),
    }


def _parse_datetime_param(value: str | None) -> datetime | None:
    """Parse an ISO-8601 query parameter, accepting trailing Z for UTC."""

    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is not None:
        return parsed.astimezone(UTC).replace(tzinfo=None)
    return parsed


def _parse_identifier_param(value: str | None) -> int | None:
    """Parse numeric IDs, including display-style IDs such as UTYM-001."""

    if value is None:
        return None
    if value.isdecimal():
        return int(value)
    suffix = value.rsplit("-", maxsplit=1)[-1]
    if suffix.isdecimal():
        return int(suffix)
    return None


def _events_statement(
    *,
    utym_id: str | None = None,
    camera_id: str | None = None,
    table_id: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    status: str | None = None,
) -> Select[tuple[OccupancyEvent]]:
    statement = select(OccupancyEvent)

    parsed_utym_id = _parse_identifier_param(utym_id)
    parsed_camera_id = _parse_identifier_param(camera_id)
    parsed_table_id = _parse_identifier_param(table_id)
    parsed_start_time = _parse_datetime_param(start_time)
    parsed_end_time = _parse_datetime_param(end_time)

    if parsed_utym_id is not None:
        statement = statement.where(OccupancyEvent.utym_id == parsed_utym_id)
    if parsed_camera_id is not None:
        statement = statement.where(OccupancyEvent.camera_id == parsed_camera_id)
    if parsed_table_id is not None:
        statement = statement.where(OccupancyEvent.table_id == parsed_table_id)
    if parsed_start_time is not None:
        statement = statement.where(OccupancyEvent.detected_at >= parsed_start_time)
    if parsed_end_time is not None:
        statement = statement.where(OccupancyEvent.detected_at <= parsed_end_time)
    if status is not None:
        statement = statement.where(OccupancyEvent.status == status)

    return statement.order_by(
        OccupancyEvent.detected_at.desc(),
        OccupancyEvent.id.desc(),
    )


@router.get("/current")
def get_current_occupancy() -> dict[str, Any]:
    """Return the latest in-memory occupancy snapshot."""

    return deepcopy(CURRENT_OCCUPANCY_SNAPSHOT)


@router.get("/events")
def list_occupancy_events(
    db: Session = Depends(get_db),
    utym_id: str | None = None,
    camera_id: str | None = None,
    table_id: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Return filtered historical occupancy events from newest to oldest."""

    events = db.execute(
        _events_statement(
            utym_id=utym_id,
            camera_id=camera_id,
            table_id=table_id,
            start_time=start_time,
            end_time=end_time,
            status=status,
        )
    ).scalars().all()
    return [_event_to_dict(event) for event in events]
