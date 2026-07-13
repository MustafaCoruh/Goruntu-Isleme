from argparse import Namespace
from pathlib import Path

import pytest

from app.field_demo import (
    FieldDemoPreflightError,
    build_app_main_argv,
    validate_inputs,
)


def _args(tmp_path: Path, source_name: str = "sample.jpg") -> Namespace:
    config = tmp_path / "tutym2_cam_001.local.json"
    source = tmp_path / source_name
    model = tmp_path / "person_detector.onnx"
    config.write_text("{}")
    source.write_bytes(b"field-demo-test-source")
    model.write_bytes(b"field-demo-test-model")
    return Namespace(
        config=str(config),
        source=str(source),
        model=str(model),
        confidence_threshold=0.5,
        iou_threshold=0.45,
        window_name="demo",
    )


def test_validate_inputs_accepts_local_photo_source(tmp_path: Path) -> None:
    inputs = validate_inputs(_args(tmp_path, "sample.jpg"))

    assert inputs.config.name == "tutym2_cam_001.local.json"
    assert inputs.source.name == "sample.jpg"
    assert inputs.model.name == "person_detector.onnx"


def test_validate_inputs_accepts_local_video_source(tmp_path: Path) -> None:
    inputs = validate_inputs(_args(tmp_path, "sample.mp4"))

    assert inputs.source.name == "sample.mp4"


def test_validate_inputs_rejects_missing_model(tmp_path: Path) -> None:
    args = _args(tmp_path)
    Path(args.model).unlink()

    with pytest.raises(FieldDemoPreflightError, match="Missing ONNX person detector model"):
        validate_inputs(args)


def test_validate_inputs_rejects_unsupported_source_extension(tmp_path: Path) -> None:
    args = _args(tmp_path, "source.txt")

    with pytest.raises(FieldDemoPreflightError, match="Unsupported source extension"):
        validate_inputs(args)


def test_build_app_main_argv_forwards_paths_and_thresholds(tmp_path: Path) -> None:
    inputs = validate_inputs(_args(tmp_path, "sample.png"))

    argv = build_app_main_argv(inputs)

    assert argv[:6] == [
        "--config",
        str(inputs.config),
        "--source",
        str(inputs.source),
        "--model",
        str(inputs.model),
    ]
    assert "--confidence-threshold" in argv
    assert "--iou-threshold" in argv
