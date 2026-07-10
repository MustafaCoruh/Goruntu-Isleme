import numpy as np
import pytest

from app.vision.detector import Detection, PersonDetector


class FakeBackend:
    def __init__(self, detections: list[Detection]) -> None:
        self.detections = detections
        self.received_frame = None

    def detect(self, frame):
        self.received_frame = frame
        return self.detections


def test_person_detector_returns_only_person_detections() -> None:
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    backend = FakeBackend(
        [
            Detection(class_name="person", confidence=0.87, bbox=[10, 20, 30, 40]),
            Detection(class_name="chair", confidence=0.92, bbox=[1, 2, 3, 4]),
        ]
    )
    detector = PersonDetector(backend)

    detections = detector.detect(frame)

    assert backend.received_frame is frame
    assert detections == [
        Detection(class_name="person", confidence=0.87, bbox=[10.0, 20.0, 30.0, 40.0])
    ]


def test_person_detector_requires_four_bbox_coordinates() -> None:
    detector = PersonDetector(
        FakeBackend([Detection(class_name="person", confidence=0.5, bbox=[1, 2, 3])])
    )

    with pytest.raises(ValueError, match="bbox must contain exactly four values"):
        detector.detect(frame=None)
