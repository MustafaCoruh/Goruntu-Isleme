import asyncio
from copy import deepcopy
import json
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.api import routes_product
from app.video_test import process_video


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


class FakeRequest:
    def __init__(self, body=b"video", filename="test.mp4") -> None:
        self.headers = {"x-video-filename": filename}
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
