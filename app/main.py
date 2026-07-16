"""Command-line demo flow for table occupancy detection."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import cv2

from app.calibration.models import CameraConfig, TablePolygon, UtymConfig
from app.camera.capture import (
    ImageFileSource,
    ImageFileSourceError,
    SUPPORTED_IMAGE_EXTENSIONS,
)
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


class DemoRunnerError(RuntimeError):
    """Raised when the local photo/video demo cannot continue."""


class FrameSource(Protocol):
    """Minimal frame-source interface used by the demo loop."""

    path: Path

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
    """Create the command-line argument parser for the local demo app."""

    parser = argparse.ArgumentParser(
        description=(
            "Run the T.UTYM#2 local field demo with a photo or video file. "
            "Keep real images, videos, RTSP URLs, and local configs outside the repo."
        )
    )
    parser.add_argument(
        "--config",
        required=True,
        help=(
            "Path to local camera calibration JSON, for example "
            r"C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json"
        ),
    )
    parser.add_argument(
        "--source",
        required=True,
        help=(
            "Path to a local image or video file, for example "
            r"C:\FTMC_FIELD_DATA\input\photos\sample.jpg"
        ),
    )
    parser.add_argument(
        "--model",
        default="models/person_detector.onnx",
        help=(
            "Path to an ONNX person detection model, for example "
            r"C:\FTMC_FIELD_DATA\models\person_detector.onnx"
        ),
    )
    parser.add_argument(
        "--output",
        help=(
            "Optional path for writing the latest overlay frame/image. Use a local "
            "field-data folder; do not commit outputs with real imagery."
        ),
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Process the source without opening an OpenCV preview window.",
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
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=1,
        help="OpenCV preview delay per frame. Use 0 to hold a photo preview open.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the demo and exit with a process-style status code."""

    args = build_argument_parser().parse_args(argv)

    try:
        _validate_local_paths(args)
        camera_config = _select_demo_camera(load_camera_config(args.config))
        detector = _load_person_detector(args)
        source = _build_source(args.source)
        _run_demo_loop(
            camera_config=camera_config,
            source=source,
            detector=detector,
            window_name=args.window_name,
            output_path=args.output,
            show_window=not args.no_display,
            wait_ms=args.wait_ms,
        )
    except (
        Exception
    ) as exc:  # noqa: BLE001 - CLI boundary should translate all failures.
        print(_field_error_message(exc), file=sys.stderr)
        return 2
    finally:
        cv2.destroyAllWindows()

    return 0


def _validate_local_paths(args: argparse.Namespace) -> None:
    for label, value in (
        ("Config", args.config),
        ("Source", args.source),
        ("Model", args.model),
    ):
        path = Path(value)
        if not path.exists():
            raise DemoRunnerError(
                f"{label} path was not found: {path}\n"
                "Check the Windows path and keep real field files under "
                r"C:\FTMC_FIELD_DATA or another local, non-repository folder."
            )
        if label != "Source" and not path.is_file():
            raise DemoRunnerError(f"{label} path must be a file: {path}")


def _select_demo_camera(config: UtymConfig | CameraConfig) -> CameraConfig:
    """Select the first camera for the single-source demo flow."""

    if isinstance(config, CameraConfig):
        return config
    if not config.cameras:
        raise DemoRunnerError(
            f"UTYM config {config.utym_id} does not contain any cameras"
        )
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
    if suffix in SUPPORTED_IMAGE_EXTENSIONS:
        return ImageFileSource(path)
    if suffix in SUPPORTED_VIDEO_EXTENSIONS:
        return VideoFileSource(path)
    raise DemoRunnerError(
        f"Unsupported source file type: {path}\n"
        f"Supported image extensions: {', '.join(sorted(SUPPORTED_IMAGE_EXTENSIONS))}; "
        f"supported video extensions: {', '.join(sorted(SUPPORTED_VIDEO_EXTENSIONS))}."
    )


def _run_demo_loop(
    *,
    camera_config: CameraConfig,
    source: FrameSource,
    detector: PersonDetector,
    window_name: str,
    output_path: str | Path | None = None,
    show_window: bool = True,
    wait_ms: int = 1,
) -> None:
    smoother = OccupancySmoother()
    latest_overlay = None

    source.open()
    try:
        while True:
            try:
                frame = source.read_frame()
            except (EOFError, ImageFileSourceError):
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
            latest_overlay = draw_debug_overlay(frame, detections, debug_occupancies)

            if output_path is not None:
                _write_overlay(output_path, latest_overlay)

            if show_window:
                cv2.imshow(window_name, latest_overlay)
                if cv2.waitKey(max(0, wait_ms)) & 0xFF == ord("q"):
                    break
    finally:
        source.close()

    if latest_overlay is None:
        raise DemoRunnerError(f"No frames could be read from source: {source.path}")


def _write_overlay(output_path: str | Path, overlay: Any) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), overlay):
        raise DemoRunnerError(f"Overlay output could not be written: {path}")


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


def _field_error_message(exc: Exception) -> str:
    return (
        "Demo could not be started.\n"
        f"Reason: {exc}\n\n"
        "Please verify these local Windows inputs:\n"
        r"  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json"
        "\n"
        r"  --source C:\FTMC_FIELD_DATA\input\photos\sample.jpg"
        "\n"
        r"  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx"
        "\n"
        "Do not paste real RTSP URLs, credentials, photos, or videos into the repository."
    )


if __name__ == "__main__":
    raise SystemExit(main())
