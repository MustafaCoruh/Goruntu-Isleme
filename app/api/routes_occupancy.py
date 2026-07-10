"""Occupancy routes for current states and historical events."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.database.models import OccupancyEvent

router = APIRouter(prefix="/occupancy", tags=["occupancy"])


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
def get_current_occupancy(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Return the most recent occupancy event for each table."""

    latest_per_table = (
        select(
            OccupancyEvent.table_id,
            func.max(OccupancyEvent.detected_at).label("latest_detected_at"),
        )
        .group_by(OccupancyEvent.table_id)
        .subquery()
    )
    latest_ids = (
        select(func.max(OccupancyEvent.id).label("latest_id"))
        .join(
            latest_per_table,
            (OccupancyEvent.table_id == latest_per_table.c.table_id)
            & (OccupancyEvent.detected_at == latest_per_table.c.latest_detected_at),
        )
        .group_by(OccupancyEvent.table_id)
        .subquery()
    )
    statement = (
        select(OccupancyEvent)
        .join(latest_ids, OccupancyEvent.id == latest_ids.c.latest_id)
        .order_by(OccupancyEvent.table_id)
    )
    events = db.execute(statement).scalars().all()
    return [_event_to_dict(event) for event in events]


@router.get("/events")
def list_occupancy_events(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Return historical occupancy events from newest to oldest."""

    events = db.execute(_events_statement()).scalars().all()
    return [_event_to_dict(event) for event in events]
