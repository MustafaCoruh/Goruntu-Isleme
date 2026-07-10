from app.calibration.models import Point, TablePolygon
from app.vision.detector import Detection
from app.vision.occupancy import TableOccupancy, compute_table_occupancy


def _table(table_id: str, x1: int, y1: int, x2: int, y2: int) -> TablePolygon:
    return TablePolygon(
        table_id=table_id,
        name=table_id,
        capacity=4,
        polygon=(Point(x1, y1), Point(x2, y1), Point(x2, y2), Point(x1, y2)),
    )


def test_compute_table_occupancy_marks_matching_person_as_occupied() -> None:
    tables = (_table("T-001", 0, 0, 100, 100), _table("T-002", 120, 0, 220, 100))
    detections = [Detection(class_name="person", confidence=0.91, bbox=[20, 20, 60, 60])]

    assert compute_table_occupancy(tables, detections) == [
        TableOccupancy(table_id="T-001", status="occupied", confidence=0.91),
        TableOccupancy(table_id="T-002", status="empty", confidence=1.0),
    ]


def test_compute_table_occupancy_marks_low_confidence_match_as_uncertain() -> None:
    tables = (_table("T-001", 0, 0, 100, 100),)
    detections = [Detection(class_name="person", confidence=0.42, bbox=[20, 20, 60, 60])]

    result = compute_table_occupancy(tables, detections)

    assert result == [TableOccupancy(table_id="T-001", status="uncertain", confidence=0.58)]


def test_compute_table_occupancy_marks_borderline_overlap_as_uncertain() -> None:
    tables = (_table("T-001", 0, 0, 100, 100),)
    detections = [Detection(class_name="person", confidence=0.84, bbox=[90, 90, 140, 140])]

    result = compute_table_occupancy(tables, detections)

    assert result == [TableOccupancy(table_id="T-001", status="uncertain", confidence=0.84)]


def test_compute_table_occupancy_ignores_non_person_detections() -> None:
    tables = (_table("T-001", 0, 0, 100, 100),)
    detections = [Detection(class_name="chair", confidence=0.99, bbox=[20, 20, 60, 60])]

    result = compute_table_occupancy(tables, detections)

    assert result == [TableOccupancy(table_id="T-001", status="empty", confidence=1.0)]
