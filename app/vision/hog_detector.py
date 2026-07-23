"""Offline OpenCV HOG person detector used when an ONNX model is unavailable."""

from __future__ import annotations

from math import exp
from typing import Any

from app.vision.detector import Detection, PERSON_CLASS_NAME


class OpenCvHogPersonDetector:
    """Detect people with OpenCV's built-in HOG coefficients.

    This detector requires no downloaded model file. It is intended as an
    offline development fallback; ONNX remains the production path.
    """

    def __init__(self, hog: Any | None = None) -> None:
        if hog is None:
            import cv2

            hog = cv2.HOGDescriptor()
            hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self._hog = hog

    def detect(self, frame) -> list[Detection]:
        rectangles, weights = self._hog.detectMultiScale(
            frame, winStride=(8, 8), padding=(8, 8), scale=1.05
        )
        flattened_weights = list(weights)
        return [
            Detection(
                class_name=PERSON_CLASS_NAME,
                confidence=_weight_to_confidence(flattened_weights[index]),
                bbox=[float(x), float(y), float(x + width), float(y + height)],
            )
            for index, (x, y, width, height) in enumerate(rectangles)
        ]


def _weight_to_confidence(weight: Any) -> float:
    value = float(weight[0] if hasattr(weight, "__len__") else weight)
    return 1.0 / (1.0 + exp(-value))
