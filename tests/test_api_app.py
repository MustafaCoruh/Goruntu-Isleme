from datetime import datetime, timedelta

from app.api.app import app
from app.api.routes_health import get_health
from app.api.routes_occupancy import get_current_occupancy, list_occupancy_events
from app.api.routes_tables import list_tables
from app.database.db import Base, create_database_engine, create_session_factory
from app.database.models import Camera, OccupancyEvent, Table, Utym


def _session_factory():
    engine = create_database_engine({"database_url": "sqlite:///:memory:"})
    Base.metadata.create_all(bind=engine)
    return create_session_factory(engine)


def _seed_api_data(session_factory):
    with session_factory() as session:
        utym = Utym(name="UTYM 1", location="Test")
        camera = Camera(name="Camera 1", source_type="file", utym=utym)
        table_1 = Table(
            name="Table 1",
            capacity=4,
            polygon_json='[[0, 0], [1, 0], [1, 1]]',
            utym=utym,
            camera=camera,
        )
        table_2 = Table(
            name="Table 2",
            capacity=2,
            polygon_json="[]",
            utym=utym,
            camera=camera,
        )
        session.add_all([utym, camera, table_1, table_2])
        session.flush()
        detected_at = datetime(2026, 7, 10, 12, 0, 0)
        session.add_all(
            [
                OccupancyEvent(
                    utym_id=utym.id,
                    camera_id=camera.id,
                    table_id=table_1.id,
                    status="empty",
                    confidence=0.9,
                    detected_at=detected_at,
                ),
                OccupancyEvent(
                    utym_id=utym.id,
                    camera_id=camera.id,
                    table_id=table_1.id,
                    status="occupied",
                    confidence=0.95,
                    detected_at=detected_at + timedelta(seconds=1),
                ),
                OccupancyEvent(
                    utym_id=utym.id,
                    camera_id=camera.id,
                    table_id=table_2.id,
                    status="uncertain",
                    confidence=0.5,
                    detected_at=detected_at,
                ),
            ]
        )
        session.commit()


def test_app_registers_expected_routes() -> None:
    route_paths = set(app.openapi()["paths"])

    assert {"/health", "/tables", "/occupancy/current", "/occupancy/events"}.issubset(route_paths)


def test_health_endpoint_returns_ok() -> None:
    assert get_health() == {"status": "ok"}


def test_tables_endpoint_lists_configured_tables() -> None:
    session_factory = _session_factory()
    _seed_api_data(session_factory)

    with session_factory() as session:
        response = list_tables(session)

    assert [table["name"] for table in response] == ["Table 1", "Table 2"]
    assert response[0]["polygon"] == [[0, 0], [1, 0], [1, 1]]


def test_occupancy_endpoints_return_current_and_historical_events() -> None:
    session_factory = _session_factory()
    _seed_api_data(session_factory)

    with session_factory() as session:
        current_events = get_current_occupancy(session)
        historical_events = list_occupancy_events(session)

    assert [(event["table_id"], event["status"]) for event in current_events] == [
        (1, "occupied"),
        (2, "uncertain"),
    ]
    assert [event["status"] for event in historical_events] == [
        "occupied",
        "uncertain",
        "empty",
    ]
