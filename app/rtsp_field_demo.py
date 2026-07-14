"""Safe RTSP field demo runner for T.UTYM#2.

This module validates a local RTSP config without printing or reporting the real
RTSP URL, then runs the existing visual demo loop against a live camera source.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from app.field_demo import (
    DEFAULT_MODEL,
    FieldDemoPreflightError,
    _report_safety_note,
    _require_probability,
    _require_report_output_path,
    _safe_file_summary,
    _utc_now,
    _write_json_report,
)

DEFAULT_RTSP_CONFIG = r"C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.rtsp.local.json"


@dataclass(frozen=True)
class RtspFieldDemoInputs:
    """Validated RTSP field demo inputs."""

    config: Path
    model: Path
    camera_id: str
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    window_name: str = "T.UTYM#2 RTSP Field Demo"
    report_output: Path | None = None
    connection_test_frames: int = 0


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the operator-friendly RTSP demo parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Run the T.UTYM#2 RTSP field demo from a local-only config. "
            "Do not paste RTSP URLs into commands, docs, GitHub, or chat."
        )
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_RTSP_CONFIG,
        help=(
            "Path to local RTSP config JSON. Defaults to "
            f"{DEFAULT_RTSP_CONFIG}. This file must stay outside the repository."
        ),
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Path to ONNX person detector. Defaults to {DEFAULT_MODEL}.",
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
        default="T.UTYM#2 RTSP Field Demo",
        help="OpenCV window title for the debug overlay.",
    )
    parser.add_argument(
        "--report-output",
        help=(
            "Optional path for a safe JSON RTSP report. The report stores camera id, "
            "filenames, thresholds, and status, but not the RTSP URL, IP address, "
            "credentials, images, videos, or full local paths."
        ),
    )
    parser.add_argument(
        "--connection-test-frames",
        type=int,
        default=0,
        help=(
            "If greater than 0, open the RTSP stream, read this many frames, "
            "write a safe connection report, and exit without running the detector."
        ),
    )
    return parser


def validate_inputs(args: argparse.Namespace) -> RtspFieldDemoInputs:
    """Validate local RTSP inputs without importing OpenCV-heavy modules."""

    config = Path(args.config).expanduser()
    model = Path(args.model).expanduser()
    report_output = Path(args.report_output).expanduser() if args.report_output else None

    _require_existing_file(config, "RTSP config JSON")
    _require_existing_file(model, "ONNX person detector model")
    _require_probability(args.confidence_threshold, "confidence-threshold")
    _require_probability(args.iou_threshold, "iou-threshold")
    if report_output is not None:
        _require_report_output_path(report_output)
    _require_non_negative_int(args.connection_test_frames, "connection-test-frames")

    raw_config = _load_json_object(config)
    camera_config = _select_camera_config(raw_config)
    camera_id = _require_rtsp_camera_config(camera_config)

    return RtspFieldDemoInputs(
        config=config,
        model=model,
        camera_id=camera_id,
        confidence_threshold=args.confidence_threshold,
        iou_threshold=args.iou_threshold,
        window_name=args.window_name,
        report_output=report_output,
        connection_test_frames=args.connection_test_frames,
    )


def run(argv: Sequence[str] | None = None) -> int:
    """Run RTSP preflight checks and start the live demo."""

    parser = build_argument_parser()
    args = parser.parse_args(argv)

    try:
        inputs = validate_inputs(args)
    except FieldDemoPreflightError as error:
        _write_preflight_failure_report(args, str(error))
        parser.exit(status=2, message=f"T.UTYM#2 RTSP preflight failed: {error}\n")

    from app.config import load_camera_config
    from app.camera.sources import RtspCameraSource
    from app.main import _load_person_detector, _run_demo_loop

    camera_config = _select_runtime_camera(load_camera_config(str(inputs.config)))
    source = RtspCameraSource(camera_config)

    if inputs.connection_test_frames > 0:
        _write_rtsp_report(inputs, status="connection_test_started")
        try:
            connection_result = _run_connection_test(source, inputs.connection_test_frames)
        except Exception as error:
            _write_rtsp_report(inputs, status="connection_test_failed", message=str(error))
            raise
        _write_rtsp_report(
            inputs, status="connection_test_completed", details=connection_result
        )
        return 0

    detector = _load_person_detector(_detector_args(inputs))

    _write_rtsp_report(inputs, status="started")
    try:
        _run_demo_loop(
            camera_config=camera_config,
            source=source,
            detector=detector,
            window_name=inputs.window_name,
        )
    except Exception as error:
        _write_rtsp_report(inputs, status="failed", message=str(error))
        raise

    _write_rtsp_report(inputs, status="completed", exit_code=0)
    return 0


def _detector_args(inputs: RtspFieldDemoInputs) -> argparse.Namespace:
    return argparse.Namespace(
        model=str(inputs.model),
        confidence_threshold=inputs.confidence_threshold,
        iou_threshold=inputs.iou_threshold,
    )


def _require_non_negative_int(value: int, label: str) -> None:
    if value < 0:
        raise FieldDemoPreflightError(f"{label} must be 0 or greater, got {value}")


def _require_existing_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FieldDemoPreflightError(
            f"Missing {label}: {path}. Keep RTSP configs and models local and pass "
            "their Windows paths with --config or --model."
        )
    if not path.is_file():
        raise FieldDemoPreflightError(f"Expected {label} to be a file, got: {path}")


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise FieldDemoPreflightError(f"RTSP config is not valid JSON: {path.name}") from error

    if not isinstance(value, dict):
        raise FieldDemoPreflightError(f"RTSP config must be a JSON object: {path.name}")
    return value


def _select_camera_config(raw_config: dict[str, Any]) -> dict[str, Any]:
    cameras = raw_config.get("cameras")
    if isinstance(cameras, list):
        for camera in cameras:
            if isinstance(camera, dict) and camera.get("source_type", "rtsp") == "rtsp":
                return camera
        raise FieldDemoPreflightError("RTSP config does not contain an RTSP camera entry")
    return raw_config


def _require_rtsp_camera_config(camera_config: dict[str, Any]) -> str:
    source_type = str(camera_config.get("source_type", "rtsp"))
    if source_type != "rtsp":
        raise FieldDemoPreflightError("RTSP config source_type must be 'rtsp'")

    camera_id = str(camera_config.get("camera_id") or "unknown")
    stream_url = camera_config.get("stream_url")
    if not isinstance(stream_url, str) or not stream_url.strip():
        raise FieldDemoPreflightError(f"Missing RTSP stream_url for camera {camera_id}")
    if "<" in stream_url or "LOCAL_ONLY" in stream_url:
        raise FieldDemoPreflightError(
            f"RTSP stream_url for camera {camera_id} still looks like a placeholder"
        )
    return camera_id


def _select_runtime_camera(config: Any) -> Any:
    from app.calibration.models import CameraConfig, UtymConfig

    if isinstance(config, CameraConfig):
        return config
    if isinstance(config, UtymConfig):
        for camera in config.cameras:
            if camera.source_type == "rtsp":
                return camera
    raise FieldDemoPreflightError("Runtime config does not contain an RTSP camera")


def _write_preflight_failure_report(args: argparse.Namespace, message: str) -> None:
    report_output = getattr(args, "report_output", None)
    if not report_output:
        return

    path = Path(report_output).expanduser()
    try:
        _write_json_report(
            path,
            {
                "generated_at": _utc_now(),
                "site": "T.UTYM#2",
                "status": "rtsp_preflight_failed",
                "message": message,
                "safety_note": _report_safety_note(),
            },
        )
    except OSError:
        return


def _run_connection_test(source: Any, frame_count: int) -> dict[str, Any]:
    started = time.perf_counter()
    frames_read = 0
    first_frame_shape: dict[str, int] | None = None

    source.open()
    try:
        for _ in range(frame_count):
            frame = source.read_frame()
            frames_read += 1
            if first_frame_shape is None:
                first_frame_shape = _frame_shape_summary(frame)
    finally:
        source.close()

    elapsed_seconds = max(time.perf_counter() - started, 0.000001)
    return {
        "requested_frames": frame_count,
        "frames_read": frames_read,
        "first_frame_shape": first_frame_shape or {},
        "elapsed_seconds": round(elapsed_seconds, 3),
        "average_fps": round(frames_read / elapsed_seconds, 2),
    }


def _frame_shape_summary(frame: Any) -> dict[str, int]:
    shape = getattr(frame, "shape", None)
    if not isinstance(shape, tuple) or len(shape) < 2:
        return {}

    return {"height": int(shape[0]), "width": int(shape[1])}


def _write_rtsp_report(
    inputs: RtspFieldDemoInputs,
    *,
    status: str,
    message: str | None = None,
    exit_code: int | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    if inputs.report_output is None:
        return

    payload: dict[str, Any] = {
        "generated_at": _utc_now(),
        "site": "T.UTYM#2",
        "status": status,
        "camera_id": inputs.camera_id,
        "config": _safe_file_summary(inputs.config),
        "model": _safe_file_summary(inputs.model),
        "confidence_threshold": inputs.confidence_threshold,
        "iou_threshold": inputs.iou_threshold,
        "safety_note": _report_safety_note(),
    }
    if message is not None:
        payload["message"] = message
    if exit_code is not None:
        payload["exit_code"] = exit_code
    if details is not None:
        payload["details"] = details

    _write_json_report(inputs.report_output, payload)


if __name__ == "__main__":
    raise SystemExit(run())
