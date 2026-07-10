"""Geometry drawing and spatial helpers for vision overlays."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

import numpy as np

from app.calibration.models import Point, TablePolygon

NumericPoint = Point | Sequence[float]
BoundingBox = Sequence[float]

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

    import cv2

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


def bbox_center(bbox: BoundingBox) -> tuple[int, int]:
    """Return the center point of a ``[x1, y1, x2, y2]`` bounding box."""

    x1, y1, x2, y2 = _normalize_bbox(bbox)
    return round((x1 + x2) / 2), round((y1 + y2) / 2)


def point_in_polygon(point: NumericPoint, polygon: Sequence[NumericPoint]) -> bool:
    """Return whether ``point`` is inside or on the boundary of ``polygon``."""

    x, y = _point_coordinates(point)
    vertices = [_point_coordinates(vertex) for vertex in polygon]
    if len(vertices) < 3:
        raise ValueError("Polygon must contain at least 3 points")

    inside = False
    previous_x, previous_y = vertices[-1]
    for current_x, current_y in vertices:
        if _point_on_segment(x, y, previous_x, previous_y, current_x, current_y):
            return True
        intersects = (current_y > y) != (previous_y > y)
        if intersects:
            edge_x = (previous_x - current_x) * (y - current_y) / (previous_y - current_y) + current_x
            if x <= edge_x:
                inside = not inside
        previous_x, previous_y = current_x, current_y

    return inside


def bbox_polygon_overlap_ratio(bbox: BoundingBox, polygon: Sequence[NumericPoint]) -> float:
    """Return the fraction of ``bbox`` area covered by ``polygon``.

    The bounding box is treated as an axis-aligned rectangle in ``[x1, y1, x2,
    y2]`` format. The result is the intersection area divided by the bbox area,
    so it is always between ``0.0`` and ``1.0``.
    """

    x1, y1, x2, y2 = _normalize_bbox(bbox)
    bbox_area = (x2 - x1) * (y2 - y1)
    if bbox_area <= 0:
        raise ValueError("Bounding box must have positive width and height")

    clipped_polygon = [_point_coordinates(point) for point in polygon]
    if len(clipped_polygon) < 3:
        raise ValueError("Polygon must contain at least 3 points")

    for inside, intersection in (
        (lambda point: point[0] >= x1, lambda start, end: _intersect_vertical(start, end, x1)),
        (lambda point: point[0] <= x2, lambda start, end: _intersect_vertical(start, end, x2)),
        (lambda point: point[1] >= y1, lambda start, end: _intersect_horizontal(start, end, y1)),
        (lambda point: point[1] <= y2, lambda start, end: _intersect_horizontal(start, end, y2)),
    ):
        clipped_polygon = _clip_polygon(clipped_polygon, inside, intersection)
        if not clipped_polygon:
            return 0.0

    return min(_polygon_area(clipped_polygon) / bbox_area, 1.0)


def _normalize_bbox(bbox: BoundingBox) -> tuple[float, float, float, float]:
    if len(bbox) != 4:
        raise ValueError("Bounding box must contain exactly four values: [x1, y1, x2, y2]")
    x1, y1, x2, y2 = (float(value) for value in bbox)
    if x2 < x1 or y2 < y1:
        raise ValueError("Bounding box coordinates must satisfy x1 <= x2 and y1 <= y2")
    return x1, y1, x2, y2


def _point_coordinates(point: NumericPoint) -> tuple[float, float]:
    if isinstance(point, Point):
        return float(point.x), float(point.y)
    if len(point) != 2:
        raise ValueError("Point must contain exactly two coordinates: [x, y]")
    return float(point[0]), float(point[1])


def _point_on_segment(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> bool:
    cross_product = (py - ay) * (bx - ax) - (px - ax) * (by - ay)
    if abs(cross_product) > 1e-9:
        return False
    return min(ax, bx) <= px <= max(ax, bx) and min(ay, by) <= py <= max(ay, by)


def _clip_polygon(
    polygon: Sequence[tuple[float, float]],
    inside: Callable[[tuple[float, float]], bool],
    intersection: Callable[[tuple[float, float], tuple[float, float]], tuple[float, float]],
) -> list[tuple[float, float]]:
    clipped: list[tuple[float, float]] = []
    start = polygon[-1]
    start_inside = inside(start)
    for end in polygon:
        end_inside = inside(end)
        if end_inside:
            if not start_inside:
                clipped.append(intersection(start, end))
            clipped.append(end)
        elif start_inside:
            clipped.append(intersection(start, end))
        start = end
        start_inside = end_inside
    return clipped


def _intersect_vertical(start: tuple[float, float], end: tuple[float, float], x: float) -> tuple[float, float]:
    start_x, start_y = start
    end_x, end_y = end
    if end_x == start_x:
        return x, start_y
    ratio = (x - start_x) / (end_x - start_x)
    return x, start_y + ratio * (end_y - start_y)


def _intersect_horizontal(start: tuple[float, float], end: tuple[float, float], y: float) -> tuple[float, float]:
    start_x, start_y = start
    end_x, end_y = end
    if end_y == start_y:
        return start_x, y
    ratio = (y - start_y) / (end_y - start_y)
    return start_x + ratio * (end_x - start_x), y


def _polygon_area(polygon: Sequence[tuple[float, float]]) -> float:
    area = 0.0
    previous_x, previous_y = polygon[-1]
    for current_x, current_y in polygon:
        area += previous_x * current_y - current_x * previous_y
        previous_x, previous_y = current_x, current_y
    return abs(area) / 2


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
