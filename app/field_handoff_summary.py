"""Build a safe field handoff summary from local T.UTYM#2 reports.

The summary is designed for post-run communication: it includes only report
labels, file names, status values, and safety flags. It rejects report payloads
that contain RTSP URLs, IP addresses, credentials, or full local paths.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

EXPECTED_SITE = "T.UTYM#2"
ALLOWED_LABELS = {
    "offline_readiness",
    "offline_package_manifest",
    "config_validation",
    "rtsp_connection",
    "local_demo",
    "rtsp_demo",
    "table_accuracy",
    "dashboard_state",
    "dashboard_state_validation",
}
FORBIDDEN_KEYWORDS = ("rtsp://", "password", "passwd", "credential", "secret", "token")
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
FULL_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"/(?:home|Users|workspace|mnt|media|var|tmp)/"),
)


class FieldHandoffSummaryError(ValueError):
    """Raised when a field handoff summary input is missing or unsafe."""


@dataclass(frozen=True)
class ReportInput:
    """Single labeled safe report input."""

    label: str
    path: Path


@dataclass(frozen=True)
class ReportSummary:
    """Safe summary of one input report."""

    label: str
    file_name: str
    report_type: str
    status: str
    safe_to_share: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "file_name": self.file_name,
            "report_type": self.report_type,
            "status": self.status,
            "safe_to_share": self.safe_to_share,
        }


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a safe T.UTYM#2 field handoff summary from local JSON reports."
    )
    parser.add_argument(
        "--input",
        action="append",
        default=[],
        metavar="LABEL=PATH",
        help="Input report mapping. Example: --input offline_readiness=offline_readiness.json",
    )
    parser.add_argument("--output", required=True, help="Safe handoff summary JSON output path.")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    try:
        inputs = [_parse_input_mapping(raw) for raw in args.input]
        payload = build_handoff_summary(inputs)
    except FieldHandoffSummaryError as exc:
        parser.exit(status=1, message=f"T.UTYM#2 field handoff summary failed: {exc}\n")

    output = Path(args.output).expanduser()
    if output.suffix.lower() != ".json":
        parser.exit(status=2, message="T.UTYM#2 field handoff summary failed: output must be .json\n")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["overall_status"] != "critical" else 1


def build_handoff_summary(inputs: Sequence[ReportInput]) -> dict[str, Any]:
    if not inputs:
        raise FieldHandoffSummaryError("At least one input report is required.")
    summaries = [_summarize_report(report_input) for report_input in inputs]
    overall_status = _choose_overall_status([summary.status for summary in summaries])
    return {
        "report_type": "field_handoff_summary",
        "site": EXPECTED_SITE,
        "overall_status": overall_status,
        "report_count": len(summaries),
        "reports": [summary.to_dict() for summary in summaries],
        "shareable_summary": {
            "site": EXPECTED_SITE,
            "overall_status": overall_status,
            "report_count": len(summaries),
            "safe_to_share": all(summary.safe_to_share for summary in summaries),
        },
        "safety": {
            "contains_rtsp_url": False,
            "contains_credentials": False,
            "contains_ip_address": False,
            "contains_full_local_path": False,
            "contains_image_or_video": False,
        },
    }


def _parse_input_mapping(raw: str) -> ReportInput:
    if "=" not in raw:
        raise FieldHandoffSummaryError("Input must use LABEL=PATH format.")
    label, path_text = raw.split("=", 1)
    label = label.strip()
    if label not in ALLOWED_LABELS:
        raise FieldHandoffSummaryError(f"Unsupported input label: {label}.")
    path = Path(path_text.strip()).expanduser()
    if path.suffix.lower() != ".json":
        raise FieldHandoffSummaryError("Input reports must be .json files.")
    return ReportInput(label=label, path=path)


def _summarize_report(report_input: ReportInput) -> ReportSummary:
    if not report_input.path.is_file():
        raise FieldHandoffSummaryError(f"Input report was not found for label {report_input.label}.")
    text = report_input.path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise FieldHandoffSummaryError(f"Input report JSON is invalid for label {report_input.label}: {exc.msg}.") from exc
    if not isinstance(payload, dict):
        raise FieldHandoffSummaryError(f"Input report root must be an object for label {report_input.label}.")
    _reject_sensitive_values(payload)

    site = payload.get("site")
    if site is not None and site != EXPECTED_SITE:
        raise FieldHandoffSummaryError(f"Input report site must be {EXPECTED_SITE} for label {report_input.label}.")

    return ReportSummary(
        label=report_input.label,
        file_name=report_input.path.name,
        report_type=str(payload.get("report_type", report_input.label)),
        status=_extract_status(payload),
        safe_to_share=_extract_safe_to_share(payload),
    )


def _extract_status(payload: dict[str, Any]) -> str:
    raw_status = payload.get("overall_status", payload.get("status", "unknown"))
    status = str(raw_status).lower()
    if status in {"pass", "passed", "ok", "normal", "ready"}:
        return "normal"
    if status in {"warn", "warning", "not_ready"}:
        return "warning"
    if status in {"fail", "failed", "critical", "error"}:
        return "critical"
    return "unknown"


def _extract_safe_to_share(payload: dict[str, Any]) -> bool:
    safety = payload.get("safety")
    if not isinstance(safety, dict):
        return True
    unsafe_flags = [value for value in safety.values() if value is True]
    return not unsafe_flags


def _choose_overall_status(statuses: Sequence[str]) -> str:
    if "critical" in statuses:
        return "critical"
    if "warning" in statuses:
        return "warning"
    if "unknown" in statuses:
        return "warning"
    return "normal"


def _reject_sensitive_values(value: Any) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _reject_sensitive_values(item)
        return
    if isinstance(value, list):
        for item in value:
            _reject_sensitive_values(item)
        return
    if not isinstance(value, str):
        return
    lowered = value.lower()
    if any(keyword in lowered for keyword in FORBIDDEN_KEYWORDS):
        raise FieldHandoffSummaryError("Input report contains a forbidden sensitive keyword or RTSP-like value.")
    if IP_PATTERN.search(value):
        raise FieldHandoffSummaryError("Input report must not contain IP addresses.")
    if any(pattern.search(value) for pattern in FULL_PATH_PATTERNS):
        raise FieldHandoffSummaryError("Input report must not contain full local paths.")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
