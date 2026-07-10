"""Debug visualization helpers for detection and table occupancy results."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from app.calibration.models import Point
from app.vision.detector import PERSON_CLASS_NAME

# BGR color order to match OpenCV image arrays.
PERSON_BOX_COLOR = (255, 0, 0)
OCCUPIED_TABLE_COLOR = (0, 0, 255)
EMPTY_TABLE_COLOR = (0, 255, 0)
UNCERTAIN_TABLE_COLOR = (0, 255, 255)
TEXT_COLOR = (255, 255, 255)
TEXT_BACKGROUND_COLOR = (0, 0, 0)

_TABLE_STATUS_COLORS = {
    "occupied": OCCUPIED_TABLE_COLOR,
    "empty": EMPTY_TABLE_COLOR,
    "uncertain": UNCERTAIN_TABLE_COLOR,
}


def draw_debug_overlay(
    frame: np.ndarray,
    detections: Sequence[Any],
    table_occupancies: Sequence[Any],
) -> np.ndarray:
    """Draw person detections and table occupancy decisions onto a frame.

    The input frame is copied before drawing. Detection bounding boxes are drawn
    for ``person`` detections only. Table occupancy items can be dataclass-like
    objects or mappings, and should include ``status``, ``confidence``, plus
    table geometry either as a top-level ``polygon`` field or a nested ``table``
    object with ``polygon`` and optional ``name`` attributes.
    """

    overlay = frame.copy()

    for detection in detections:
        if _get_value(detection, "class_name") == PERSON_CLASS_NAME:
            bbox = _get_value(detection, "bbox")
            if bbox is not None and len(bbox) == 4:
                x1, y1, x2, y2 = (int(round(float(coordinate))) for coordinate in bbox)
                _draw_rectangle(overlay, x1, y1, x2, y2, PERSON_BOX_COLOR, thickness=2)

    for occupancy in table_occupancies:
        _draw_table_occupancy(overlay, occupancy)

    return overlay


def _draw_table_occupancy(frame: np.ndarray, occupancy: Any) -> None:
    polygon = _get_polygon(occupancy)
    if not polygon:
        return

    status = str(_get_value(occupancy, "status", "uncertain"))
    confidence = float(_get_value(occupancy, "confidence", 0.0))
    color = _TABLE_STATUS_COLORS.get(status, UNCERTAIN_TABLE_COLOR)
    points = [_point_to_xy(point) for point in polygon]

    _draw_polygon(frame, points, color, thickness=2)
    _draw_label(frame, _label_text(occupancy, status, confidence), points, color)


def _draw_polygon(
    frame: np.ndarray,
    points: Sequence[tuple[int, int]],
    color: tuple[int, int, int],
    thickness: int,
) -> None:
    for index, start in enumerate(points):
        end = points[(index + 1) % len(points)]
        _draw_line(frame, start, end, color, thickness)


def _draw_rectangle(
    frame: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: tuple[int, int, int],
    thickness: int,
) -> None:
    _draw_polygon(frame, [(x1, y1), (x2, y1), (x2, y2), (x1, y2)], color, thickness)


def _draw_line(
    frame: np.ndarray,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
    thickness: int,
) -> None:
    x1, y1 = start
    x2, y2 = end
    steps = max(abs(x2 - x1), abs(y2 - y1), 1)
    for step in range(steps + 1):
        x = round(x1 + (x2 - x1) * step / steps)
        y = round(y1 + (y2 - y1) * step / steps)
        _paint_square(frame, int(x), int(y), color, thickness)


def _paint_square(
    frame: np.ndarray,
    x: int,
    y: int,
    color: tuple[int, int, int],
    thickness: int,
) -> None:
    radius = max(0, thickness // 2)
    x1 = max(0, x - radius)
    x2 = min(frame.shape[1], x + radius + 1)
    y1 = max(0, y - radius)
    y2 = min(frame.shape[0], y + radius + 1)
    frame[y1:y2, x1:x2] = color


def _draw_label(
    frame: np.ndarray,
    label: str,
    points: Sequence[tuple[int, int]],
    color: tuple[int, int, int],
) -> None:
    x = max(0, min(point[0] for point in points))
    y = max(0, min(point[1] for point in points) - 14)
    width = min(frame.shape[1] - x, max(10, len(label) * 6 + 10))
    height = 12
    frame[y : min(frame.shape[0], y + height), x : x + width] = TEXT_BACKGROUND_COLOR
    frame[y : min(frame.shape[0], y + height), x : min(frame.shape[1], x + 4)] = color
    _draw_tiny_text(frame, label, x + 6, y + 2, TEXT_COLOR)


def _draw_tiny_text(
    frame: np.ndarray,
    text: str,
    x: int,
    y: int,
    color: tuple[int, int, int],
) -> None:
    """Render a compact debug-text hint without adding a heavyweight GUI dependency."""

    cursor = x
    for character in text[: max(0, (frame.shape[1] - x) // 6)]:
        pattern = ord(character)
        for row in range(7):
            for col in range(4):
                if pattern & (1 << ((row + col) % 7)):
                    _paint_square(frame, cursor + col, y + row, color, 1)
        cursor += 6


def _label_text(occupancy: Any, status: str, confidence: float) -> str:
    name = _get_table_name(occupancy)
    return f"{name}: {status} {confidence:.2f}"


def _get_table_name(occupancy: Any) -> str:
    table = _get_value(occupancy, "table")
    return str(
        _get_value(occupancy, "name")
        or _get_value(table, "name")
        or _get_value(occupancy, "table_id")
        or _get_value(table, "table_id")
        or "Table"
    )


def _get_polygon(occupancy: Any) -> Sequence[Any] | None:
    table = _get_value(occupancy, "table")
    polygon = _get_value(occupancy, "polygon") or _get_value(table, "polygon")
    return polygon if polygon is not None else None


def _point_to_xy(point: Any) -> tuple[int, int]:
    if isinstance(point, Point):
        return point.x, point.y
    if isinstance(point, Mapping):
        return int(point["x"]), int(point["y"])
    return int(point[0]), int(point[1])


def _get_value(source: Any, key: str, default: Any = None) -> Any:
    if source is None:
        return default
    if isinstance(source, Mapping):
        return source.get(key, default)
    return getattr(source, key, default)
