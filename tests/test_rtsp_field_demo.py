from argparse import Namespace
from pathlib import Path

import pytest

from app.field_demo import FieldDemoPreflightError
from app.rtsp_field_demo import validate_inputs, _write_rtsp_report


def _args(tmp_path: Path, stream_url: str = "rtsp://user:pass@camera.local/stream") -> Namespace:
    config = tmp_path / "tutym2_cam_001.rtsp.local.json"
    model = tmp_path / "person_detector.onnx"
    config.write_text(
        '{"utym_id":"T.UTYM#2","camera_id":"TUTYM2-CAM-001",'
        f'"source_type":"rtsp","stream_url":"{stream_url}",'
        '"resolution":{"width":1920,"height":1080},"tables":[]}'
    )
    model.write_bytes(b"model")
    return Namespace(
        config=str(config),
        model=str(model),
        confidence_threshold=0.5,
        iou_threshold=0.45,
        window_name="rtsp demo",
        report_output=None,
    )


def test_validate_inputs_accepts_local_rtsp_config(tmp_path: Path) -> None:
    inputs = validate_inputs(_args(tmp_path))

    assert inputs.camera_id == "TUTYM2-CAM-001"
    assert inputs.config.name == "tutym2_cam_001.rtsp.local.json"


def test_validate_inputs_rejects_placeholder_rtsp_url(tmp_path: Path) -> None:
    args = _args(tmp_path, "rtsp://<USER>:<PASSWORD>@<CAMERA_IP>/<STREAM_PATH>")

    with pytest.raises(FieldDemoPreflightError, match="placeholder"):
        validate_inputs(args)


def test_validate_inputs_rejects_non_json_report_output(tmp_path: Path) -> None:
    args = _args(tmp_path)
    args.report_output = str(tmp_path / "reports" / "rtsp_result.txt")

    with pytest.raises(FieldDemoPreflightError, match="Report output must be a .json file"):
        validate_inputs(args)


def test_write_rtsp_report_omits_stream_url_and_full_paths(tmp_path: Path) -> None:
    args = _args(tmp_path)
    args.report_output = str(tmp_path / "reports" / "rtsp_result.json")
    inputs = validate_inputs(args)

    _write_rtsp_report(inputs, status="completed", exit_code=0)

    text = Path(args.report_output).read_text()
    assert "completed" in text
    assert "TUTYM2-CAM-001" in text
    assert "rtsp://" not in text
    assert str(tmp_path) not in text
