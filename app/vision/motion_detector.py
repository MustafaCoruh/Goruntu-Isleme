"""Offline moving-object detector used as a last-resort development fallback."""

from __future__ import annotations

from typing import Any

from app.vision.detector import Detection, PERSON_CLASS_NAME


class OpenCvMotionPersonDetector:
    """Approximate people with moving foreground regions.

    This is intentionally a development-only fallback for restricted machines
    whose OpenCV build does not provide HOGDescriptor.
    """

    def __init__(self, cv2_module: Any | None = None, subtractor: Any | None = None) -> None:
        if cv2_module is None:
            import cv2

            cv2_module = cv2
        self._cv2 = cv2_module
        self._subtractor = subtractor or cv2_module.createBackgroundSubtractorMOG2(
            history=200, varThreshold=16, detectShadows=True
        )

    def detect(self, frame) -> list[Detection]:
        mask = self._subtractor.apply(frame)
        _, mask = self._cv2.threshold(mask, 200, 255, self._cv2.THRESH_BINARY)
        contours, _ = self._cv2.findContours(
            mask, self._cv2.RETR_EXTERNAL, self._cv2.CHAIN_APPROX_SIMPLE
        )
        frame_area = float(frame.shape[0] * frame.shape[1])
        minimum_area = max(500.0, frame_area * 0.002)
        detections: list[Detection] = []
        for contour in contours:
            area = float(self._cv2.contourArea(contour))
            if area < minimum_area:
                continue
            x, y, width, height = self._cv2.boundingRect(contour)
            detections.append(
                Detection(
                    class_name=PERSON_CLASS_NAME,
                    confidence=min(0.75, 0.5 + area / frame_area),
                    bbox=[float(x), float(y), float(x + width), float(y + height)],
                )
            )
        return detections
