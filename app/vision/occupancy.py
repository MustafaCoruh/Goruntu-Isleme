"""Table occupancy calculation helpers for calibrated camera regions."""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from app.calibration.models import TablePolygon
from app.vision.detector import Detection, PERSON_CLASS_NAME
from app.vision.geometry import (
    bbox_center,
    bbox_polygon_overlap_ratio,
    point_in_polygon,
)

OccupancyStatus = Literal["empty", "occupied", "uncertain"]

MIN_OCCUPIED_CONFIDENCE = 0.5
MIN_OCCUPIED_OVERLAP = 0.10
BORDERLINE_OVERLAP = 0.02
EMPTY_CONFIDENCE = 1.0
HIGH_CONFIDENCE_OCCUPIED_THRESHOLD = 0.80
MERGE_CONFLICT_STATUS: OccupancyStatus = "uncertain"
MERGE_CONFIDENCE_STRATEGY = "max"


class OccupancySmoother:
    """Smooth table occupancy decisions across the last N frame results.

    The smoother keeps an independent rolling history per ``table_id``. A table
    is reported as ``occupied`` when at least ``min_votes`` results in the
    current window are occupied, as ``empty`` when at least ``min_votes``
    results are empty, and as ``uncertain`` otherwise.
    """

    def __init__(self, smoothing_window: int = 10, occupied_min_votes: int = 6) -> None:
        if smoothing_window <= 0:
            raise ValueError("smoothing_window must be greater than 0")
        if occupied_min_votes <= 0:
            raise ValueError("occupied_min_votes must be greater than 0")
        if occupied_min_votes > smoothing_window:
            raise ValueError("occupied_min_votes cannot exceed smoothing_window")

        self.smoothing_window = smoothing_window
        self.occupied_min_votes = occupied_min_votes
        self._history: dict[str, deque[OccupancyStatus]] = {}

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "OccupancySmoother":
        """Create a smoother from application configuration values."""

        return cls(
            smoothing_window=int(config.get("smoothing_window", 10)),
            occupied_min_votes=int(config.get("occupied_min_votes", 6)),
        )

    def smooth(self, occupancies: Sequence[TableOccupancy]) -> list[TableOccupancy]:
        """Record one frame of table results and return smoothed decisions."""

        return [self._smooth_single_table(occupancy) for occupancy in occupancies]

    def reset(self, table_id: str | None = None) -> None:
        """Clear accumulated history for one table or for all tables."""

        if table_id is None:
            self._history.clear()
            return

        self._history.pop(table_id, None)

    def _smooth_single_table(self, occupancy: TableOccupancy) -> TableOccupancy:
        history = self._history.setdefault(
            occupancy.history_key, deque(maxlen=self.smoothing_window)
        )
        history.append(occupancy.status)

        occupied_votes = history.count("occupied")
        empty_votes = history.count("empty")

        if occupied_votes >= self.occupied_min_votes:
            status: OccupancyStatus = "occupied"
            confidence = occupied_votes / len(history)
        elif empty_votes >= self.occupied_min_votes:
            status = "empty"
            confidence = empty_votes / len(history)
        else:
            status = "uncertain"
            confidence = max(occupied_votes, empty_votes) / len(history)

        return TableOccupancy(
            table_id=occupancy.table_id,
            status=status,
            confidence=round(confidence, 2),
            camera_id=occupancy.camera_id,
        )


@dataclass(frozen=True)
class TableOccupancy:
    """Occupancy result for a single calibrated table."""

    table_id: str
    status: OccupancyStatus
    confidence: float
    camera_id: str | None = None

    @property
    def history_key(self) -> str:
        """Unique smoothing key, including camera id when available."""

        return f"{self.camera_id}:{self.table_id}" if self.camera_id else self.table_id


def merge_camera_occupancy_results(
    results_by_camera: Mapping[str, Sequence[TableOccupancy]],
    config: Mapping[str, Any] | None = None,
) -> list[TableOccupancy]:
    """Merge camera-level occupancy results into one decision per table.

    The merge is table-centric: if multiple cameras report the same
    ``table_id``, a single aggregate ``TableOccupancy`` is returned for that
    table. By default, any high-confidence ``occupied`` camera result wins.
    Otherwise conflicting camera statuses become ``uncertain``.

    Supported configuration keys:
    - ``high_confidence_occupied_threshold``: minimum occupied confidence that
      can force an aggregate ``occupied`` decision.
    - ``conflict_status``: status to use when cameras disagree.
    - ``confidence_strategy``: ``"max"`` or ``"weighted_average"``.
    - ``camera_weights``: optional camera-id to weight mapping for weighted
      average confidence.
    """

    merge_config = dict(config or {})
    high_confidence_threshold = float(
        merge_config.get(
            "high_confidence_occupied_threshold", HIGH_CONFIDENCE_OCCUPIED_THRESHOLD
        )
    )
    conflict_status = _validated_status(
        merge_config.get("conflict_status", MERGE_CONFLICT_STATUS)
    )
    confidence_strategy = str(
        merge_config.get("confidence_strategy", MERGE_CONFIDENCE_STRATEGY)
    )
    camera_weights = merge_config.get("camera_weights", {})
    if not isinstance(camera_weights, Mapping):
        raise ValueError("camera_weights must be a mapping of camera ids to weights")

    results_by_table: dict[str, list[TableOccupancy]] = {}
    for camera_id, camera_results in results_by_camera.items():
        for result in camera_results:
            normalized_result = (
                result
                if result.camera_id is not None
                else TableOccupancy(
                    table_id=result.table_id,
                    status=result.status,
                    confidence=result.confidence,
                    camera_id=camera_id,
                )
            )
            results_by_table.setdefault(result.table_id, []).append(normalized_result)

    return [
        _merge_single_table_camera_results(
            table_results,
            high_confidence_threshold=high_confidence_threshold,
            conflict_status=conflict_status,
            confidence_strategy=confidence_strategy,
            camera_weights=camera_weights,
        )
        for table_results in results_by_table.values()
    ]


def _merge_single_table_camera_results(
    table_results: Sequence[TableOccupancy],
    *,
    high_confidence_threshold: float,
    conflict_status: OccupancyStatus,
    confidence_strategy: str,
    camera_weights: Mapping[str, float],
) -> TableOccupancy:
    high_confidence_occupied = any(
        result.status == "occupied"
        and _clamp_confidence(result.confidence) >= high_confidence_threshold
        for result in table_results
    )
    statuses = {result.status for result in table_results}

    if high_confidence_occupied:
        status: OccupancyStatus = "occupied"
    elif len(statuses) == 1:
        status = table_results[0].status
    else:
        status = conflict_status

    return TableOccupancy(
        table_id=table_results[0].table_id,
        status=status,
        confidence=_merge_confidence(
            table_results, strategy=confidence_strategy, camera_weights=camera_weights
        ),
    )


def _merge_confidence(
    table_results: Sequence[TableOccupancy],
    *,
    strategy: str,
    camera_weights: Mapping[str, float],
) -> float:
    if strategy == "max":
        return round(
            max(_clamp_confidence(result.confidence) for result in table_results), 2
        )

    if strategy == "weighted_average":
        weighted_confidence = 0.0
        total_weight = 0.0
        for result in table_results:
            weight = float(camera_weights.get(result.camera_id or "", 1.0))
            if weight < 0:
                raise ValueError("camera weights cannot be negative")
            weighted_confidence += _clamp_confidence(result.confidence) * weight
            total_weight += weight

        if total_weight == 0:
            raise ValueError("at least one camera weight must be greater than 0")

        return round(weighted_confidence / total_weight, 2)

    raise ValueError('confidence_strategy must be either "max" or "weighted_average"')


def _validated_status(status: Any) -> OccupancyStatus:
    if status not in {"empty", "occupied", "uncertain"}:
        raise ValueError("conflict_status must be empty, occupied, or uncertain")
    return status


def compute_table_occupancy(
    tables: Sequence[TablePolygon],
    detections: Sequence[Detection],
    camera_id: str | None = None,
) -> list[TableOccupancy]:
    """Compute table occupancy from calibrated table polygons and detections.

    A table is considered ``occupied`` when a confident person detection matches
    the table region. Low-confidence or borderline matches are reported as
    ``uncertain``. Tables without any matching person evidence are ``empty``.
    """

    person_detections = [
        detection
        for detection in detections
        if detection.class_name == PERSON_CLASS_NAME
    ]

    return [
        _compute_single_table_occupancy(table, person_detections, camera_id)
        for table in tables
    ]


def _compute_single_table_occupancy(
    table: TablePolygon,
    detections: Sequence[Detection],
    camera_id: str | None = None,
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
            camera_id=camera_id,
        )

    if uncertain_confidences:
        return TableOccupancy(
            table_id=table.table_id,
            status="uncertain",
            confidence=max(uncertain_confidences),
            camera_id=camera_id,
        )

    return TableOccupancy(
        table_id=table.table_id,
        status="empty",
        confidence=EMPTY_CONFIDENCE,
        camera_id=camera_id,
    )


def _match_detection_to_table(
    table: TablePolygon, detection: Detection
) -> OccupancyStatus | None:
    center_inside = point_in_polygon(bbox_center(detection.bbox), table.polygon)
    overlap_ratio = bbox_polygon_overlap_ratio(detection.bbox, table.polygon)
    confident = detection.confidence >= MIN_OCCUPIED_CONFIDENCE

    if confident and (center_inside or overlap_ratio >= MIN_OCCUPIED_OVERLAP):
        return "occupied"

    if center_inside or overlap_ratio >= BORDERLINE_OVERLAP:
        return "uncertain"

    return None


def _uncertain_confidence(detection: Detection) -> float:
    return _clamp_confidence(
        round(max(detection.confidence, 1.0 - detection.confidence), 2)
    )


def _clamp_confidence(confidence: float) -> float:
    return max(0.0, min(float(confidence), 1.0))
