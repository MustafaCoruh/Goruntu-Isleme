import json

import pytest

from app.r4_acceptance import R4AcceptanceError, build_r4_acceptance_report


def _dashboard_state(status="normal"):
    states = ["occupied", "empty"] * 7
    return {
        "report_type": "dashboard_state",
        "site": "T.UTYM#2",
        "camera_id": "TUTYM2-CAM-001",
        "overall_status": status,
        "connection_status": "connected",
        "average_fps": 8.0,
        "table_summary": {"total": 14, "occupied": 7, "empty": 7, "unknown": 0, "no_data": 0},
        "tables": [
            {
                "table_id": f"table_{index:02d}",
                "display_name": f"Masa {index:02d}",
                "state": states[index - 1],
                "confidence": 0.9,
                "label": "TP" if states[index - 1] == "occupied" else "TN",
                "color": "red_or_orange" if states[index - 1] == "occupied" else "green",
                "warning": None,
            }
            for index in range(1, 15)
        ],
        "warnings": [],
        "criticals": [],
        "sources": {
            "offline_readiness": {"status": "loaded", "name": "offline_readiness.json"},
            "config_validation": {"status": "loaded", "name": "config_validation.json"},
            "rtsp_connection": {"status": "loaded", "name": "rtsp_connection.json"},
            "table_accuracy": {"status": "loaded", "name": "table_accuracy.json"},
        },
        "safety": {
            "contains_rtsp_url": False,
            "contains_credentials": False,
            "contains_image_or_video": False,
            "contains_full_local_path": False,
        },
    }


def _table_accuracy(accuracy=1.0):
    tables = []
    for index in range(1, 15):
        tables.append(
            {
                "table_id": f"table_{index:02d}",
                "ground_truth": "occupied",
                "prediction": "occupied",
                "label": "TP",
                "confidence": 0.9,
                "safe_note": "safe note",
            }
        )
    if accuracy < 1.0:
        tables[0]["prediction"] = "empty"
        tables[0]["label"] = "FN"
    correct = 13 if accuracy < 1.0 else 14
    return {
        "report_type": "table_accuracy_evaluation",
        "schema_version": "1.0",
        "site": "T.UTYM#2",
        "camera_id": "TUTYM2-CAM-001",
        "evaluation_context": {
            "test_type": "rtsp_live",
            "lighting": "normal",
            "occupancy_level": "medium",
            "camera_angle_changed": False,
            "calibration_recent": True,
            "duration_minutes": 5,
            "average_fps": 8.0,
        },
        "inputs": {
            "config_name": "tutym2_cam_001.rtsp.local.json",
            "model_name": "person_detector.onnx",
            "model_version": "field-test",
        },
        "summary": {
            "table_count": 14,
            "tp": correct,
            "tn": 0,
            "fp": 0,
            "fn": 14 - correct,
            "unk": 0,
            "correct": correct,
            "incorrect": 14 - correct,
            "evaluated": 14,
            "accuracy": correct / 14,
        },
        "tables": tables,
        "decision": {
            "prototype_ready": True,
            "recommended_next_action": "Continue controlled R4.",
            "requires_recalibration": False,
            "requires_model_change": False,
            "requires_camera_adjustment": False,
        },
        "safety": {
            "contains_image_or_video": False,
            "contains_rtsp_url": False,
            "contains_ip_address": False,
            "contains_credentials": False,
            "contains_person_name": False,
            "contains_full_local_path": False,
        },
    }


def _handoff_summary(status="normal"):
    return {
        "report_type": "field_handoff_summary",
        "site": "T.UTYM#2",
        "overall_status": status,
        "report_count": 2,
        "reports": [
            {"label": "dashboard_state", "file_name": "dashboard_state.json", "report_type": "dashboard_state", "status": "normal", "safe_to_share": True},
            {"label": "table_accuracy", "file_name": "table_accuracy.json", "report_type": "table_accuracy_evaluation", "status": "normal", "safe_to_share": True},
        ],
        "shareable_summary": {"site": "T.UTYM#2", "overall_status": status, "report_count": 2, "safe_to_share": True},
        "safety": {
            "contains_rtsp_url": False,
            "contains_credentials": False,
            "contains_ip_address": False,
            "contains_full_local_path": False,
            "contains_image_or_video": False,
        },
    }


def _write(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_build_r4_acceptance_report_ready(tmp_path):
    report = build_r4_acceptance_report(
        dashboard_state_path=_write(tmp_path / "dashboard_state.json", _dashboard_state()),
        handoff_summary_path=_write(tmp_path / "handoff.json", _handoff_summary()),
        table_accuracy_path=_write(tmp_path / "table_accuracy.json", _table_accuracy()),
    )

    assert report["overall_status"] == "ready"
    assert report["ready_for_controlled_field_acceptance"] is True
    assert report["summary"]["table_count"] == 14
    assert report["safety"]["contains_rtsp_url"] is False


def test_build_r4_acceptance_report_ready_with_warnings_for_false_negative(tmp_path):
    report = build_r4_acceptance_report(
        dashboard_state_path=_write(tmp_path / "dashboard_state.json", _dashboard_state()),
        handoff_summary_path=_write(tmp_path / "handoff.json", _handoff_summary()),
        table_accuracy_path=_write(tmp_path / "table_accuracy.json", _table_accuracy(accuracy=0.9)),
    )

    assert report["overall_status"] == "ready_with_warnings"
    assert report["summary"]["false_negative_count"] == 1


def test_build_r4_acceptance_report_rejects_missing_handoff_table_accuracy_label(tmp_path):
    handoff = _handoff_summary()
    handoff["reports"] = handoff["reports"][:1]

    with pytest.raises(R4AcceptanceError, match="missing required report labels"):
        build_r4_acceptance_report(
            dashboard_state_path=_write(tmp_path / "dashboard_state.json", _dashboard_state()),
            handoff_summary_path=_write(tmp_path / "handoff.json", handoff),
            table_accuracy_path=_write(tmp_path / "table_accuracy.json", _table_accuracy()),
        )
