from app.local_assets import calibration_path, model_path
from app.api.routes_product import _asset_paths
from app.api.routes_tables import _default_calibration_config_path, save_calibration_config
from app.product_check import check_product_assets


def test_local_asset_paths_can_be_overridden(monkeypatch, tmp_path):
    config = tmp_path / "calibration.json"
    model = tmp_path / "detector.onnx"
    monkeypatch.setenv("FTMC_TUTYM2_CONFIG_PATH", str(config))
    monkeypatch.setenv("FTMC_PERSON_MODEL_PATH", str(model))

    assert calibration_path() == config
    assert model_path() == model
    assert _default_calibration_config_path() == config
    assert _asset_paths() == (config, model)


def test_saved_calibration_is_immediately_used_by_readiness(monkeypatch, tmp_path):
    config = tmp_path / "tutym2.local.json"
    model = tmp_path / "detector.onnx"
    model.write_bytes(b"test model")
    monkeypatch.setenv("FTMC_TUTYM2_CONFIG_PATH", str(config))
    monkeypatch.setenv("FTMC_PERSON_MODEL_PATH", str(model))
    tables = [
        {
            "table_id": f"T-{index:03d}",
            "name": f"Masa {index}",
            "capacity": 1,
            "polygon": [[index * 10, 10], [index * 10 + 5, 10], [index * 10 + 5, 20]],
        }
        for index in range(1, 15)
    ]

    save_calibration_config(
        {
            "utym_id": "T.UTYM#2",
            "camera_id": "TUTYM2-CAM-001",
            "source_type": "rtsp",
            "stream_url": "LOCAL_ONLY_DO_NOT_COMMIT_REAL_RTSP_URL",
            "resolution": {"width": 1920, "height": 1080},
            "tables": tables,
        }
    )
    result = check_product_assets(config, model, session_factory=lambda *args, **kwargs: object())

    assert result["ready_for_video_test"] is True
    assert result["status"] == "READY"
