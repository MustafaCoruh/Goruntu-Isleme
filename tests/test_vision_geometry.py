import sys
import types

import numpy as np

cv2_stub = types.SimpleNamespace(
    FONT_HERSHEY_SIMPLEX=0,
    LINE_AA=16,
)


def _draw_point(frame: np.ndarray, point: tuple[int, int], color: tuple[int, int, int]) -> None:
    x, y = point
    if 0 <= y < frame.shape[0] and 0 <= x < frame.shape[1]:
        frame[y, x] = color


def _polylines(
    frame: np.ndarray,
    points: list[np.ndarray],
    isClosed: bool,
    color: tuple[int, int, int],
    thickness: int,
) -> None:
    for polygon in points:
        for x, y in polygon.reshape(-1, 2):
            _draw_point(frame, (int(x), int(y)), color)


def _put_text(
    frame: np.ndarray,
    text: str,
    org: tuple[int, int],
    font_face: int,
    font_scale: float,
    color: tuple[int, int, int],
    thickness: int,
    line_type: int,
) -> None:
    _draw_point(frame, org, color)


cv2_stub.polylines = _polylines
cv2_stub.putText = _put_text
sys.modules.setdefault("cv2", cv2_stub)

from app.calibration.models import Point, TablePolygon
from app.vision.geometry import draw_table_polygons


def test_draw_table_polygons_draws_empty_and_occupied_tables() -> None:
    frame = np.zeros((120, 180, 3), dtype=np.uint8)
    tables = (
        TablePolygon(
            table_id="T-001",
            name="Masa 1",
            capacity=4,
            polygon=(Point(10, 10), Point(70, 10), Point(70, 70), Point(10, 70)),
        ),
        TablePolygon(
            table_id="T-002",
            name="Masa 2",
            capacity=2,
            polygon=(Point(90, 10), Point(150, 10), Point(150, 70), Point(90, 70)),
        ),
    )

    result = draw_table_polygons(frame, tables, {"T-001": False, "T-002": True})

    assert result is frame
    assert frame[10, 10].tolist() == [0, 255, 0]
    assert frame[10, 90].tolist() == [0, 0, 255]
    assert np.count_nonzero(frame) > 0


def test_draw_table_polygons_defaults_missing_status_to_empty() -> None:
    frame = np.zeros((80, 80, 3), dtype=np.uint8)
    table = TablePolygon(
        table_id="T-001",
        name="Masa 1",
        capacity=4,
        polygon=(Point(10, 10), Point(50, 10), Point(50, 50), Point(10, 50)),
    )

    draw_table_polygons(frame, (table,), occupancy_status={})

    assert frame[10, 10].tolist() == [0, 255, 0]
    assert frame[30, 30].tolist() == [255, 255, 255]
