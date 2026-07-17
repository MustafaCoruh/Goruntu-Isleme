"""Build a safe R4 acceptance gate report for T.UTYM#2.

R4 is the controlled field-acceptance stage. This module intentionally works on
already-sanitized JSON reports only: dashboard_state.json, field_handoff_summary.json,
and table_accuracy_report.json. It produces one compact JSON decision that can be
shared without RTSP URLs, camera IPs, credentials, images/videos, or full local paths.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from app.dashboard_state_validator import DashboardStateValidationError, validate_dashboard_state
from app.table_accuracy_report import TableAccuracyReportError, validate_report as validate_table_accuracy_report

EXPECTED_SITE = "T.UTYM#2"
EXPECTED_CAMERA_ID = "TUTYM2-CAM-001"
EXPECTED_TABLE_COUNT = 14
REQUIRED_HANDOFF_REPORTS = frozenset({"dashboard_state", "table_accuracy"})


class R4AcceptanceError(ValueError):
    """Raised when R4 acceptance inputs are missing, invalid, or unsafe."""


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a safe T.UTYM#2 R4 acceptance gate report.")
    parser.add_argument("--dashboard-state", required=True, help="Path to safe dashboard_state.json.")
    parser.add_argument("--handoff-summary", required=True, help="Path to safe field_handoff_summary.json.")
    parser.add_argument("--table-accuracy", required=True, help="Path to safe table accuracy report JSON.")
    parser.add_argument("--output", required=True, help="Path for the safe R4 acceptance JSON report.")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    try:
        payload = build_r4_acceptance_report(
            dashboard_state_path=Path(args.dashboard_state).expanduser(),
            handoff_summary_path=Path(args.handoff_summary).expanduser(),
            table_accuracy_path=Path(args.table_accuracy).expanduser(),
        )
    except (OSError, json.JSONDecodeError, DashboardStateValidationError, TableAccuracyReportError, R4AcceptanceError) as error:
        parser.exit(status=2, message=f"T.UTYM#2 R4 acceptance failed: {error}\n")

    output = Path(args.output).expanduser()
    if output.suffix.lower() != ".json":
        parser.exit(status=2, message="T.UTYM#2 R4 acceptance failed: output must be .json\n")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ready_for_controlled_field_acceptance"] else 1


def build_r4_acceptance_report(*, dashboard_state_path: Path, handoff_summary_path: Path, table_accuracy_path: Path) -> dict[str, Any]:
    dashboard_state = _read_json_file(dashboard_state_path, "dashboard_state")
    handoff_summary = _read_json_file(handoff_summary_path, "field_handoff_summary")
    table_accuracy = _read_json_file(table_accuracy_path, "table_accuracy")

    validate_dashboard_state(dashboard_state)
    table_result = validate_table_accuracy_report(table_accuracy)
    _validate_handoff_summary(handoff_summary)

    blockers: list[str] = []
    warnings: list[str] = []

    if dashboard_state.get("overall_status") == "critical":
        blockers.append("dashboard_state overall_status is critical")
    if dashboard_state.get("table_summary", {}).get("total") != EXPECTED_TABLE_COUNT:
        blockers.append("dashboard_state table_summary.total must be 14")
    if table_result.table_count != EXPECTED_TABLE_COUNT:
        blockers.append("table_accuracy table_count must be 14")
    if handoff_summary.get("overall_status") == "critical":
        blockers.append("field_handoff_summary overall_status is critical")
    if not handoff_summary.get("shareable_summary", {}).get("safe_to_share"):
        blockers.append("field_handoff_summary shareable_summary.safe_to_share must be true")

    accuracy = table_result.accuracy
    if accuracy is None:
        warnings.append("table accuracy is not available")
    elif accuracy < 0.80:
        warnings.append("table accuracy is below 0.80; R4 can continue only as controlled pilot")
    if table_result.fn > 0:
        warnings.append("table accuracy has false negatives; operator must review missed occupancy cases")
    if dashboard_state.get("warnings"):
        warnings.append("dashboard_state contains warnings")

    overall_status = "blocked" if blockers else "ready_with_warnings" if warnings else "ready"
    return {
        "report_type": "r4_acceptance_gate",
        "site": EXPECTED_SITE,
        "camera_id": EXPECTED_CAMERA_ID,
        "overall_status": overall_status,
        "ready_for_controlled_field_acceptance": overall_status in {"ready", "ready_with_warnings"},
        "required_inputs": {
            "dashboard_state": dashboard_state_path.name,
            "field_handoff_summary": handoff_summary_path.name,
            "table_accuracy": table_accuracy_path.name,
        },
        "summary": {
            "table_count": EXPECTED_TABLE_COUNT,
            "dashboard_overall_status": dashboard_state.get("overall_status"),
            "handoff_overall_status": handoff_summary.get("overall_status"),
            "table_accuracy": accuracy,
            "false_positive_count": table_result.fp,
            "false_negative_count": table_result.fn,
            "unknown_count": table_result.unk,
        },
        "blockers": blockers,
        "warnings": warnings,
        "safety": {
            "contains_rtsp_url": False,
            "contains_credentials": False,
            "contains_image_or_video": False,
            "contains_full_local_path": False,
            "contains_ip_address": False,
        },
    }


def _read_json_file(path: Path, label: str) -> Mapping[str, Any]:
    if path.suffix.lower() != ".json":
        raise R4AcceptanceError(f"{label} input must be a .json file")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise R4AcceptanceError(f"{label} input root must be an object")
    return payload


def _validate_handoff_summary(payload: Mapping[str, Any]) -> None:
    if payload.get("report_type") != "field_handoff_summary":
        raise R4AcceptanceError("field_handoff_summary report_type is required")
    if payload.get("site") != EXPECTED_SITE:
        raise R4AcceptanceError(f"field_handoff_summary site must be {EXPECTED_SITE}")
    shareable = payload.get("shareable_summary")
    if not isinstance(shareable, Mapping):
        raise R4AcceptanceError("field_handoff_summary shareable_summary is required")
    if shareable.get("safe_to_share") is not True:
        raise R4AcceptanceError("field_handoff_summary shareable_summary.safe_to_share must be true")
    safety = payload.get("safety")
    if not isinstance(safety, Mapping):
        raise R4AcceptanceError("field_handoff_summary safety is required")
    for key, value in safety.items():
        if value is True:
            raise R4AcceptanceError(f"field_handoff_summary safety.{key} must not be true")
    reports = payload.get("reports")
    if not isinstance(reports, list):
        raise R4AcceptanceError("field_handoff_summary reports must be a list")
    labels = {str(report.get("label")) for report in reports if isinstance(report, Mapping)}
    missing = REQUIRED_HANDOFF_REPORTS - labels
    if missing:
        raise R4AcceptanceError(f"field_handoff_summary missing required report labels: {sorted(missing)}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
