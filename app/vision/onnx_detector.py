"""ONNX Runtime based person detector backend."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort

from app.vision.detector import Detection, PERSON_CLASS_NAME

DEFAULT_MODEL_PATH = "models/person_detector.onnx"
DEFAULT_CONFIDENCE_THRESHOLD = 0.5
DEFAULT_IOU_THRESHOLD = 0.45
PERSON_CLASS_ID = 0


@dataclass(frozen=True)
class OnnxPersonDetectorConfig:
    """Configuration for :class:`OnnxPersonDetector`."""

    model_path: str = DEFAULT_MODEL_PATH
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    iou_threshold: float = DEFAULT_IOU_THRESHOLD


class OnnxPersonDetector:
    """Detect people in image frames with an ONNX Runtime object detector.

    The implementation is tailored for COCO-trained YOLO-style models such as
    the repository's selected YOLOX-Nano artifact. It accepts common detector
    output layouts, filters COCO class id ``0`` (person), applies confidence
    thresholding, rescales boxes to the original frame, and runs NMS.
    """

    def __init__(
        self,
        config: OnnxPersonDetectorConfig | dict[str, Any] | None = None,
        *,
        session: ort.InferenceSession | None = None,
    ) -> None:
        self.config = _coerce_config(config)
        self._session = session or ort.InferenceSession(
            str(Path(self.config.model_path)), providers=["CPUExecutionProvider"]
        )
        self._input = self._session.get_inputs()[0]
        self._input_name = self._input.name
        self._input_height, self._input_width = _resolve_input_size(self._input.shape)

    def detect(self, frame) -> list[Detection]:
        """Return person detections for ``frame`` in ``[x1, y1, x2, y2]`` format."""

        input_tensor, scale = self._preprocess(frame)
        outputs = self._session.run(None, {self._input_name: input_tensor})
        detections = self._postprocess(outputs, frame_shape=frame.shape, scale=scale)
        return detections

    def _preprocess(self, frame) -> tuple[np.ndarray, float]:
        if frame is None or not hasattr(frame, "shape") or len(frame.shape) < 2:
            raise ValueError("frame must be an image array with height and width")

        height, width = frame.shape[:2]
        scale = min(self._input_width / width, self._input_height / height)
        resized_width = int(width * scale)
        resized_height = int(height * scale)

        resized = _resize_nearest(frame, resized_height, resized_width)
        padded = np.full(
            (self._input_height, self._input_width, 3), 114, dtype=np.uint8
        )
        padded[:resized_height, :resized_width] = resized

        rgb = padded[..., ::-1]
        tensor = rgb.astype(np.float32) / 255.0
        tensor = np.transpose(tensor, (2, 0, 1))[np.newaxis, ...]
        return np.ascontiguousarray(tensor), scale

    def _postprocess(
        self, outputs: list[np.ndarray], *, frame_shape: tuple[int, ...], scale: float
    ) -> list[Detection]:
        predictions = _flatten_predictions(outputs)
        if predictions.size == 0:
            return []

        boxes, scores, class_ids = _extract_boxes_scores_classes(predictions)
        keep = (class_ids == PERSON_CLASS_ID) & (
            scores >= self.config.confidence_threshold
        )
        boxes = boxes[keep]
        scores = scores[keep]
        if len(boxes) == 0:
            return []

        boxes = boxes / scale
        boxes[:, [0, 2]] = np.clip(boxes[:, [0, 2]], 0, frame_shape[1])
        boxes[:, [1, 3]] = np.clip(boxes[:, [1, 3]], 0, frame_shape[0])

        keep_indices = _non_maximum_suppression(
            boxes, scores, self.config.iou_threshold
        )
        return [
            Detection(
                class_name=PERSON_CLASS_NAME,
                confidence=float(scores[index]),
                bbox=[float(value) for value in boxes[index].tolist()],
            )
            for index in keep_indices
        ]


def _resize_nearest(frame: np.ndarray, height: int, width: int) -> np.ndarray:
    source_height, source_width = frame.shape[:2]
    y_indices = np.minimum(
        (np.arange(height) / (height / source_height)).astype(np.int64),
        source_height - 1,
    )
    x_indices = np.minimum(
        (np.arange(width) / (width / source_width)).astype(np.int64), source_width - 1
    )
    return frame[y_indices[:, None], x_indices]


def _coerce_config(
    config: OnnxPersonDetectorConfig | dict[str, Any] | None,
) -> OnnxPersonDetectorConfig:
    if config is None:
        return OnnxPersonDetectorConfig()
    if isinstance(config, OnnxPersonDetectorConfig):
        return config
    return OnnxPersonDetectorConfig(
        model_path=config.get("model_path", DEFAULT_MODEL_PATH),
        confidence_threshold=float(
            config.get("confidence_threshold", DEFAULT_CONFIDENCE_THRESHOLD)
        ),
        iou_threshold=float(config.get("iou_threshold", DEFAULT_IOU_THRESHOLD)),
    )


def _resolve_input_size(shape: list[Any]) -> tuple[int, int]:
    height = _dimension_to_int(shape[2] if len(shape) == 4 else None, 416)
    width = _dimension_to_int(shape[3] if len(shape) == 4 else None, 416)
    return height, width


def _dimension_to_int(value: Any, default: int) -> int:
    if isinstance(value, int) and value > 0:
        return value
    return default


def _flatten_predictions(outputs: list[np.ndarray]) -> np.ndarray:
    if not outputs:
        return np.empty((0, 0), dtype=np.float32)
    predictions = np.asarray(outputs[0])
    if predictions.ndim == 3:
        predictions = predictions[0]
    return predictions.reshape(-1, predictions.shape[-1]).astype(np.float32)


def _extract_boxes_scores_classes(
    predictions: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if predictions.shape[1] == 6:
        boxes = predictions[:, :4]
        scores = predictions[:, 4]
        class_ids = predictions[:, 5].astype(np.int64)
        return boxes, scores, class_ids

    if predictions.shape[1] < 6:
        raise ValueError(
            "ONNX detector output must contain box, confidence, and class values"
        )

    boxes = _center_to_corners(predictions[:, :4])
    objectness = predictions[:, 4]
    class_scores = predictions[:, 5:]
    class_ids = np.argmax(class_scores, axis=1).astype(np.int64)
    scores = objectness * class_scores[np.arange(len(class_scores)), class_ids]
    return boxes, scores, class_ids


def _center_to_corners(boxes: np.ndarray) -> np.ndarray:
    corners = np.empty_like(boxes, dtype=np.float32)
    corners[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
    corners[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
    corners[:, 2] = boxes[:, 0] + boxes[:, 2] / 2
    corners[:, 3] = boxes[:, 1] + boxes[:, 3] / 2
    return corners


def _non_maximum_suppression(
    boxes: np.ndarray, scores: np.ndarray, iou_threshold: float
) -> list[int]:
    order = scores.argsort()[::-1]
    keep: list[int] = []
    while order.size > 0:
        current = int(order[0])
        keep.append(current)
        if order.size == 1:
            break
        ious = _iou(boxes[current], boxes[order[1:]])
        order = order[1:][ious <= iou_threshold]
    return keep


def _iou(box: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    x1 = np.maximum(box[0], boxes[:, 0])
    y1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[2], boxes[:, 2])
    y2 = np.minimum(box[3], boxes[:, 3])

    intersection = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
    box_area = np.maximum(0, box[2] - box[0]) * np.maximum(0, box[3] - box[1])
    boxes_area = np.maximum(0, boxes[:, 2] - boxes[:, 0]) * np.maximum(
        0, boxes[:, 3] - boxes[:, 1]
    )
    union = box_area + boxes_area - intersection
    return np.divide(
        intersection, union, out=np.zeros_like(intersection), where=union > 0
    )
