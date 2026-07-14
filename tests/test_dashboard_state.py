import json

from app.dashboard_state import build_dashboard_state


def _write(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_build_dashboard_state_handles_missing_reports(tmp_path):
    state = build_dashboard_state(tmp_path)

    assert state["overall_status"] == "not_ready"
    assert state["table_summary"]["no_data"] == 14
    assert len(state["tables"]) == 14


def test_build_dashboard_state_combines_valid_reports(tmp_path):
    _write(tmp_path / "offline_readiness.json", {"overall_status": "pass", "safety": {"contains_rtsp_url": False}})
    _write(
        tmp_path / "config_validation_summary.json",
        {"status": "valid", "table_count": 14, "resolution": {"width": 1920, "height": 1080}},
    )
    _write(
        tmp_path / "rtsp_connection_test.json",
        {
            "status": "connection_test_completed",
            "details": {"requested_frames": 10, "frames_read": 10, "average_fps": 8.3},
            "safety": {"contains_rtsp_url": False},
        },
    )
    tables = [
        {"table_id": f"table_{index:02d}", "prediction": "occupied" if index <= 6 else "empty", "label": "TP", "confidence": 0.9}
        for index in range(1, 15)
    ]
    _write(
        tmp_path / "tutym2_table_accuracy_report.json",
        {"summary": {"accuracy": 0.95, "fn": 0}, "tables": tables, "safety": {"contains_rtsp_url": False}},
    )

    state = build_dashboard_state(tmp_path)

    assert state["overall_status"] == "normal"
    assert state["connection_status"] == "connected"
    assert state["average_fps"] == 8.3
    assert state["table_summary"]["occupied"] == 6
    assert state["table_summary"]["empty"] == 8


def test_build_dashboard_state_marks_low_fps_warning(tmp_path):
    _write(
        tmp_path / "rtsp_connection_test.json",
        {"status": "connection_test_completed", "details": {"requested_frames": 10, "frames_read": 10, "average_fps": 2.0}},
    )

    state = build_dashboard_state(tmp_path)

    assert state["overall_status"] == "warning"
    assert any("FPS düşük" in warning for warning in state["warnings"])


def test_build_dashboard_state_marks_zero_frames_critical(tmp_path):
    _write(
        tmp_path / "rtsp_connection_test.json",
        {"status": "connection_test_completed", "details": {"requested_frames": 10, "frames_read": 0, "average_fps": 0}},
    )

    state = build_dashboard_state(tmp_path)

    assert state["overall_status"] == "critical"
    assert state["connection_status"] == "disconnected"


def test_build_dashboard_state_marks_safety_violation_critical(tmp_path):
    _write(tmp_path / "offline_readiness.json", {"overall_status": "pass", "safety": {"contains_rtsp_url": True}})

    state = build_dashboard_state(tmp_path)

    assert state["overall_status"] == "critical"
    assert any("güvenli değil" in critical for critical in state["criticals"])


def test_build_dashboard_state_marks_invalid_json_critical(tmp_path):
    (tmp_path / "offline_readiness.json").write_text("{not-json", encoding="utf-8")

    state = build_dashboard_state(tmp_path)

    assert state["overall_status"] == "critical"
    assert state["sources"]["offline_readiness"]["status"] == "invalid_json"
