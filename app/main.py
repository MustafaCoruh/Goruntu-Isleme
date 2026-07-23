"""Command-line demo flow for table occupancy detection."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import cv2

from app.calibration.models import CameraConfig, TablePolygon, UtymConfig
from app.config import load_camera_config
from app.vision.detector import PersonDetector
from app.vision.occupancy import (
    OccupancySmoother,
    TableOccupancy,
    compute_table_occupancy,
)
from app.vision.visualization import draw_debug_overlay

SUPPORTED_VIDEO_EXTENSIONS = frozenset({".avi", ".m4v", ".mkv", ".mov", ".mp4"})
DEFAULT_WINDOW_NAME = "UTYM Table Occupancy Demo"


class FrameSource(Protocol):
    """Minimal frame-source interface used by the demo loop."""

    def open(self) -> None: ...

    def read_frame(self) -> Any: ...

    def close(self) -> None: ...


@dataclass(frozen=True)
class TableOccupancyDebug:
    """Occupancy result enriched with table geometry for debug drawing."""

    table: TablePolygon
    table_id: str
    status: str
    confidence: float


class VideoFileSource:
    """Read frames from a video file through OpenCV."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._capture: cv2.VideoCapture | None = None

    def open(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(f"Video file does not exist: {self.path}")

        self.close()
        capture = cv2.VideoCapture(str(self.path))
        if not capture.isOpened():
            capture.release()
            raise RuntimeError(f"Could not open video source: {self.path}")

        self._capture = capture

    def read_frame(self) -> Any:
        if self._capture is None or not self._capture.isOpened():
            raise RuntimeError(f"Video source is not open: {self.path}")

        ok, frame = self._capture.read()
        if not ok or frame is None:
            raise EOFError(f"No more frames available from video: {self.path}")

        return frame

    def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def __enter__(self) -> "VideoFileSource":
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser for the demo app."""

    parser = argparse.ArgumentParser(description="Run the UTYM occupancy demo flow.")
    parser.add_argument(
        "--config", required=True, help="Path to camera calibration JSON."
    )
    parser.add_argument(
        "--source", required=True, help="Path to a local video source."
    )
    parser.add_argument(
        "--model",
        default="models/person_detector.onnx",
        help="Path to an ONNX person detection model.",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.5,
        help="Minimum detector confidence for person detections.",
    )
    parser.add_argument(
        "--iou-threshold",
        type=float,
        default=0.45,
        help="NMS IoU threshold for person detections.",
    )
    parser.add_argument(
        "--window-name",
        default=DEFAULT_WINDOW_NAME,
        help="OpenCV window title for the debug overlay.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the demo and exit with a process-style status code."""

    args = build_argument_parser().parse_args(argv)
    camera_config = _select_demo_camera(load_camera_config(args.config))
    detector = _load_person_detector(args)
    source = _build_source(args.source)

    try:
        _run_demo_loop(
            camera_config=camera_config,
            source=source,
            detector=detector,
            window_name=args.window_name,
        )
    finally:
        cv2.destroyAllWindows()

    return 0


def _select_demo_camera(config: UtymConfig | CameraConfig) -> CameraConfig:
    """Select the first camera for the single-source demo flow."""

    if isinstance(config, CameraConfig):
        return config
    if not config.cameras:
        raise ValueError(f"UTYM config {config.utym_id} does not contain any cameras")
    return config.cameras[0]


def _load_person_detector(args: argparse.Namespace) -> PersonDetector:
    from app.vision.onnx_detector import OnnxPersonDetector, OnnxPersonDetectorConfig

    backend = OnnxPersonDetector(
        OnnxPersonDetectorConfig(
            model_path=args.model,
            confidence_threshold=args.confidence_threshold,
            iou_threshold=args.iou_threshold,
        )
    )
    return PersonDetector(backend)


def _build_source(source_path: str | Path) -> FrameSource:
    path = Path(source_path)
    suffix = path.suffix.lower()
    if suffix in SUPPORTED_VIDEO_EXTENSIONS:
        return VideoFileSource(path)
    raise ValueError(
        f"Unsupported source extension for {path}. "
        f"Supported video extensions: {', '.join(sorted(SUPPORTED_VIDEO_EXTENSIONS))}"
    )


def _run_demo_loop(
    *,
    camera_config: CameraConfig,
    source: FrameSource,
    detector: PersonDetector,
    window_name: str,
) -> None:
    smoother = OccupancySmoother()

    source.open()
    try:
        while True:
            try:
                frame = source.read_frame()
            except EOFError:
                break

            detections = detector.detect(frame)
            occupancies = smoother.smooth(
                compute_table_occupancy(
                    camera_config.tables, detections, camera_config.camera_id
                )
            )
            debug_occupancies = _attach_table_geometry(
                camera_config.tables, occupancies
            )
            overlay = draw_debug_overlay(frame, detections, debug_occupancies)

            cv2.imshow(window_name, overlay)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        source.close()


def _attach_table_geometry(
    tables: tuple[TablePolygon, ...], occupancies: list[TableOccupancy]
) -> list[TableOccupancyDebug]:
    tables_by_id = {table.table_id: table for table in tables}
    return [
        TableOccupancyDebug(
            table=tables_by_id[occupancy.table_id],
            table_id=occupancy.table_id,
            status=occupancy.status,
            confidence=occupancy.confidence,
        )
        for occupancy in occupancies
        if occupancy.table_id in tables_by_id
    ]


if __name__ == "__main__":
    raise SystemExit(main())
