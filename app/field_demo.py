"""Operator-friendly local video demo runner for T.UTYM#2.

This module performs safe preflight checks before delegating to the existing
``app.main`` video demo flow. It intentionally keeps real videos, RTSP URLs,
and model artifacts outside the repository.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

SUPPORTED_VIDEO_EXTENSIONS = frozenset({".avi", ".m4v", ".mkv", ".mov", ".mp4"})
SUPPORTED_SOURCE_EXTENSIONS = SUPPORTED_VIDEO_EXTENSIONS
DEFAULT_CONFIG = r"C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json"
DEFAULT_MODEL = r"C:\FTMC_FIELD_DATA\models\person_detector.onnx"


class FieldDemoPreflightError(RuntimeError):
    """Raised when local field demo inputs are missing or unsafe."""


@dataclass(frozen=True)
class FieldDemoInputs:
    """Validated local field demo paths and detector thresholds."""

    config: Path
    source: Path
    model: Path
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    window_name: str = "T.UTYM#2 Local Field Demo"
    report_output: Path | None = None


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the operator-friendly T.UTYM#2 demo parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Run the T.UTYM#2 local field demo against a local video file. "
            "Do not pass real RTSP URLs or sensitive paths that will be committed."
        )
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help=(
            "Path to local calibrated config JSON. Defaults to "
            f"{DEFAULT_CONFIG}. This file should stay outside the repository."
        ),
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Path to a local video on the field machine; never commit this file.",
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
        default="T.UTYM#2 Local Field Demo",
        help="OpenCV window title for the debug overlay.",
    )
    # MERGE-CHECK: report-output must stay available for safe local demo reports.
    parser.add_argument(
        "--report-output",
        help=(
            "Optional path for a safe JSON run report. The report stores filenames, "
            "extensions, thresholds, and run status, but not real videos, "
            "RTSP URLs, full local paths, or credentials."
        ),
    )
    return parser


def validate_inputs(args: argparse.Namespace) -> FieldDemoInputs:
    """Validate local demo inputs before importing OpenCV-heavy modules."""

    config = Path(args.config).expanduser()
    source = Path(args.source).expanduser()
    model = Path(args.model).expanduser()
    report_output = Path(args.report_output).expanduser() if args.report_output else None

    _require_existing_file(config, "config JSON")
    _require_existing_file(source, "local video source")
    _require_existing_file(model, "ONNX person detector model")
    _require_supported_source(source)
    _require_probability(args.confidence_threshold, "confidence-threshold")
    _require_probability(args.iou_threshold, "iou-threshold")
    if report_output is not None:
        _require_report_output_path(report_output)

    return FieldDemoInputs(
        config=config,
        source=source,
        model=model,
        confidence_threshold=args.confidence_threshold,
        iou_threshold=args.iou_threshold,
        window_name=args.window_name,
        report_output=report_output,
    )


def build_app_main_argv(inputs: FieldDemoInputs) -> list[str]:
    """Convert validated field-demo inputs into ``app.main`` arguments."""

    return [
        "--config",
        str(inputs.config),
        "--source",
        str(inputs.source),
        "--model",
        str(inputs.model),
        "--confidence-threshold",
        str(inputs.confidence_threshold),
        "--iou-threshold",
        str(inputs.iou_threshold),
        "--window-name",
        inputs.window_name,
    ]


def run(argv: Sequence[str] | None = None) -> int:
    """Run preflight checks and delegate to the existing demo implementation."""

    parser = build_argument_parser()
    args = parser.parse_args(argv)

    try:
        inputs = validate_inputs(args)
    except FieldDemoPreflightError as error:
        _write_preflight_failure_report(args, str(error))
        parser.exit(status=2, message=f"T.UTYM#2 field demo preflight failed: {error}\n")

    from app.main import main as app_main

    _write_run_report(inputs, status="started")
    try:
        exit_code = app_main(build_app_main_argv(inputs))
    except Exception as error:
        _write_run_report(inputs, status="failed", message=str(error))
        raise

    _write_run_report(inputs, status="completed", exit_code=exit_code)
    return exit_code


def _require_report_output_path(path: Path) -> None:
    if path.suffix.lower() != ".json":
        raise FieldDemoPreflightError(
            f"Report output must be a .json file, got: {path}. "
            "Use a local path such as C:\\FTMC_FIELD_DATA\\reports\\demo_result.json."
        )


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
                "status": "preflight_failed",
                "message": message,
                "safety_note": _report_safety_note(),
            },
        )
    except OSError:
        # Preflight errors should still be shown even if the optional report path
        # is not writable. The operator can fix the reported input issue first.
        return


def _write_run_report(
    inputs: FieldDemoInputs,
    *,
    status: str,
    message: str | None = None,
    exit_code: int | None = None,
) -> None:
    if inputs.report_output is None:
        return

    payload: dict[str, Any] = {
        "generated_at": _utc_now(),
        "site": "T.UTYM#2",
        "status": status,
        "source": _safe_file_summary(inputs.source),
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

    _write_json_report(inputs.report_output, payload)


def _safe_file_summary(path: Path) -> dict[str, str]:
    return {"name": path.name, "extension": path.suffix.lower()}


def _write_json_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _report_safety_note() -> str:
    return (
        "This report must not contain real videos, RTSP URLs, IP addresses, "
        "credentials, or participant information."
    )


def _require_existing_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FieldDemoPreflightError(
            f"Missing {label}: {path}. Keep real field files outside the repository "
            "and pass their local Windows paths with --config, --source, or --model."
        )
    if not path.is_file():
        raise FieldDemoPreflightError(f"Expected {label} to be a file, got: {path}")


def _require_supported_source(path: Path) -> None:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SOURCE_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_SOURCE_EXTENSIONS))
        raise FieldDemoPreflightError(
            f"Unsupported source extension for {path}. Supported extensions: {supported}. "
            "Use a local video first; RTSP live runner will be handled separately."
        )


def _require_probability(value: float, label: str) -> None:
    if not 0 <= value <= 1:
        raise FieldDemoPreflightError(f"{label} must be between 0 and 1, got {value}")


if __name__ == "__main__":
    raise SystemExit(run())
