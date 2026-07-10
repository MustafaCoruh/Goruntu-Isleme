from datetime import datetime, timedelta

import pytest

from app.database.db import Base, create_database_engine, create_session_factory
from app.database.models import Camera, OccupancyEvent, Table, Utym
from app.database.repositories import OccupancyEventRepository


def _session_factory():
    engine = create_database_engine({"database_url": "sqlite:///:memory:"})
    Base.metadata.create_all(bind=engine)
    return create_session_factory(engine)


def _seed_table(session):
    utym = Utym(name="UTYM 1", location="Test")
    camera = Camera(name="Camera 1", source_type="file", utym=utym)
    table = Table(
        name="Table 1",
        capacity=4,
        polygon_json="[]",
        utym=utym,
        camera=camera,
    )
    session.add_all([utym, camera, table])
    session.flush()
    return utym, camera, table


def test_save_occupancy_event_records_initial_state_and_transitions_only() -> None:
    session_factory = _session_factory()
    with session_factory() as session:
        utym, camera, table = _seed_table(session)
        repository = OccupancyEventRepository(session)
        detected_at = datetime(2026, 7, 10, 12, 0, 0)

        first_event = repository.save_occupancy_event(
            table.id, camera.id, utym.id, "empty", 1.0, detected_at
        )
        repeated_event = repository.save_occupancy_event(
            table.id,
            camera.id,
            utym.id,
            "empty",
            0.99,
            detected_at + timedelta(seconds=1),
        )
        transition_event = repository.save_occupancy_event(
            table.id,
            camera.id,
            utym.id,
            "occupied",
            0.92,
            detected_at + timedelta(seconds=2),
        )

        events = session.query(OccupancyEvent).order_by(OccupancyEvent.detected_at).all()

    assert first_event is not None
    assert repeated_event is None
    assert transition_event is not None
    assert [event.status for event in events] == ["empty", "occupied"]


def test_save_occupancy_event_can_skip_uncertain_statuses() -> None:
    session_factory = _session_factory()
    with session_factory() as session:
        utym, camera, table = _seed_table(session)
        repository = OccupancyEventRepository(session, save_uncertain_events=False)

        event = repository.save_occupancy_event(
            table.id,
            camera.id,
            utym.id,
            "uncertain",
            0.5,
            datetime(2026, 7, 10, 12, 0, 0),
        )
        event_count = session.query(OccupancyEvent).count()

    assert event is None
    assert event_count == 0


def test_save_occupancy_event_rejects_unknown_status() -> None:
    session_factory = _session_factory()
    with session_factory() as session:
        utym, camera, table = _seed_table(session)
        repository = OccupancyEventRepository(session)

        with pytest.raises(ValueError, match="status must be one of"):
            repository.save_occupancy_event(
                table.id,
                camera.id,
                utym.id,
                "busy",
                0.9,
                datetime(2026, 7, 10, 12, 0, 0),
            )
