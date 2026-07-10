"""Geometry drawing helpers for vision overlays."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import cv2
import numpy as np

from app.calibration.models import Point, TablePolygon

EMPTY_TABLE_COLOR = (0, 255, 0)
OCCUPIED_TABLE_COLOR = (0, 0, 255)
DEFAULT_TABLE_COLOR = EMPTY_TABLE_COLOR
TEXT_COLOR = (255, 255, 255)


def draw_table_polygons(
    frame: np.ndarray,
    tables: Sequence[TablePolygon],
    occupancy_status: Mapping[str, bool] | None = None,
) -> np.ndarray:
    """Draw calibrated table polygons and labels on a video frame.

    ``occupancy_status`` is keyed by ``table_id``. A truthy value means occupied
    and is drawn in red; missing or false values are treated as empty and drawn
    in green. The function mutates and returns ``frame`` so callers can use it in
    OpenCV pipelines without an additional copy.
    """

    for table in tables:
        points = _polygon_to_cv_points(table.polygon)
        color = _table_color(table.table_id, occupancy_status)

        cv2.polylines(frame, [points], isClosed=True, color=color, thickness=2)
        cv2.putText(
            frame,
            _table_label(table),
            _label_position(points),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            TEXT_COLOR,
            2,
            cv2.LINE_AA,
        )

    return frame


def _polygon_to_cv_points(polygon: Sequence[Point]) -> np.ndarray:
    return np.array([(point.x, point.y) for point in polygon], dtype=np.int32)


def _table_color(
    table_id: str, occupancy_status: Mapping[str, bool] | None
) -> tuple[int, int, int]:
    if occupancy_status is None:
        return DEFAULT_TABLE_COLOR
    return (
        OCCUPIED_TABLE_COLOR
        if occupancy_status.get(table_id, False)
        else EMPTY_TABLE_COLOR
    )


def _table_label(table: TablePolygon) -> str:
    return table.name or table.table_id


def _label_position(points: np.ndarray) -> tuple[int, int]:
    centroid = points.mean(axis=0).astype(int)
    return int(centroid[0]), int(centroid[1])
