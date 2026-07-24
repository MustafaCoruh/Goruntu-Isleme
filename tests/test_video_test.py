import asyncio
from copy import deepcopy
import json
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.api import routes_product
from app.video_test import _create_detector, extract_video_frame, process_video
from app.vision.detector import Detection


def _write_config(path: Path) -> None:
    tables = []
    for index in range(1, 15):
        left = index * 10
        tables.append(
            {
                "table_id": f"T-{index:03d}",
                "name": f"Masa {index}",
                "capacity": 1,
                "polygon": [[left, 10], [left + 5, 10], [left + 5, 20], [left, 20]],
            }
        )
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


class FakeCapture:
    def __init__(self, frame_count: int = 18) -> None:
        self.frames = [object() for _ in range(frame_count)]
        self.released = False

    def isOpened(self):
        return True

    def read(self):
        return (True, self.frames.pop(0)) if self.frames else (False, None)

    def release(self):
        self.released = True


class EmptyDetector:
    def detect(self, frame):
        return []


class FakeFrame:
    shape = (720, 1280, 3)


class FakeJpegBuffer:
    def tobytes(self):
        return b"jpeg-data"


class FakeFrameCapture:
    def __init__(self):
        self.released = False
        self.position = None

    def isOpened(self):
        return True

    def set(self, key, value):
        self.position = (key, value)

    def read(self):
        return True, FakeFrame()

    def release(self):
        self.released = True


def test_extract_video_frame_seeks_encodes_and_releases(tmp_path):
    capture = FakeFrameCapture()

    jpeg, width, height = extract_video_frame(
        tmp_path / "video.mp4",
        2.5,
        capture_factory=lambda path: capture,
        encode_frame=lambda extension, frame: (True, FakeJpegBuffer()),
    )

    assert jpeg == b"jpeg-data"
    assert (width, height) == (1280, 720)
    assert capture.position == (0, 2500)
    assert capture.released is True


def test_process_video_returns_fourteen_smoothed_table_results(tmp_path):
    config = tmp_path / "config.json"
    _write_config(config)
    capture = FakeCapture()

    result = process_video(
        tmp_path / "video.mp4",
        config,
        tmp_path / "model.onnx",
        capture_factory=lambda path: capture,
        detector=EmptyDetector(),
    )

    assert result["utym_id"] == "T.UTYM#2"
    assert result["camera_id"] == "TUTYM2-CAM-001"
    assert result["processed_frames"] == 6
    assert len(result["tables"]) == 14
    assert all(table["status"] == "empty" for table in result["tables"])
    assert capture.released is True


def test_detector_factory_falls_back_to_offline_hog(monkeypatch, tmp_path):
    class FakeHogBackend:
        def detect(self, frame):
            return [Detection("person", 0.8, [1, 2, 3, 4])]

    monkeypatch.setattr(
        "app.video_test.OnnxPersonDetector",
        lambda config: (_ for _ in ()).throw(RuntimeError("model unavailable")),
    )
    monkeypatch.setattr(
        "app.video_test.OpenCvHogPersonDetector", lambda: FakeHogBackend()
    )

    detector = _create_detector(tmp_path / "missing.onnx")

    assert detector.detect(object())[0].bbox == [1.0, 2.0, 3.0, 4.0]


class FakeRequest:
    def __init__(self, body=b"video", filename="test.mp4", timestamp=None) -> None:
        self.headers = {"x-video-filename": filename}
        if timestamp is not None:
            self.headers["x-video-timestamp"] = str(timestamp)
        self.body = body

    async def stream(self):
        yield self.body


def test_video_endpoint_blocks_upload_until_product_is_ready(monkeypatch):
    monkeypatch.setattr(
        routes_product,
        "check_product_assets",
        lambda config, model: {"ready_for_video_test": False, "next_step": "Model gerekli."},
    )

    with pytest.raises(HTTPException) as error:
        asyncio.run(routes_product.run_video_test(FakeRequest()))

    assert error.value.status_code == 409


def test_video_endpoint_processes_and_deletes_temporary_file(monkeypatch):
    monkeypatch.setattr(
        routes_product,
        "check_product_assets",
        lambda config, model: {"ready_for_video_test": True},
    )
    temporary_paths = []

    def fake_process(path, config, model):
        temporary_paths.append(path)
        assert path.exists()
        return {
            "utym_id": "T.UTYM#2",
            "camera_id": "TUTYM2-CAM-001",
            "timestamp": "2026-07-17T12:00:00Z",
            "processed_frames": 8,
            "tables": [{"table_id": "T-001", "name": "Masa 1", "status": "empty", "confidence": 1.0}],
        }

    monkeypatch.setattr(routes_product, "process_video", fake_process)
    original_snapshot = deepcopy(routes_product.CURRENT_OCCUPANCY_SNAPSHOT)
    try:
        response = asyncio.run(routes_product.run_video_test(FakeRequest()))

        assert response == {"status": "completed", "processed_frames": 8, "table_count": 1}
        assert temporary_paths and not temporary_paths[0].exists()
    finally:
        routes_product.CURRENT_OCCUPANCY_SNAPSHOT.clear()
        routes_product.CURRENT_OCCUPANCY_SNAPSHOT.update(original_snapshot)


def test_video_endpoint_returns_json_safe_processing_error_and_deletes_upload(monkeypatch):
    monkeypatch.setattr(
        routes_product,
        "check_product_assets",
        lambda config, model: {"ready_for_video_test": True},
    )
    temporary_paths = []

    def fail_processing(path, config, model):
        temporary_paths.append(path)
        raise RuntimeError(f"decoder failed for {path}")

    monkeypatch.setattr(routes_product, "process_video", fail_processing)

    with pytest.raises(HTTPException) as error:
        asyncio.run(routes_product.run_video_test(FakeRequest()))

    assert error.value.status_code == 422
    assert "Video işlenemedi (RuntimeError)" in error.value.detail
    assert "<geçici-video>" in error.value.detail
    assert temporary_paths and not temporary_paths[0].exists()


def test_detector_factory_reports_both_backend_failures(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "app.video_test.OnnxPersonDetector",
        lambda config: (_ for _ in ()).throw(RuntimeError("bad onnx")),
    )
    monkeypatch.setattr(
        "app.video_test.OpenCvHogPersonDetector",
        lambda: (_ for _ in ()).throw(ImportError("opencv missing")),
    )
    monkeypatch.setattr(
        "app.video_test.OpenCvMotionPersonDetector",
        lambda: (_ for _ in ()).throw(ImportError("motion missing")),
    )

    with pytest.raises(RuntimeError, match="hareket dedektörü başlatılamadı"):
        _create_detector(tmp_path / "missing.onnx")


def test_detector_factory_uses_motion_when_hog_is_unavailable(monkeypatch, tmp_path):
    class FakeMotionBackend:
        def detect(self, frame):
            return [Detection("person", 0.6, [4, 5, 6, 7])]

    monkeypatch.setattr(
        "app.video_test.OnnxPersonDetector",
        lambda config: (_ for _ in ()).throw(RuntimeError("bad onnx")),
    )
    monkeypatch.setattr(
        "app.video_test.OpenCvHogPersonDetector",
        lambda: (_ for _ in ()).throw(AttributeError("no HOGDescriptor")),
    )
    monkeypatch.setattr(
        "app.video_test.OpenCvMotionPersonDetector", lambda: FakeMotionBackend()
    )

    detector = _create_detector(tmp_path / "missing.onnx")

    assert detector.detect(object())[0].bbox == [4.0, 5.0, 6.0, 7.0]


def test_calibration_frame_endpoint_returns_jpeg_and_deletes_upload(monkeypatch):
    temporary_paths = []

    def fake_extract(path, timestamp):
        temporary_paths.append(path)
        assert path.exists()
        assert timestamp == 3.5
        return b"jpeg-data", 1280, 720

    monkeypatch.setattr(routes_product, "extract_video_frame", fake_extract)
    response = asyncio.run(
        routes_product.get_calibration_frame(FakeRequest(timestamp=3.5))
    )

    assert response.body == b"jpeg-data"
    assert response.media_type == "image/jpeg"
    assert response.headers["x-frame-width"] == "1280"
    assert response.headers["x-frame-height"] == "720"
    assert temporary_paths and not temporary_paths[0].exists()
