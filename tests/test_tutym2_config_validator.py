import json

import pytest

from app.tutym2_config_validator import Tutym2ConfigValidationError, validate_config, validate_config_file


def _table(index):
    left = 10 + index * 5
    return {
        "table_id": f"T-{index:03d}",
        "name": f"Masa {index}",
        "capacity": 1,
        "polygon": [[left, 10], [left + 10, 10], [left + 10, 20], [left, 20]],
    }


def _valid_config():
    return {
        "utym_id": "T.UTYM#2",
        "camera_id": "TUTYM2-CAM-001",
        "source_type": "rtsp",
        "stream_url": "LOCAL_ONLY_DO_NOT_COMMIT_REAL_RTSP_URL",
        "resolution": {"width": 1920, "height": 1080},
        "tables": [_table(index) for index in range(1, 15)],
    }


def test_validate_config_accepts_safe_template_config():
    result = validate_config(_valid_config())

    assert result.table_count == 14
    assert result.stream_url_mode == "local_only_placeholder"
    assert result.to_safe_dict()["status"] == "valid"


def test_validate_config_file_loads_json(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(_valid_config()), encoding="utf-8")

    assert validate_config_file(path).camera_id == "TUTYM2-CAM-001"


def test_validate_config_rejects_real_rtsp_without_flag():
    payload = _valid_config()
    payload["stream_url"] = "rtsp://user:pass@10.0.0.1/stream"

    with pytest.raises(Tutym2ConfigValidationError, match="Real RTSP URL"):
        validate_config(payload)


def test_validate_config_allows_real_rtsp_with_local_flag():
    payload = _valid_config()
    payload["stream_url"] = "rtsp://user:pass@10.0.0.1/stream"

    assert validate_config(payload, allow_real_rtsp=True).stream_url_mode == "real_rtsp_local_only"


def test_validate_config_rejects_wrong_table_count():
    payload = _valid_config()
    payload["tables"] = payload["tables"][:-1]

    with pytest.raises(Tutym2ConfigValidationError, match="14 records"):
        validate_config(payload)


def test_validate_config_rejects_wrong_capacity():
    payload = _valid_config()
    payload["tables"][0]["capacity"] = 2

    with pytest.raises(Tutym2ConfigValidationError, match="capacity"):
        validate_config(payload)


def test_validate_config_rejects_duplicate_table_id():
    payload = _valid_config()
    payload["tables"][1]["table_id"] = payload["tables"][0]["table_id"]

    with pytest.raises(Tutym2ConfigValidationError, match="Duplicate"):
        validate_config(payload)


def test_validate_config_rejects_polygon_outside_resolution():
    payload = _valid_config()
    payload["tables"][0]["polygon"][0] = [2000, 10]

    with pytest.raises(Tutym2ConfigValidationError, match="between 0 and 1920"):
        validate_config(payload)
