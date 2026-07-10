from app.calibration.models import Point, TablePolygon
from app.vision.detector import Detection
from app.vision.occupancy import (
    OccupancySmoother,
    OccupancyStatus,
    TableOccupancy,
    compute_table_occupancy,
)


def _table(table_id: str, x1: int, y1: int, x2: int, y2: int) -> TablePolygon:
    return TablePolygon(
        table_id=table_id,
        name=table_id,
        capacity=4,
        polygon=(Point(x1, y1), Point(x2, y1), Point(x2, y2), Point(x1, y2)),
    )


def _person(confidence: float, bbox: list[float]) -> Detection:
    return Detection(class_name="person", confidence=confidence, bbox=bbox)


def _occupancy(table_id: str, status: OccupancyStatus) -> TableOccupancy:
    return TableOccupancy(table_id=table_id, status=status, confidence=1.0)


def test_person_inside_table_region_marks_occupied() -> None:
    tables = (_table("M-001", 0, 0, 100, 100),)

    result = compute_table_occupancy(tables, [_person(0.92, [20, 20, 60, 60])])

    assert result == [TableOccupancy("M-001", "occupied", 0.92)]


def test_no_person_inside_table_region_marks_empty() -> None:
    tables = (_table("M-001", 0, 0, 100, 100),)

    result = compute_table_occupancy(tables, [_person(0.92, [140, 20, 180, 60])])

    assert result == [TableOccupancy("M-001", "empty", 1.0)]


def test_low_confidence_person_inside_table_region_marks_uncertain() -> None:
    tables = (_table("M-001", 0, 0, 100, 100),)

    result = compute_table_occupancy(tables, [_person(0.42, [20, 20, 60, 60])])

    assert result == [TableOccupancy("M-001", "uncertain", 0.58)]


def test_multiple_people_at_same_table_still_marks_occupied() -> None:
    tables = (_table("M-001", 0, 0, 100, 100),)
    detections = [
        _person(0.71, [10, 10, 40, 60]),
        _person(0.95, [50, 20, 90, 80]),
    ]

    result = compute_table_occupancy(tables, detections)

    assert result == [TableOccupancy("M-001", "occupied", 0.95)]


def test_person_on_two_table_boundary_uses_table_centric_match_rule() -> None:
    tables = (
        _table("M-001", 0, 0, 100, 100),
        _table("M-002", 100, 0, 200, 100),
    )

    result = compute_table_occupancy(tables, [_person(0.88, [80, 20, 120, 80])])

    assert result == [
        TableOccupancy("M-001", "occupied", 0.88),
        TableOccupancy("M-002", "occupied", 0.88),
    ]


def test_time_based_smoothing_decides_from_last_n_frames() -> None:
    smoother = OccupancySmoother(smoothing_window=3, occupied_min_votes=2)
    frame_statuses: list[OccupancyStatus] = [
        "occupied",
        "occupied",
        "empty",
        "empty",
    ]

    result = [
        smoother.smooth([_occupancy("M-001", status)])[0]
        for status in frame_statuses
    ]

    assert result == [
        TableOccupancy("M-001", "uncertain", 1.0),
        TableOccupancy("M-001", "occupied", 1.0),
        TableOccupancy("M-001", "occupied", 0.67),
        TableOccupancy("M-001", "empty", 0.67),
    ]
