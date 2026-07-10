import numpy as np

from app.vision.detector import Detection
from app.vision.onnx_detector import OnnxPersonDetector


class FakeInput:
    name = "images"
    shape = [1, 3, 416, 416]


class FakeSession:
    def __init__(self, output):
        self.output = output
        self.received = None

    def get_inputs(self):
        return [FakeInput()]

    def run(self, output_names, feed):
        self.received = feed["images"]
        return [self.output]


def test_onnx_person_detector_filters_thresholds_and_applies_nms() -> None:
    output = np.zeros((1, 4, 85), dtype=np.float32)
    output[0, 0, :6] = [50, 50, 40, 40, 0.9, 0.9]
    output[0, 1, :6] = [52, 52, 40, 40, 0.8, 0.9]
    output[0, 2, :7] = [200, 200, 20, 20, 0.95, 0.1, 0.95]
    output[0, 3, :6] = [300, 300, 20, 20, 0.2, 0.9]
    session = FakeSession(output)
    detector = OnnxPersonDetector(
        {"confidence_threshold": 0.5, "iou_threshold": 0.45}, session=session
    )

    detections = detector.detect(np.zeros((416, 416, 3), dtype=np.uint8))

    assert session.received.shape == (1, 3, 416, 416)
    assert detections == [
        Detection(
            class_name="person",
            confidence=0.809999942779541,
            bbox=[30.0, 30.0, 70.0, 70.0],
        )
    ]


def test_onnx_person_detector_accepts_xyxy_class_output() -> None:
    output = np.array(
        [[[10, 20, 30, 40, 0.75, 0], [1, 2, 3, 4, 0.99, 2]]], dtype=np.float32
    )
    detector = OnnxPersonDetector(session=FakeSession(output))

    detections = detector.detect(np.zeros((416, 416, 3), dtype=np.uint8))

    assert detections == [
        Detection(class_name="person", confidence=0.75, bbox=[10.0, 20.0, 30.0, 40.0])
    ]
