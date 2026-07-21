from pathlib import Path

import pytest

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

from app.calibration.models import CameraConfig, Point, Resolution, TablePolygon
from app.main import (
    DemoRunnerError,
    VideoFileSource,
    _build_source,
    _field_error_message,
    _run_demo_loop,
)
from app.vision.detector import Detection, PERSON_CLASS_NAME


class FakeDetector:
    def detect(self, frame):
        return [
            Detection(class_name=PERSON_CLASS_NAME, confidence=0.9, bbox=[1, 1, 4, 4])
        ]


def _camera_config() -> CameraConfig:
    return CameraConfig(
        utym_id="T.UTYM#2",
        camera_id="TUTYM2-CAM-001",
        resolution=Resolution(width=20, height=20),
        tables=(
            TablePolygon(
                table_id="T-001",
                name="Masa 1",
                capacity=1,
                polygon=(Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)),
            ),
        ),
    )


def test_build_source_accepts_video_file_extensions(tmp_path: Path) -> None:
    source = _build_source(tmp_path / "sample.mp4")

    assert isinstance(source, VideoFileSource)


def test_build_source_reports_supported_local_file_types(tmp_path: Path) -> None:
    with pytest.raises(DemoRunnerError, match="Supported image extensions"):
        _build_source(tmp_path / "sample.bmp")


def test_run_demo_loop_processes_single_image_and_writes_overlay(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "sample.jpg"
    output_path = tmp_path / "reports" / "overlay.jpg"
    frame = np.zeros((20, 20, 3), dtype=np.uint8)
    assert cv2.imwrite(str(image_path), frame)

    _run_demo_loop(
        camera_config=_camera_config(),
        source=_build_source(image_path),
        detector=FakeDetector(),
        window_name="test",
        output_path=output_path,
        show_window=False,
    )

    assert output_path.exists()
    overlay = cv2.imread(str(output_path), cv2.IMREAD_COLOR)
    assert overlay is not None
    assert overlay.sum() > 0


def test_field_error_message_includes_windows_paths() -> None:
    message = _field_error_message(DemoRunnerError("Config path was not found"))

    assert r"C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json" in message
    assert r"C:\FTMC_FIELD_DATA\input\photos\sample.jpg" in message
    assert r"C:\FTMC_FIELD_DATA\models\person_detector.onnx" in message
