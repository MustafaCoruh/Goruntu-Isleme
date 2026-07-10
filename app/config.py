"""Application configuration loading helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from app.calibration.models import CameraConfig, UtymConfig
from app.calibration.service import load_camera_config as _load_camera_config
from app.calibration.service import parse_camera_config as _parse_camera_config


def load_camera_config(path: str | Path) -> UtymConfig | CameraConfig:
    """Load a camera/UTYM calibration config from a JSON file."""

    return _load_camera_config(str(path))


def parse_camera_config(raw_config: Mapping[str, Any]) -> UtymConfig | CameraConfig:
    """Parse raw JSON-compatible values into typed config models."""

    return _parse_camera_config(raw_config)
