"""Headless local-video inference for the T.UTYM#2 dashboard."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from app.calibration.models import CameraConfig, UtymConfig
from app.config import load_camera_config
from app.vision.detector import PersonDetector
from app.vision.hog_detector import OpenCvHogPersonDetector
from app.vision.occupancy import OccupancySmoother, TableOccupancy, compute_table_occupancy
from app.vision.onnx_detector import OnnxPersonDetector, OnnxPersonDetectorConfig


def extract_video_frame(
    source_path: Path,
    timestamp_seconds: float = 0,
    *,
    capture_factory: Callable[[str], Any] | None = None,
    encode_frame: Callable[[str, Any], tuple[bool, Any]] | None = None,
) -> tuple[bytes, int, int]:
    """Decode one frame for browser-independent calibration preview."""

    if timestamp_seconds < 0:
        raise ValueError("timestamp_seconds cannot be negative")
    if capture_factory is None or encode_frame is None:
        import cv2

        capture_factory = capture_factory or cv2.VideoCapture
        encode_frame = encode_frame or cv2.imencode

    capture = capture_factory(str(source_path))
    if not capture.isOpened():
        capture.release()
        raise RuntimeError("Video açılamadı.")
    try:
        if timestamp_seconds:
            capture.set(0, timestamp_seconds * 1000)
        ok, frame = capture.read()
        if not ok or frame is None:
            raise RuntimeError("Videodan kalibrasyon karesi okunamadı.")
        encoded, buffer = encode_frame(".jpg", frame)
        if not encoded:
            raise RuntimeError("Kalibrasyon karesi JPEG biçimine dönüştürülemedi.")
        height, width = frame.shape[:2]
        return buffer.tobytes(), int(width), int(height)
    finally:
        capture.release()


def process_video(
    source_path: Path,
    config_path: Path,
    model_path: Path,
    *,
    max_frames: int = 600,
    frame_stride: int = 3,
    capture_factory: Callable[[str], Any] | None = None,
    detector: PersonDetector | None = None,
) -> dict[str, Any]:
    """Process sampled video frames and return the latest 14-table snapshot."""

    if max_frames <= 0 or frame_stride <= 0:
        raise ValueError("max_frames and frame_stride must be positive")

    camera = _select_camera(load_camera_config(config_path))
    if capture_factory is None:
        import cv2

        capture_factory = cv2.VideoCapture
    if detector is None:
        detector = _create_detector(model_path)

    capture = capture_factory(str(source_path))
    if not capture.isOpened():
        capture.release()
        raise RuntimeError("Video açılamadı.")

    smoother = OccupancySmoother()
    latest: list[TableOccupancy] = []
    read_frames = 0
    processed_frames = 0
    try:
        while read_frames < max_frames:
            ok, frame = capture.read()
            if not ok or frame is None:
                break
            read_frames += 1
            if (read_frames - 1) % frame_stride:
                continue
            latest = smoother.smooth(
                compute_table_occupancy(camera.tables, detector.detect(frame), camera.camera_id)
            )
            processed_frames += 1
    finally:
        capture.release()

    if processed_frames == 0:
        raise RuntimeError("Videodan işlenebilir kare okunamadı.")

    names = {table.table_id: table.name for table in camera.tables}
    return {
        "utym_id": camera.utym_id or "T.UTYM#2",
        "camera_id": camera.camera_id,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "processed_frames": processed_frames,
        "tables": [
            {
                "table_id": item.table_id,
                "name": names.get(item.table_id, item.table_id),
                "status": item.status,
                "confidence": item.confidence,
            }
            for item in latest
        ],
    }


def _create_detector(model_path: Path) -> PersonDetector:
    try:
        backend = OnnxPersonDetector(OnnxPersonDetectorConfig(model_path=str(model_path)))
    except Exception:
        backend = OpenCvHogPersonDetector()
    return PersonDetector(backend)


def _select_camera(config: UtymConfig | CameraConfig) -> CameraConfig:
    if isinstance(config, CameraConfig):
        return config
    if not config.cameras:
        raise ValueError("Config içinde kamera bulunamadı.")
    return config.cameras[0]
