"""Import helpers for flight test planning data."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import FlightTest, Participant, SessionParticipant, Utym, UtymSession


class FlightTestImportError(ValueError):
    """Raised when a flight test import payload is invalid."""


REQUIRED_TEXT_FIELDS = ("aircraft_name", "test_name")
OPTIONAL_TEXT_FIELDS = ("test_number", "external_reference")
PARTICIPANT_TEXT_FIELDS = ("full_name",)
DEFAULT_UTYM_NAME = "Imported Flight Test UTYM"
DEFAULT_SESSION_STATUS = "planned"


def import_flight_test_json(db: Session, content: str | bytes) -> FlightTest:
    """Validate and import a flight test from a JSON document."""

    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise FlightTestImportError(f"Invalid JSON: {exc.msg}") from exc

    return import_flight_test_payload(db, payload)


def import_flight_test_payload(db: Session, payload: Mapping[str, Any]) -> FlightTest:
    """Create a flight test, participants, assignments, and UTYM session."""

    normalized = _validate_payload(payload)

    utym = _get_or_create_utym(db, normalized["utym_name"], normalized.get("utym_location"))
    flight_test = FlightTest(
        aircraft_name=normalized["aircraft_name"],
        test_name=normalized["test_name"],
        test_number=normalized.get("test_number"),
        planned_start_time=normalized.get("planned_start_time"),
        planned_end_time=normalized.get("planned_end_time"),
        external_reference=normalized.get("external_reference"),
    )
    db.add(flight_test)
    db.flush()

    utym_session = UtymSession(
        flight_test=flight_test,
        utym=utym,
        start_time=normalized.get("planned_start_time"),
        end_time=normalized.get("planned_end_time"),
        status=DEFAULT_SESSION_STATUS,
    )
    db.add(utym_session)
    db.flush()

    for participant_data in normalized["participants"]:
        participant = _get_or_create_participant(db, participant_data)
        db.add(SessionParticipant(utym_session=utym_session, participant=participant))

    db.commit()
    db.refresh(flight_test)
    return flight_test


def _validate_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise FlightTestImportError("Import document must be a JSON object.")

    normalized: dict[str, Any] = {}
    for field in REQUIRED_TEXT_FIELDS:
        normalized[field] = _required_text(payload, field)
    for field in OPTIONAL_TEXT_FIELDS:
        normalized[field] = _optional_text(payload, field)

    normalized["planned_start_time"] = _optional_datetime(payload, "planned_start_time")
    normalized["planned_end_time"] = _optional_datetime(payload, "planned_end_time")
    if (
        normalized["planned_start_time"] is not None
        and normalized["planned_end_time"] is not None
        and normalized["planned_end_time"] < normalized["planned_start_time"]
    ):
        raise FlightTestImportError("planned_end_time cannot be before planned_start_time.")

    participants = payload.get("participants")
    if participants is None:
        participants = []
    if not isinstance(participants, Sequence) or isinstance(participants, (str, bytes, bytearray)):
        raise FlightTestImportError("participants must be an array.")
    normalized["participants"] = [_validate_participant(item, index) for index, item in enumerate(participants)]

    normalized["utym_name"] = _optional_text(payload, "utym_name") or DEFAULT_UTYM_NAME
    normalized["utym_location"] = _optional_text(payload, "utym_location")
    return normalized


def _validate_participant(item: Any, index: int) -> dict[str, str | None]:
    if not isinstance(item, Mapping):
        raise FlightTestImportError(f"participants[{index}] must be an object.")
    normalized: dict[str, str | None] = {}
    for field in PARTICIPANT_TEXT_FIELDS:
        normalized[field] = _required_text(item, field, prefix=f"participants[{index}].")
    normalized["organization"] = _optional_text(item, "organization")
    normalized["role"] = _optional_text(item, "role")
    normalized["external_reference"] = _optional_text(item, "external_reference")
    return normalized


def _required_text(payload: Mapping[str, Any], field: str, prefix: str = "") -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise FlightTestImportError(f"{prefix}{field} is required and must be a non-empty string.")
    return value.strip()


def _optional_text(payload: Mapping[str, Any], field: str) -> str | None:
    value = payload.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise FlightTestImportError(f"{field} must be a string when provided.")
    stripped = value.strip()
    return stripped or None


def _optional_datetime(payload: Mapping[str, Any], field: str) -> datetime | None:
    value = payload.get(field)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise FlightTestImportError(f"{field} must be an ISO-8601 string when provided.")
    try:
        return datetime.fromisoformat(value.strip().replace("Z", "+00:00")).astimezone(UTC).replace(tzinfo=None)
    except ValueError as exc:
        raise FlightTestImportError(f"{field} must be a valid ISO-8601 datetime.") from exc


def _get_or_create_utym(db: Session, name: str, location: str | None) -> Utym:
    utym = db.scalar(select(Utym).where(Utym.name == name))
    if utym is not None:
        return utym
    utym = Utym(name=name, location=location)
    db.add(utym)
    db.flush()
    return utym


def _get_or_create_participant(db: Session, data: Mapping[str, str | None]) -> Participant:
    conditions = [Participant.full_name == data["full_name"]]
    if data.get("organization") is None:
        conditions.append(Participant.organization.is_(None))
    else:
        conditions.append(Participant.organization == data["organization"])
    participant = db.scalar(select(Participant).where(*conditions))
    if participant is not None:
        return participant
    participant = Participant(
        full_name=data["full_name"] or "",
        organization=data.get("organization"),
        role=data.get("role"),
        external_reference=data.get("external_reference"),
    )
    db.add(participant)
    db.flush()
    return participant
