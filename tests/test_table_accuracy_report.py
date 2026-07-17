import json

import pytest

from app.table_accuracy_report import TableAccuracyReportError, validate_report, validate_report_file


def _valid_report():
    tables = []
    labels = [
        ("occupied", "occupied", "TP"),
        ("empty", "empty", "TN"),
        ("empty", "occupied", "FP"),
        ("occupied", "empty", "FN"),
    ]
    for index in range(1, 15):
        ground_truth, prediction, label = labels[index % len(labels)]
        tables.append(
            {
                "table_id": f"table_{index:02d}",
                "ground_truth": ground_truth,
                "prediction": prediction,
                "label": label,
                "confidence": 0.8,
                "safe_note": "safe technical note",
            }
        )

    return {
        "report_type": "table_accuracy_evaluation",
        "schema_version": "1.0",
        "site": "T.UTYM#2",
        "camera_id": "TUTYM2-CAM-001",
        "created_at": "YYYY-MM-DDTHH:MM:SS",
        "evaluation_context": {
            "test_type": "rtsp_live",
            "lighting": "normal",
            "occupancy_level": "medium",
            "camera_angle_changed": False,
            "calibration_recent": True,
            "duration_minutes": 5,
            "average_fps": 8.3,
        },
        "inputs": {
            "config_name": "tutym2_cam_001.rtsp.local.json",
            "model_name": "person_detector.onnx",
            "model_version": "initial-field-test",
        },
        "summary": {
            "table_count": 14,
            "tp": 3,
            "tn": 4,
            "fp": 4,
            "fn": 3,
            "unk": 0,
            "correct": 7,
            "incorrect": 7,
            "evaluated": 14,
            "accuracy": 0.5,
        },
        "tables": tables,
        "decision": {
            "prototype_ready": False,
            "recommended_next_action": "Continue validation.",
            "requires_recalibration": True,
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


def test_validate_report_accepts_safe_valid_payload():
    result = validate_report(_valid_report())

    assert result.table_count == 14
    assert result.accuracy == 0.5
    assert result.tp == 3
    assert result.to_safe_dict()["status"] == "valid"


def test_validate_report_file_loads_json(tmp_path):
    report_path = tmp_path / "accuracy.json"
    report_path.write_text(json.dumps(_valid_report()), encoding="utf-8")

    assert validate_report_file(report_path).camera_id == "TUTYM2-CAM-001"


def test_validate_report_rejects_sensitive_rtsp_url():
    payload = _valid_report()
    payload["inputs"]["config_name"] = "rtsp://user:pass@example.local/stream"

    with pytest.raises(TableAccuracyReportError, match="Sensitive value"):
        validate_report(payload)


def test_validate_report_rejects_summary_mismatch():
    payload = _valid_report()
    payload["summary"]["tp"] = 99

    with pytest.raises(TableAccuracyReportError, match="summary.tp"):
        validate_report(payload)


def test_validate_report_rejects_wrong_label_for_table_values():
    payload = _valid_report()
    payload["tables"][0]["label"] = "FN"

    with pytest.raises(TableAccuracyReportError, match="label must be"):
        validate_report(payload)


def test_validate_report_rejects_missing_table():
    payload = _valid_report()
    payload["tables"] = payload["tables"][:-1]

    with pytest.raises(TableAccuracyReportError, match="14 records"):
        validate_report(payload)


def test_validate_report_rejects_safety_flag_true():
    payload = _valid_report()
    payload["safety"]["contains_rtsp_url"] = True

    with pytest.raises(TableAccuracyReportError, match="contains_rtsp_url"):
        validate_report(payload)


def test_validate_report_rejects_input_paths():
    payload = _valid_report()
    payload["inputs"]["config_name"] = "C:\\FTMC_FIELD_DATA\\configs\\real.json"

    with pytest.raises(TableAccuracyReportError, match="Sensitive value"):
        validate_report(payload)


def test_validate_report_rejects_local_photo_test_type():
    payload = _valid_report()
    payload["evaluation_context"]["test_type"] = "local_photo"

    with pytest.raises(TableAccuracyReportError, match="evaluation_context.test_type"):
        validate_report(payload)
