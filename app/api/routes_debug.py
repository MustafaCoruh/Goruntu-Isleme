"""Debug visualization routes for camera/table occupancy overlays."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Response, status

from app.calibration.models import CameraConfig, UtymConfig
from app.config import load_camera_config
from app.api.routes_occupancy import CURRENT_OCCUPANCY_SNAPSHOT
from app.vision.visualization import draw_debug_overlay

router = APIRouter(prefix="/debug", tags=["debug"])

_DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parents[2] / "configs" / "utym_001_cam_001.json"
)
_DEBUG_ENABLED_ENV = "FTMC_DEBUG_UI_ENABLED"

_SAMPLE_DETECTIONS: list[dict[str, Any]] = [
    {"class_name": "person", "confidence": 0.88, "bbox": [130, 170, 285, 455]},
    {"class_name": "person", "confidence": 0.77, "bbox": [745, 145, 930, 500]},
]


def is_debug_ui_enabled() -> bool:
    """Return whether debug visualization endpoints are available."""

    value = os.getenv(_DEBUG_ENABLED_ENV, "true").strip().lower()
    return value not in {"0", "false", "no", "off"}


def _require_debug_enabled() -> None:
    if not is_debug_ui_enabled():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debug UI is disabled for operation mode.",
        )


def _select_debug_camera(config: UtymConfig | CameraConfig) -> CameraConfig:
    if isinstance(config, CameraConfig):
        return config
    if not config.cameras:
        raise ValueError(f"UTYM config {config.utym_id} does not contain any cameras")
    return config.cameras[0]


def _load_debug_tables() -> list[dict[str, Any]]:
    config = _select_debug_camera(
        load_camera_config(os.getenv("FTMC_CAMERA_CONFIG", _DEFAULT_CONFIG_PATH))
    )
    snapshot_tables = {
        str(table["table_id"]): table
        for table in CURRENT_OCCUPANCY_SNAPSHOT.get("tables", [])
    }

    tables: list[dict[str, Any]] = []
    for table in config.tables:
        snapshot = snapshot_tables.get(table.table_id, {})
        tables.append(
            {
                "table_id": table.table_id,
                "name": table.name,
                "capacity": table.capacity,
                "polygon": [[point.x, point.y] for point in table.polygon],
                "status": snapshot.get("status", "uncertain"),
                "confidence": snapshot.get("confidence", 0.0),
            }
        )
    return tables


def _resolution_from_tables(tables: list[dict[str, Any]]) -> tuple[int, int]:
    try:
        config = _select_debug_camera(
            load_camera_config(os.getenv("FTMC_CAMERA_CONFIG", _DEFAULT_CONFIG_PATH))
        )
        return config.resolution.width, config.resolution.height
    except (FileNotFoundError, KeyError, ValueError):
        max_x = max(
            (point[0] for table in tables for point in table["polygon"]), default=1280
        )
        max_y = max(
            (point[1] for table in tables for point in table["polygon"]), default=720
        )
        return max(640, max_x + 80), max(360, max_y + 80)


@router.get("/state")
def get_debug_state() -> dict[str, Any]:
    """Return the latest debug snapshot consumed by the static debug page."""

    _require_debug_enabled()
    tables = _load_debug_tables()
    width, height = _resolution_from_tables(tables)
    return {
        "enabled": True,
        "mode_hint": f"Set {_DEBUG_ENABLED_ENV}=false to hide this screen in operation mode.",
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "frame_url": "/debug/frame.jpg",
        "frame": {"width": width, "height": height},
        "detections": deepcopy(_SAMPLE_DETECTIONS),
        "tables": tables,
    }


@router.get("/frame.jpg")
def get_debug_frame() -> Response:
    """Return a periodically refreshable JPEG debug frame with overlay data."""

    _require_debug_enabled()
    tables = _load_debug_tables()
    width, height = _resolution_from_tables(tables)
    import cv2
    import numpy as np

    frame = np.full((height, width, 3), (34, 38, 49), dtype=np.uint8)
    overlay = draw_debug_overlay(frame, _SAMPLE_DETECTIONS, tables)
    ok, encoded = cv2.imencode(".jpg", overlay)
    if not ok:
        raise HTTPException(status_code=500, detail="Could not encode debug frame.")
    return Response(content=encoded.tobytes(), media_type="image/jpeg")
