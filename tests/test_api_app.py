from datetime import datetime, timedelta

from app.api.app import app
from app.api.routes_health import get_health
from app.api.routes_occupancy import (
    CURRENT_OCCUPANCY_SNAPSHOT,
    get_current_occupancy,
    list_occupancy_events,
)
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

    assert {
        "/health",
        "/tables",
        "/occupancy/current",
        "/occupancy/events",
        "/product/readiness",
    }.issubset(route_paths)


def test_product_readiness_endpoint_returns_safe_result(monkeypatch) -> None:
    from app.api import routes_product

    monkeypatch.setattr(
        routes_product,
        "check_product_assets",
        lambda config, model: {
            "ready_for_video_test": False,
            "status": "NOT_READY",
            "checks": [{"name": "person_model", "status": "fail", "message": "Model eksik."}],
            "next_step": "Modeli yükleyin.",
        },
    )

    response = routes_product.get_product_readiness()

    assert response["status"] == "NOT_READY"
    assert response["checks"][0]["message"] == "Model eksik."
    assert "path" not in str(response).lower()


def test_health_endpoint_returns_ok() -> None:
    assert get_health() == {"status": "ok"}


def test_tables_endpoint_lists_configured_tables() -> None:
    session_factory = _session_factory()
    _seed_api_data(session_factory)

    with session_factory() as session:
        response = list_tables(session)

    assert [table["name"] for table in response] == ["Table 1", "Table 2"]
    assert response[0]["polygon"] == [[0, 0], [1, 0], [1, 1]]


def test_current_occupancy_endpoint_returns_in_memory_snapshot() -> None:
    response = get_current_occupancy()

    assert response == CURRENT_OCCUPANCY_SNAPSHOT
    assert response is not CURRENT_OCCUPANCY_SNAPSHOT
    assert response["tables"] is not CURRENT_OCCUPANCY_SNAPSHOT["tables"]


def test_occupancy_events_endpoint_returns_historical_events() -> None:
    session_factory = _session_factory()
    _seed_api_data(session_factory)

    with session_factory() as session:
        historical_events = list_occupancy_events(session)

    assert [event["status"] for event in historical_events] == [
        "occupied",
        "uncertain",
        "empty",
    ]
    assert set(historical_events[0]) == {
        "table_id",
        "status",
        "confidence",
        "detected_at",
    }
    assert historical_events[0]["detected_at"] == "2026-07-10T12:00:01Z"


def test_occupancy_events_endpoint_filters_historical_events() -> None:
    session_factory = _session_factory()
    _seed_api_data(session_factory)

    with session_factory() as session:
        filtered_events = list_occupancy_events(
            session,
            utym_id="UTYM-001",
            camera_id="CAM-001",
            table_id="1",
            start_time="2026-07-10T12:00:01Z",
            end_time="2026-07-10T12:00:01Z",
            status="occupied",
        )

    assert filtered_events == [
        {
            "table_id": 1,
            "status": "occupied",
            "confidence": 0.95,
            "detected_at": "2026-07-10T12:00:01Z",
        }
    ]


def test_debug_routes_are_registered() -> None:
    route_paths = set(app.openapi()["paths"])

    assert {"/debug/state", "/debug/frame.jpg"}.issubset(route_paths)


def test_debug_state_returns_overlay_payload(monkeypatch) -> None:
    from app.api.routes_debug import get_debug_state

    monkeypatch.setenv("FTMC_DEBUG_UI_ENABLED", "true")
    response = get_debug_state()

    assert response["enabled"] is True
    assert response["frame_url"] == "/debug/frame.jpg"
    assert response["detections"][0]["class_name"] == "person"
    assert response["tables"][0]["polygon"] == [[100, 200], [300, 200], [320, 420], [80, 420]]
    assert response["tables"][0]["status"] == "occupied"


def test_debug_state_can_be_disabled_for_operation_mode(monkeypatch) -> None:
    import pytest
    from fastapi import HTTPException

    from app.api.routes_debug import get_debug_state

    monkeypatch.setenv("FTMC_DEBUG_UI_ENABLED", "false")

    with pytest.raises(HTTPException) as error:
        get_debug_state()

    assert error.value.status_code == 404


def test_calibration_config_route_is_registered() -> None:
    route_paths = set(app.openapi()["paths"])

    assert "/calibration/config" in route_paths



def test_default_calibration_config_path_targets_tutym2_windows_field_file(monkeypatch) -> None:
    from app.api.routes_tables import _default_calibration_config_path

    monkeypatch.delenv("FTMC_CALIBRATION_CONFIG_PATH", raising=False)

    assert (
        str(_default_calibration_config_path())
        == r"C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json"
    )

def test_save_calibration_config_writes_validated_json(tmp_path, monkeypatch) -> None:
    from app.api.routes_tables import save_calibration_config

    config_path = tmp_path / "camera-config.json"
    monkeypatch.setenv("FTMC_CALIBRATION_CONFIG_PATH", str(config_path))

    response = save_calibration_config(
        {
            "utym_id": "UTYM-001",
            "camera_id": "CAM-001",
            "resolution": {"width": 640, "height": 480},
            "tables": [
                {
                    "table_id": "T-001",
                    "name": "Masa 1",
                    "capacity": 4,
                    "polygon": [[1, 2], [3, 4], [5, 6]],
                }
            ],
        }
    )

    assert response["path"] == str(config_path)
    assert config_path.exists()


def test_session_assignment_routes_are_registered() -> None:
    route_paths = set(app.openapi()["paths"])

    assert {
        "/sessions/active/assignment",
        "/sessions/active/participants/{session_participant_id}/assignment",
    }.issubset(route_paths)


def test_manual_session_assignment_updates_table_time_and_source() -> None:
    from app.api.routes_sessions import ManualAssignmentRequest, assign_participant_to_table, get_active_session_assignment
    from app.database.models import (
        FlightTest,
        Participant,
        SessionParticipant,
        UtymSession,
    )

    session_factory = _session_factory()
    with session_factory() as session:
        utym = Utym(name="UTYM Assignment", location="Test")
        camera = Camera(name="Camera Assignment", source_type="file", utym=utym)
        table = Table(
            name="Masa 1",
            capacity=2,
            polygon_json="[]",
            utym=utym,
            camera=camera,
        )
        flight_test = FlightTest(aircraft_name="Jet", test_name="Aktif Test")
        utym_session = UtymSession(flight_test=flight_test, utym=utym, status="active")
        participant = Participant(full_name="Ayşe Demir", organization="Test", role="Operatör")
        session_participant = SessionParticipant(utym_session=utym_session, participant=participant)
        session.add_all(
            [
                utym,
                camera,
                table,
                flight_test,
                utym_session,
                participant,
                session_participant,
            ]
        )
        session.commit()
        session_participant_id = session_participant.id
        table_id = table.id

    with session_factory() as session:
        response = assign_participant_to_table(
            session_participant_id,
            ManualAssignmentRequest(table_id=table_id),
            session,
        )
        assert response["assigned_table_id"] == table_id
        assert response["assignment_source"] == "manual"
        assert response["assigned_at"] is not None

    with session_factory() as session:
        state = get_active_session_assignment(session)
        assert state["participants"][0]["assigned_table_name"] == "Masa 1"
        assert state["tables"][0]["assigned_count"] == 1


def test_session_participant_report_route_is_registered() -> None:
    route_paths = set(app.openapi()["paths"])

    assert "/reports/session/{session_id}/participants" in route_paths


def test_session_participant_report_returns_assignment_history() -> None:
    from app.api.routes_reports import get_session_participant_table_history
    from app.database.models import (
        FlightTest,
        Participant,
        SessionParticipant,
        UtymSession,
    )

    session_factory = _session_factory()
    with session_factory() as session:
        utym = Utym(name="UTYM Report", location="Test")
        camera = Camera(name="Camera Report", source_type="file", utym=utym)
        table = Table(
            name="Masa 1",
            capacity=2,
            polygon_json="[]",
            utym=utym,
            camera=camera,
        )
        flight_test = FlightTest(aircraft_name="Jet", test_name="Rapor Test")
        utym_session = UtymSession(
            flight_test=flight_test,
            utym=utym,
            status="completed",
        )
        participant = Participant(
            full_name="Ahmet Yılmaz",
            organization="Test",
            role="Mühendis",
        )
        session_participant = SessionParticipant(
            utym_session=utym_session,
            participant=participant,
            expected_table=table,
            assigned_at=datetime(2026, 7, 9, 9, 5, 0),
            assignment_source="manual",
        )
        session.add_all(
            [
                utym,
                camera,
                table,
                flight_test,
                utym_session,
                participant,
                session_participant,
            ]
        )
        session.commit()
        session_id = utym_session.id
        table_id = table.id

    with session_factory() as session:
        report = get_session_participant_table_history(session_id, session)

    assert report == [
        {
            "participant_name": "Ahmet Yılmaz",
            "table_id": table_id,
            "table_name": "Masa 1",
            "assigned_at": "2026-07-09T09:05:00Z",
            "assignment_source": "manual",
        }
    ]
