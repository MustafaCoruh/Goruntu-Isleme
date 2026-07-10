"""Table occupancy calculation helpers for calibrated camera regions."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from app.calibration.models import TablePolygon
from app.vision.detector import Detection, PERSON_CLASS_NAME
from app.vision.geometry import bbox_center, bbox_polygon_overlap_ratio, point_in_polygon

OccupancyStatus = Literal["empty", "occupied", "uncertain"]

MIN_OCCUPIED_CONFIDENCE = 0.5
MIN_OCCUPIED_OVERLAP = 0.10
BORDERLINE_OVERLAP = 0.02
EMPTY_CONFIDENCE = 1.0


@dataclass(frozen=True)
class TableOccupancy:
    """Occupancy result for a single calibrated table."""

    table_id: str
    status: OccupancyStatus
    confidence: float


def compute_table_occupancy(
    tables: Sequence[TablePolygon],
    detections: Sequence[Detection],
) -> list[TableOccupancy]:
    """Compute table occupancy from calibrated table polygons and detections.

    A table is considered ``occupied`` when a confident person detection matches
    the table region. Low-confidence or borderline matches are reported as
    ``uncertain``. Tables without any matching person evidence are ``empty``.
    """

    person_detections = [
        detection for detection in detections if detection.class_name == PERSON_CLASS_NAME
    ]

    return [
        _compute_single_table_occupancy(table, person_detections)
        for table in tables
    ]


def _compute_single_table_occupancy(
    table: TablePolygon,
    detections: Sequence[Detection],
) -> TableOccupancy:
    occupied_confidences: list[float] = []
    uncertain_confidences: list[float] = []

    for detection in detections:
        match = _match_detection_to_table(table, detection)
        if match == "occupied":
            occupied_confidences.append(_clamp_confidence(detection.confidence))
        elif match == "uncertain":
            uncertain_confidences.append(_uncertain_confidence(detection))

    if occupied_confidences:
        return TableOccupancy(
            table_id=table.table_id,
            status="occupied",
            confidence=max(occupied_confidences),
        )

    if uncertain_confidences:
        return TableOccupancy(
            table_id=table.table_id,
            status="uncertain",
            confidence=max(uncertain_confidences),
        )

    return TableOccupancy(
        table_id=table.table_id,
        status="empty",
        confidence=EMPTY_CONFIDENCE,
    )


def _match_detection_to_table(table: TablePolygon, detection: Detection) -> OccupancyStatus | None:
    center_inside = point_in_polygon(bbox_center(detection.bbox), table.polygon)
    overlap_ratio = bbox_polygon_overlap_ratio(detection.bbox, table.polygon)
    confident = detection.confidence >= MIN_OCCUPIED_CONFIDENCE

    if confident and (center_inside or overlap_ratio >= MIN_OCCUPIED_OVERLAP):
        return "occupied"

    if center_inside or overlap_ratio >= BORDERLINE_OVERLAP:
        return "uncertain"

    return None


def _uncertain_confidence(detection: Detection) -> float:
    return _clamp_confidence(round(max(detection.confidence, 1.0 - detection.confidence), 2))


def _clamp_confidence(confidence: float) -> float:
    return max(0.0, min(float(confidence), 1.0))
