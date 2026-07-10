"""Import routes for flight test planning data."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.database.importers import FlightTestImportError, import_flight_test_json

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("/flight-tests", status_code=status.HTTP_201_CREATED)
async def import_flight_test(request: Request, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Import a JSON flight test request body and create related database records."""

    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type and content_type not in {"application/json", "text/json", "application/octet-stream"}:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only JSON files are supported.")

    content = await request.body()
    try:
        flight_test = import_flight_test_json(db, content)
    except FlightTestImportError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    session = flight_test.utym_sessions[0]
    return {
        "flight_test_id": flight_test.id,
        "utym_session_id": session.id,
        "participant_count": len(session.session_participants),
        "status": "imported",
    }
