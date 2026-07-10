"""Standard person detection interface for vision model backends."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol

PERSON_CLASS_NAME = "person"


@dataclass(frozen=True)
class Detection:
    """A single object detection result in image coordinates.

    ``bbox`` uses the common ``[x1, y1, x2, y2]`` format where ``(x1, y1)`` is
    the top-left corner and ``(x2, y2)`` is the bottom-right corner.
    """

    class_name: str
    confidence: float
    bbox: list[float]


class DetectionBackend(Protocol):
    """Protocol implemented by replaceable model-specific detector backends.

    ONNX, YOLO, OpenVINO, or any future runtime should be adapted to this
    protocol so application code depends only on :class:`PersonDetector`.
    """

    def detect(self, frame) -> Iterable[Detection]:
        """Return raw detections for ``frame`` from the underlying model."""


class PersonDetector:
    """Model-agnostic detector that exposes only person detections."""

    def __init__(self, backend: DetectionBackend) -> None:
        self._backend = backend

    def detect(self, frame) -> list[Detection]:
        """Detect people in ``frame`` with bounding boxes and confidence values.

        The concrete model implementation stays behind ``DetectionBackend``;
        this method normalizes results and filters out every class except
        ``person``.
        """

        return [
            _normalize_detection(detection)
            for detection in self._backend.detect(frame)
            if detection.class_name == PERSON_CLASS_NAME
        ]


def _normalize_detection(detection: Detection) -> Detection:
    return Detection(
        class_name=PERSON_CLASS_NAME,
        confidence=float(detection.confidence),
        bbox=_normalize_bbox(detection.bbox),
    )


def _normalize_bbox(bbox: Sequence[float]) -> list[float]:
    if len(bbox) != 4:
        raise ValueError("Detection bbox must contain exactly four values: [x1, y1, x2, y2]")
    return [float(coordinate) for coordinate in bbox]
