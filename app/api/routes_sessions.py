"""Session assignment routes for active flight test operations."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.database.repositories import SessionAssignmentRepository

router = APIRouter(tags=["sessions"])


class ManualAssignmentRequest(BaseModel):
    """Request body for manually assigning a participant to a table."""

    table_id: int = Field(..., gt=0)


@router.get("/sessions/active/assignment")
def get_active_session_assignment(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Return the active flight test session with participants and table occupancy."""

    repository = SessionAssignmentRepository(db)
    assignment_state = repository.get_active_assignment_state()
    if assignment_state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active flight test session found.",
        )

    return assignment_state


@router.post("/sessions/active/participants/{session_participant_id}/assignment")
def assign_participant_to_table(
    session_participant_id: int,
    request: ManualAssignmentRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Manually assign one participant in the active session to a table."""

    repository = SessionAssignmentRepository(db)
    try:
        participant = repository.assign_participant_to_table(
            session_participant_id=session_participant_id,
            table_id=request.table_id,
            assignment_source="manual",
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.commit()
    db.refresh(participant)
    return repository.serialize_session_participant(participant)
