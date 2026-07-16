import json

import pytest

from app.dashboard_state_validator import DashboardStateValidationError, validate_dashboard_state, validate_dashboard_state_file


def _valid_state():
    tables = []
    for index in range(1, 15):
        state = "occupied" if index <= 6 else "empty"
        tables.append(
            {
                "table_id": f"table_{index:02d}",
                "display_name": f"Masa {index:02d}",
                "state": state,
                "confidence": 0.9,
                "label": "TP" if state == "occupied" else "TN",
                "color": "red_or_orange" if state == "occupied" else "green",
                "warning": None,
            }
        )
    return {
        "report_type": "dashboard_state",
        "site": "T.UTYM#2",
        "camera_id": "TUTYM2-CAM-001",
        "overall_status": "normal",
        "connection_status": "connected",
        "average_fps": 8.3,
        "table_summary": {"total": 14, "occupied": 6, "empty": 8, "unknown": 0, "no_data": 0},
        "tables": tables,
        "warnings": [],
        "criticals": [],
        "sources": {
            "offline_readiness": {"status": "loaded", "name": "offline_readiness.json"},
            "config_validation": {"status": "loaded", "name": "config_validation_summary.json"},
            "rtsp_connection": {"status": "loaded", "name": "rtsp_connection_test.json"},
            "table_accuracy": {"status": "loaded", "name": "tutym2_table_accuracy_report.json"},
        },
        "safety": {
            "contains_rtsp_url": False,
            "contains_credentials": False,
            "contains_image_or_video": False,
            "contains_full_local_path": False,
        },
    }


def test_validate_dashboard_state_accepts_valid_state():
    validate_dashboard_state(_valid_state())


def test_validate_dashboard_state_file_loads_json(tmp_path):
    path = tmp_path / "dashboard_state.json"
    path.write_text(json.dumps(_valid_state()), encoding="utf-8")

    validate_dashboard_state_file(path)


def test_validate_dashboard_state_rejects_bad_overall_status():
    payload = _valid_state()
    payload["overall_status"] = "bad"

    with pytest.raises(DashboardStateValidationError, match="overall_status"):
        validate_dashboard_state(payload)


def test_validate_dashboard_state_rejects_wrong_table_count():
    payload = _valid_state()
    payload["tables"] = payload["tables"][:-1]

    with pytest.raises(DashboardStateValidationError, match="14 records"):
        validate_dashboard_state(payload)


def test_validate_dashboard_state_rejects_summary_mismatch():
    payload = _valid_state()
    payload["table_summary"]["occupied"] = 99

    with pytest.raises(DashboardStateValidationError, match="counts must add up"):
        validate_dashboard_state(payload)


def test_validate_dashboard_state_rejects_safety_true():
    payload = _valid_state()
    payload["safety"]["contains_rtsp_url"] = True

    with pytest.raises(DashboardStateValidationError, match="contains_rtsp_url"):
        validate_dashboard_state(payload)


def test_validate_dashboard_state_rejects_missing_source():
    payload = _valid_state()
    del payload["sources"]["rtsp_connection"]

    with pytest.raises(DashboardStateValidationError, match="sources missing"):
        validate_dashboard_state(payload)
