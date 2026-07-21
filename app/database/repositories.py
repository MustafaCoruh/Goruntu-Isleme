"""Repository helpers for database persistence operations."""

from __future__ import annotations

from datetime import datetime
from typing import Final

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import OccupancyEvent

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
