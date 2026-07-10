"""Report routes for historical session participant assignments."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import get_db
from app.database.models import SessionParticipant, UtymSession
from app.database.repositories import _format_datetime

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/session/{session_id}/participants")
def get_session_participant_table_history(
    session_id: int,
    db: Session = Depends(get_db),
) -> list[dict[str, object]]:
    """Return participant table-assignment history for a UTYM session."""

    utym_session = db.get(UtymSession, session_id)
    if utym_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )

    statement = (
        select(SessionParticipant)
        .options(
            selectinload(SessionParticipant.participant),
            selectinload(SessionParticipant.expected_table),
        )
        .where(SessionParticipant.utym_session_id == session_id)
        .order_by(
            SessionParticipant.assigned_at.asc().nullslast(),
            SessionParticipant.id.asc(),
        )
    )
    participants = db.scalars(statement).all()

    return [
        {
            "participant_name": participant.participant.full_name,
            "table_id": participant.expected_table.id if participant.expected_table else None,
            "table_name": participant.expected_table.name if participant.expected_table else None,
            "assigned_at": _format_datetime(participant.assigned_at),
            "assignment_source": participant.assignment_source,
        }
        for participant in participants
    ]
