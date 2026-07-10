import json
from datetime import datetime

import pytest
from sqlalchemy import select

from app.database.db import Base, create_database_engine, create_session_factory
from app.database.importers import FlightTestImportError, import_flight_test_json
from app.database.models import FlightTest, Participant, SessionParticipant, UtymSession


def _session_factory():
    engine = create_database_engine({"database_url": "sqlite:///:memory:"})
    Base.metadata.create_all(bind=engine)
    return create_session_factory(engine)


def test_import_flight_test_json_creates_flight_session_and_participants() -> None:
    session_factory = _session_factory()
    payload = {
        "aircraft_name": "X",
        "test_name": "Y Flight Test",
        "test_number": "FT-2026-001",
        "planned_start_time": "2026-07-09T09:00:00Z",
        "planned_end_time": "2026-07-09T12:00:00Z",
        "participants": [
            {
                "full_name": "Ahmet Yılmaz",
                "organization": "Test Team",
                "role": "Engineer",
            }
        ],
    }

    with session_factory() as session:
        flight_test = import_flight_test_json(session, json.dumps(payload))
        flight_test_id = flight_test.id

    with session_factory() as session:
        imported = session.get(FlightTest, flight_test_id)
        assert imported is not None
        assert imported.aircraft_name == "X"
        assert imported.test_number == "FT-2026-001"
        assert imported.planned_start_time == datetime(2026, 7, 9, 9, 0, 0)
        utym_session = session.scalar(select(UtymSession).where(UtymSession.flight_test_id == flight_test_id))
        assert utym_session is not None
        assert utym_session.status == "planned"
        assert utym_session.start_time == datetime(2026, 7, 9, 9, 0, 0)
        assignments = session.scalars(select(SessionParticipant)).all()
        assert len(assignments) == 1
        assert assignments[0].participant.full_name == "Ahmet Yılmaz"


def test_import_flight_test_json_matches_existing_participant() -> None:
    session_factory = _session_factory()
    payload = {
        "aircraft_name": "X",
        "test_name": "Y Flight Test",
        "participants": [{"full_name": "Ahmet Yılmaz", "organization": "Test Team"}],
    }

    with session_factory() as session:
        session.add(Participant(full_name="Ahmet Yılmaz", organization="Test Team", role="Engineer"))
        session.commit()
        import_flight_test_json(session, json.dumps(payload))
        participants = session.scalars(select(Participant)).all()

    assert len(participants) == 1


def test_import_flight_test_json_rejects_invalid_payload() -> None:
    session_factory = _session_factory()

    with session_factory() as session:
        with pytest.raises(FlightTestImportError, match="aircraft_name"):
            import_flight_test_json(session, json.dumps({"test_name": "Missing aircraft"}))
