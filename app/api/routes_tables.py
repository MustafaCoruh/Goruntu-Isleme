"""Table listing routes for the FastAPI application."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.database.models import Table

router = APIRouter(tags=["tables"])


def _parse_polygon(polygon_json: str) -> Any:
    """Decode a stored table polygon, preserving invalid legacy values as text."""

    try:
        return json.loads(polygon_json)
    except json.JSONDecodeError:
        return polygon_json


@router.get("/tables")
def list_tables(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Return configured tables ordered by their primary key."""

    tables = db.execute(select(Table).order_by(Table.id)).scalars().all()
    return [
        {
            "id": table.id,
            "utym_id": table.utym_id,
            "camera_id": table.camera_id,
            "name": table.name,
            "capacity": table.capacity,
            "polygon": _parse_polygon(table.polygon_json),
            "created_at": table.created_at.isoformat(),
        }
        for table in tables
    ]
