"""Occupancy routes for current states and historical events."""

from __future__ import annotations

from copy import deepcopy
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


def _event_to_dict(event: OccupancyEvent) -> dict[str, Any]:
    return {
        "id": event.id,
        "utym_id": event.utym_id,
        "camera_id": event.camera_id,
        "table_id": event.table_id,
        "status": event.status,
        "confidence": event.confidence,
        "detected_at": event.detected_at.isoformat(),
    }


def _events_statement() -> Select[tuple[OccupancyEvent]]:
    return select(OccupancyEvent).order_by(
        OccupancyEvent.detected_at.desc(),
        OccupancyEvent.id.desc(),
    )


@router.get("/current")
def get_current_occupancy() -> dict[str, Any]:
    """Return the latest in-memory occupancy snapshot."""

    return deepcopy(CURRENT_OCCUPANCY_SNAPSHOT)


@router.get("/events")
def list_occupancy_events(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Return historical occupancy events from newest to oldest."""

    events = db.execute(_events_statement()).scalars().all()
    return [_event_to_dict(event) for event in events]
