import json

from app.product_check import check_product_assets


def _write_config(path, *, placeholder=False):
    tables = []
    for index in range(1, 15):
        left = index * 10
        table = {
            "table_id": f"T-{index:03d}",
            "name": f"Masa {index}",
            "capacity": 1,
            "polygon": [[left, 10], [left + 5, 10], [left + 5, 20], [left, 20]],
        }
        if placeholder:
            table["notes"] = "PLACEHOLDER_POLYGON"
        tables.append(table)
    path.write_text(
        json.dumps(
            {
                "utym_id": "T.UTYM#2",
                "camera_id": "TUTYM2-CAM-001",
                "source_type": "rtsp",
                "stream_url": "LOCAL_ONLY_DO_NOT_COMMIT_REAL_RTSP_URL",
                "resolution": {"width": 1920, "height": 1080},
                "tables": tables,
            }
        ),
        encoding="utf-8",
    )


def test_product_check_is_ready_with_calibration_and_loadable_model(tmp_path):
    config = tmp_path / "config.json"
    model = tmp_path / "model.onnx"
    _write_config(config)
    model.write_bytes(b"fake model handled by test loader")

    result = check_product_assets(config, model, session_factory=lambda *args, **kwargs: object())

    assert result["ready_for_video_test"] is True
    assert result["status"] == "READY"
    assert all(check["status"] == "pass" for check in result["checks"])
    assert result["next_step"].startswith("Hazır:")


def test_product_check_rejects_placeholder_calibration_and_invalid_model(tmp_path):
    config = tmp_path / "config.json"
    model = tmp_path / "model.onnx"
    _write_config(config, placeholder=True)
    model.write_text("not an ONNX model", encoding="utf-8")

    def reject_model(*args, **kwargs):
        raise ValueError("invalid model")

    result = check_product_assets(config, model, session_factory=reject_model)

    assert result["ready_for_video_test"] is False
    assert result["status"] == "NOT_READY"
    assert {check["name"] for check in result["checks"] if check["status"] == "fail"} == {
        "table_calibration",
        "person_model",
    }
    assert "14 gerçek masa poligonu" in result["next_step"]


def test_product_check_explains_model_is_next_after_calibration(tmp_path):
    config = tmp_path / "config.json"
    model = tmp_path / "model.onnx"
    _write_config(config)
    model.write_text("not an ONNX model", encoding="utf-8")

    result = check_product_assets(
        config,
        model,
        session_factory=lambda *args, **kwargs: (_ for _ in ()).throw(ValueError()),
    )

    assert "Kalibrasyon hazır" in result["next_step"]
    assert "models/person_detector.onnx" in result["next_step"]
