"""Repository helpers for database persistence operations."""

from __future__ import annotations

from datetime import datetime
from typing import Final

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import OccupancyEvent, SessionParticipant, Table, UtymSession, utc_now

OCCUPANCY_STATUSES: Final[set[str]] = {"empty", "occupied", "uncertain"}


class OccupancyEventRepository:
    """Persist occupancy state changes without writing every processed frame.

    The repository stores the first observed state for a table and subsequent
    records only when the state changes. This keeps the event table focused on
    meaningful transitions such as ``empty`` -> ``occupied`` instead of one row
    per frame.
    """

    def __init__(self, session: Session, save_uncertain_events: bool = True) -> None:
        """Create the repository.

        Args:
            session: Active SQLAlchemy session used for reads and writes.
            save_uncertain_events: When ``False``, ``uncertain`` detections are
                ignored and do not create event rows.
        """

        self.session = session
        self.save_uncertain_events = save_uncertain_events

    def save_occupancy_event(
        self,
        table_id: int,
        camera_id: int,
        utym_id: int,
        status: str,
        confidence: float | None,
        detected_at: datetime,
    ) -> OccupancyEvent | None:
        """Save an occupancy event if it represents a new state or transition.

        Returns the newly created :class:`OccupancyEvent`, or ``None`` when the
        last saved event for the same UTYM/camera/table already has the supplied
        status. ``uncertain`` events are also skipped when configured with
        ``save_uncertain_events=False``.
        """

        normalized_status = status.strip().lower()
        if normalized_status not in OCCUPANCY_STATUSES:
            raise ValueError(
                "status must be one of: " + ", ".join(sorted(OCCUPANCY_STATUSES))
            )

        if normalized_status == "uncertain" and not self.save_uncertain_events:
            return None

        latest_event = self._latest_event(table_id, camera_id, utym_id)
        if latest_event is not None and latest_event.status == normalized_status:
            return None

        event = OccupancyEvent(
            table_id=table_id,
            camera_id=camera_id,
            utym_id=utym_id,
            status=normalized_status,
            confidence=confidence,
            detected_at=detected_at,
        )
        self.session.add(event)
        self.session.flush()
        return event

    def _latest_event(
        self, table_id: int, camera_id: int, utym_id: int
    ) -> OccupancyEvent | None:
        statement = (
            select(OccupancyEvent)
            .where(
                OccupancyEvent.table_id == table_id,
                OccupancyEvent.camera_id == camera_id,
                OccupancyEvent.utym_id == utym_id,
            )
            .order_by(OccupancyEvent.detected_at.desc(), OccupancyEvent.id.desc())
            .limit(1)
        )
        return self.session.execute(statement).scalar_one_or_none()


class SessionAssignmentRepository:
    """Read and update manual participant-to-table assignments for sessions."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_active_assignment_state(self) -> dict[str, object] | None:
        """Return the current active session assignment dashboard payload."""

        active_session = self._active_session()
        if active_session is None:
            return None

        return {
            "session": self._serialize_session(active_session),
            "participants": [
                self.serialize_session_participant(session_participant)
                for session_participant in sorted(
                    active_session.session_participants,
                    key=lambda item: (item.participant.full_name.lower(), item.id),
                )
            ],
            "tables": self._serialize_tables(active_session.utym_id),
        }

    def assign_participant_to_table(
        self,
        session_participant_id: int,
        table_id: int,
        assignment_source: str = "manual",
    ):
        """Assign an active-session participant to a table and timestamp it."""

        active_session = self._active_session()
        if active_session is None:
            raise LookupError("No active flight test session found.")

        session_participant = self.session.get(SessionParticipant, session_participant_id)
        if session_participant is None:
            raise LookupError("Session participant not found.")
        if session_participant.utym_session_id != active_session.id:
            raise ValueError("Participant does not belong to the active session.")

        table = self.session.get(Table, table_id)
        if table is None:
            raise LookupError("Table not found.")
        if table.utym_id != active_session.utym_id:
            raise ValueError("Table does not belong to the active session UTYM.")

        session_participant.expected_table_id = table.id
        session_participant.assigned_at = utc_now()
        session_participant.assignment_source = assignment_source
        self.session.flush()
        return session_participant

    def serialize_session_participant(self, session_participant) -> dict[str, object]:
        """Serialize one participant row for the assignment UI."""

        participant = session_participant.participant
        table = session_participant.expected_table
        return {
            "session_participant_id": session_participant.id,
            "participant_id": participant.id,
            "full_name": participant.full_name,
            "organization": participant.organization,
            "role": participant.role,
            "assigned_table_id": table.id if table else None,
            "assigned_table_name": table.name if table else None,
            "assigned_at": _format_datetime(session_participant.assigned_at),
            "assignment_source": session_participant.assignment_source,
        }

    def _active_session(self):
        from sqlalchemy.orm import selectinload

        statement = (
            select(UtymSession)
            .options(
                selectinload(UtymSession.flight_test),
                selectinload(UtymSession.utym),
                selectinload(UtymSession.session_participants)
                .selectinload(SessionParticipant.participant),
                selectinload(UtymSession.session_participants)
                .selectinload(SessionParticipant.expected_table),
            )
            .where(UtymSession.status == "active")
            .order_by(UtymSession.start_time.desc().nullslast(), UtymSession.id.desc())
            .limit(1)
        )
        return self.session.execute(statement).scalar_one_or_none()

    def _serialize_session(self, utym_session) -> dict[str, object]:
        flight_test = utym_session.flight_test
        return {
            "id": utym_session.id,
            "status": utym_session.status,
            "utym_id": utym_session.utym_id,
            "utym_name": utym_session.utym.name,
            "start_time": _format_datetime(utym_session.start_time),
            "end_time": _format_datetime(utym_session.end_time),
            "flight_test": {
                "id": flight_test.id,
                "aircraft_name": flight_test.aircraft_name,
                "test_name": flight_test.test_name,
                "test_number": flight_test.test_number,
                "planned_start_time": _format_datetime(flight_test.planned_start_time),
                "planned_end_time": _format_datetime(flight_test.planned_end_time),
            },
        }

    def _serialize_tables(self, utym_id: int) -> list[dict[str, object]]:
        tables = self.session.scalars(
            select(Table).where(Table.utym_id == utym_id).order_by(Table.name, Table.id)
        ).all()
        return [self._serialize_table(table) for table in tables]

    def _serialize_table(self, table) -> dict[str, object]:
        latest_event = self.session.execute(
            select(OccupancyEvent)
            .where(OccupancyEvent.table_id == table.id)
            .order_by(OccupancyEvent.detected_at.desc(), OccupancyEvent.id.desc())
            .limit(1)
        ).scalar_one_or_none()
        assigned_count = self.session.scalar(
            select(func.count(SessionParticipant.id)).where(
                SessionParticipant.expected_table_id == table.id
            )
        )
        return {
            "id": table.id,
            "name": table.name,
            "capacity": table.capacity,
            "occupancy_status": latest_event.status if latest_event else "unknown",
            "occupancy_confidence": latest_event.confidence if latest_event else None,
            "last_detected_at": _format_datetime(latest_event.detected_at) if latest_event else None,
            "assigned_count": assigned_count or 0,
        }


def _format_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.replace(microsecond=0).isoformat() + "Z"
