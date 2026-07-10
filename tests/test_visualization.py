from dataclasses import dataclass

import numpy as np

from app.calibration.models import Point, TablePolygon
from app.vision.detector import Detection
from app.vision.visualization import draw_debug_overlay


@dataclass(frozen=True)
class DebugTableOccupancy:
    table: TablePolygon
    status: str
    confidence: float


def _table(name: str, x1: int, y1: int, x2: int, y2: int) -> TablePolygon:
    return TablePolygon(
        table_id=name,
        name=name,
        capacity=4,
        polygon=(Point(x1, y1), Point(x2, y1), Point(x2, y2), Point(x1, y2)),
    )


def test_draw_debug_overlay_draws_expected_debug_colors_and_preserves_input() -> None:
    frame = np.zeros((140, 220, 3), dtype=np.uint8)
    detections = [Detection(class_name="person", confidence=0.91, bbox=[10, 10, 50, 60])]
    table_occupancies = [
        DebugTableOccupancy(_table("Masa 1", 70, 10, 120, 50), "occupied", 0.91),
        DebugTableOccupancy(_table("Masa 2", 70, 70, 120, 110), "empty", 1.0),
        DebugTableOccupancy(_table("Masa 3", 140, 70, 200, 110), "uncertain", 0.55),
    ]

    overlay = draw_debug_overlay(frame, detections, table_occupancies)

    assert overlay is not frame
    assert frame.sum() == 0
    assert overlay[10, 10].tolist() == [255, 0, 0]
    assert overlay[10, 70].tolist() == [0, 0, 255]
    assert overlay[70, 70].tolist() == [0, 255, 0]
    assert overlay[70, 140].tolist() == [0, 255, 255]
    assert overlay.sum() > 0


def test_draw_debug_overlay_accepts_mapping_inputs() -> None:
    frame = np.zeros((80, 80, 3), dtype=np.uint8)
    detections = [{"class_name": "person", "confidence": 0.8, "bbox": [5, 5, 25, 25]}]
    table_occupancies = [
        {
            "name": "Masa 1",
            "status": "occupied",
            "confidence": 0.91,
            "polygon": [[30, 10], [60, 10], [60, 40], [30, 40]],
        }
    ]

    overlay = draw_debug_overlay(frame, detections, table_occupancies)

    assert overlay[5, 5].tolist() == [255, 0, 0]
    assert overlay[10, 30].tolist() == [0, 0, 255]
