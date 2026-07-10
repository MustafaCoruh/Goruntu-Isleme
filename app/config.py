"""Application configuration loading helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.calibration.models import CameraConfig, Point, Resolution, TablePolygon


def load_camera_config(path: str | Path) -> CameraConfig:
    """Load a camera calibration config from a JSON file."""

    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as config_file:
        raw_config = json.load(config_file)

    return parse_camera_config(raw_config)


def parse_camera_config(raw_config: dict[str, Any]) -> CameraConfig:
    """Parse raw JSON-compatible values into typed camera config models."""

    resolution = raw_config.get("resolution", {})
    return CameraConfig(
        utym_id=str(raw_config["utym_id"]),
        camera_id=str(raw_config["camera_id"]),
        resolution=Resolution(
            width=int(resolution["width"]),
            height=int(resolution["height"]),
        ),
        tables=tuple(_parse_table(table) for table in raw_config.get("tables", [])),
    )


def _parse_table(raw_table: dict[str, Any]) -> TablePolygon:
    return TablePolygon(
        table_id=str(raw_table["table_id"]),
        name=str(raw_table.get("name", raw_table["table_id"])),
        capacity=int(raw_table.get("capacity", 0)),
        polygon=tuple(_parse_point(point) for point in raw_table.get("polygon", [])),
    )


def _parse_point(raw_point: Any) -> Point:
    if isinstance(raw_point, dict):
        return Point(x=int(raw_point["x"]), y=int(raw_point["y"]))

    x, y = raw_point
    return Point(x=int(x), y=int(y))
