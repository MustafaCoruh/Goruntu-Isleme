"""Safe T.UTYM#2 table accuracy report validator.

The validator checks the machine-readable JSON report produced from the
operator model-performance review. It intentionally rejects reports that contain
RTSP URLs, credentials, full local paths, or inconsistent table metrics.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

EXPECTED_REPORT_TYPE = "table_accuracy_evaluation"
EXPECTED_SITE = "T.UTYM#2"
EXPECTED_TABLE_COUNT = 14
SCHEMA_VERSION = "1.0"
ALLOWED_TEST_TYPES = frozenset({"local_video", "rtsp_live"})
ALLOWED_LIGHTING = frozenset({"normal", "dim", "bright", "mixed"})
ALLOWED_OCCUPANCY_LEVELS = frozenset({"empty", "low", "medium", "high"})
ALLOWED_GROUND_TRUTH = frozenset({"occupied", "empty"})
ALLOWED_PREDICTIONS = frozenset({"occupied", "empty", "unknown"})
ALLOWED_LABELS = frozenset({"TP", "TN", "FP", "FN", "UNK"})
EXPECTED_TABLE_IDS = tuple(f"table_{index:02d}" for index in range(1, EXPECTED_TABLE_COUNT + 1))

SENSITIVE_PATTERNS = (
    re.compile(r"rtsp://", re.IGNORECASE),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"\\\\[^\\]+\\[^\\]+"),
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"passwd", re.IGNORECASE),
    re.compile(r"username", re.IGNORECASE),
)


class TableAccuracyReportError(ValueError):
    """Raised when a table accuracy report is invalid or unsafe."""


@dataclass(frozen=True)
class ValidationResult:
    """Safe validation result for a table accuracy report."""

    site: str
    camera_id: str
    table_count: int
    accuracy: float | None
    tp: int
    tn: int
    fp: int
    fn: int
    unk: int

    def to_safe_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable summary without sensitive values."""

        return {
            "site": self.site,
            "camera_id": self.camera_id,
            "table_count": self.table_count,
            "accuracy": self.accuracy,
            "tp": self.tp,
            "tn": self.tn,
            "fp": self.fp,
            "fn": self.fn,
            "unk": self.unk,
            "status": "valid",
        }


def build_argument_parser() -> argparse.ArgumentParser:
    """Create CLI parser for local report validation."""

    parser = argparse.ArgumentParser(
        description=(
            "Validate a safe T.UTYM#2 table accuracy JSON report. The report must "
            "not contain images, RTSP URLs, credentials, IP addresses, or full paths."
        )
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Path to local table accuracy JSON report to validate.",
    )
    parser.add_argument(
        "--summary-output",
        help="Optional path for a safe validation summary JSON file.",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    """Validate a local table accuracy report and print a safe summary."""

    parser = build_argument_parser()
    args = parser.parse_args(argv)
    report_path = Path(args.report).expanduser()
    summary_output = Path(args.summary_output).expanduser() if args.summary_output else None

    try:
        result = validate_report_file(report_path)
        safe_summary = result.to_safe_dict()
        if summary_output is not None:
            _require_json_output(summary_output)
            _write_json(summary_output, safe_summary)
        print(json.dumps(safe_summary, ensure_ascii=False, indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, TableAccuracyReportError) as error:
        parser.exit(status=2, message=f"T.UTYM#2 table accuracy report validation failed: {error}\n")

    return 0


def validate_report_file(path: Path) -> ValidationResult:
    """Load and validate a table accuracy report from disk."""

    if path.suffix.lower() != ".json":
        raise TableAccuracyReportError(f"Report must be a .json file, got: {path.name}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return validate_report(payload)


def validate_report(payload: Mapping[str, Any]) -> ValidationResult:
    """Validate report structure, safety, and aggregate metrics."""

    _require_no_sensitive_strings(payload)
    _require_equal(payload.get("report_type"), EXPECTED_REPORT_TYPE, "report_type")
    _require_equal(payload.get("schema_version"), SCHEMA_VERSION, "schema_version")
    _require_equal(payload.get("site"), EXPECTED_SITE, "site")

    camera_id = _require_non_empty_string(payload.get("camera_id"), "camera_id")
    _validate_evaluation_context(_require_mapping(payload.get("evaluation_context"), "evaluation_context"))
    _validate_inputs(_require_mapping(payload.get("inputs"), "inputs"))
    tables = _validate_tables(_require_list(payload.get("tables"), "tables"))
    calculated = _calculate_summary(tables)
    _validate_summary(_require_mapping(payload.get("summary"), "summary"), calculated)
    _validate_decision(_require_mapping(payload.get("decision"), "decision"))
    _validate_safety(_require_mapping(payload.get("safety"), "safety"))

    return ValidationResult(
        site=EXPECTED_SITE,
        camera_id=camera_id,
        table_count=calculated["table_count"],
        accuracy=calculated["accuracy"],
        tp=calculated["tp"],
        tn=calculated["tn"],
        fp=calculated["fp"],
        fn=calculated["fn"],
        unk=calculated["unk"],
    )


def _validate_evaluation_context(context: Mapping[str, Any]) -> None:
    _require_in(context.get("test_type"), ALLOWED_TEST_TYPES, "evaluation_context.test_type")
    _require_in(context.get("lighting"), ALLOWED_LIGHTING, "evaluation_context.lighting")
    _require_in(context.get("occupancy_level"), ALLOWED_OCCUPANCY_LEVELS, "evaluation_context.occupancy_level")
    _require_bool(context.get("camera_angle_changed"), "evaluation_context.camera_angle_changed")
    _require_bool(context.get("calibration_recent"), "evaluation_context.calibration_recent")
    _require_number(context.get("duration_minutes"), "evaluation_context.duration_minutes", minimum=0)
    _require_number(context.get("average_fps"), "evaluation_context.average_fps", minimum=0)


def _validate_inputs(inputs: Mapping[str, Any]) -> None:
    for key in ("config_name", "model_name", "model_version"):
        value = _require_non_empty_string(inputs.get(key), f"inputs.{key}")
        if any(separator in value for separator in ("/", "\\")):
            raise TableAccuracyReportError(f"inputs.{key} must be a filename only, not a path")


def _validate_tables(tables: list[Any]) -> list[Mapping[str, Any]]:
    if len(tables) != EXPECTED_TABLE_COUNT:
        raise TableAccuracyReportError(f"tables must contain {EXPECTED_TABLE_COUNT} records")

    validated: list[Mapping[str, Any]] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(tables, start=1):
        table = _require_mapping(item, f"tables[{index}]")
        table_id = _require_non_empty_string(table.get("table_id"), f"tables[{index}].table_id")
        if table_id not in EXPECTED_TABLE_IDS:
            raise TableAccuracyReportError(f"Invalid table_id: {table_id}")
        if table_id in seen_ids:
            raise TableAccuracyReportError(f"Duplicate table_id: {table_id}")
        seen_ids.add(table_id)

        ground_truth = _require_in(table.get("ground_truth"), ALLOWED_GROUND_TRUTH, f"{table_id}.ground_truth")
        prediction = _require_in(table.get("prediction"), ALLOWED_PREDICTIONS, f"{table_id}.prediction")
        label = _require_in(table.get("label"), ALLOWED_LABELS, f"{table_id}.label")
        _require_label_matches_values(ground_truth, prediction, label, table_id)

        confidence = table.get("confidence")
        if confidence is not None:
            _require_number(confidence, f"{table_id}.confidence", minimum=0, maximum=1)
        safe_note = table.get("safe_note")
        if safe_note is not None and not isinstance(safe_note, str):
            raise TableAccuracyReportError(f"{table_id}.safe_note must be a string or null")
        validated.append(table)

    missing_ids = set(EXPECTED_TABLE_IDS) - seen_ids
    if missing_ids:
        raise TableAccuracyReportError(f"Missing table IDs: {sorted(missing_ids)}")
    return validated


def _require_label_matches_values(ground_truth: str, prediction: str, label: str, table_id: str) -> None:
    expected_label = _expected_label(ground_truth, prediction)
    if label != expected_label:
        raise TableAccuracyReportError(
            f"{table_id}.label must be {expected_label} for ground_truth={ground_truth} "
            f"and prediction={prediction}, got {label}"
        )


def _expected_label(ground_truth: str, prediction: str) -> str:
    if prediction == "unknown":
        return "UNK"
    if ground_truth == "occupied" and prediction == "occupied":
        return "TP"
    if ground_truth == "empty" and prediction == "empty":
        return "TN"
    if ground_truth == "empty" and prediction == "occupied":
        return "FP"
    if ground_truth == "occupied" and prediction == "empty":
        return "FN"
    raise TableAccuracyReportError(f"Unsupported ground_truth/prediction pair: {ground_truth}/{prediction}")


def _calculate_summary(tables: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    counts = {label.lower(): 0 for label in ALLOWED_LABELS}
    table_count = 0
    for table in tables:
        table_count += 1
        counts[str(table["label"]).lower()] += 1

    correct = counts["tp"] + counts["tn"]
    incorrect = counts["fp"] + counts["fn"]
    evaluated = table_count - counts["unk"]
    accuracy = None if evaluated == 0 else round(correct / evaluated, 4)
    return {
        "table_count": table_count,
        "tp": counts["tp"],
        "tn": counts["tn"],
        "fp": counts["fp"],
        "fn": counts["fn"],
        "unk": counts["unk"],
        "correct": correct,
        "incorrect": incorrect,
        "evaluated": evaluated,
        "accuracy": accuracy,
    }


def _validate_summary(summary: Mapping[str, Any], calculated: Mapping[str, Any]) -> None:
    for key, expected_value in calculated.items():
        actual_value = summary.get(key)
        if key == "accuracy" and actual_value is not None:
            actual_value = round(float(actual_value), 4)
        if actual_value != expected_value:
            raise TableAccuracyReportError(
                f"summary.{key} must be {expected_value}, got {summary.get(key)}"
            )


def _validate_decision(decision: Mapping[str, Any]) -> None:
    _require_bool(decision.get("prototype_ready"), "decision.prototype_ready")
    _require_non_empty_string(decision.get("recommended_next_action"), "decision.recommended_next_action")
    _require_bool(decision.get("requires_recalibration"), "decision.requires_recalibration")
    _require_bool(decision.get("requires_model_change"), "decision.requires_model_change")
    _require_bool(decision.get("requires_camera_adjustment"), "decision.requires_camera_adjustment")


def _validate_safety(safety: Mapping[str, Any]) -> None:
    expected_keys = {
        "contains_image_or_video",
        "contains_rtsp_url",
        "contains_ip_address",
        "contains_credentials",
        "contains_person_name",
        "contains_full_local_path",
    }
    missing = expected_keys - set(safety)
    if missing:
        raise TableAccuracyReportError(f"safety is missing keys: {sorted(missing)}")
    for key in expected_keys:
        if safety.get(key) is not False:
            raise TableAccuracyReportError(f"safety.{key} must be false")


def _require_no_sensitive_strings(value: Any, path: str = "report") -> None:
    if isinstance(value, str):
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(value):
                raise TableAccuracyReportError(f"Sensitive value pattern found at {path}")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            _require_no_sensitive_strings(item, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _require_no_sensitive_strings(item, f"{path}[{index}]")


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TableAccuracyReportError(f"{field_name} must be an object")
    return value


def _require_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise TableAccuracyReportError(f"{field_name} must be a list")
    return value


def _require_equal(value: Any, expected: Any, field_name: str) -> None:
    if value != expected:
        raise TableAccuracyReportError(f"{field_name} must be {expected!r}, got {value!r}")


def _require_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TableAccuracyReportError(f"{field_name} must be a non-empty string")
    return value


def _require_in(value: Any, allowed: frozenset[str], field_name: str) -> str:
    if value not in allowed:
        raise TableAccuracyReportError(f"{field_name} must be one of {sorted(allowed)}, got {value!r}")
    return str(value)


def _require_bool(value: Any, field_name: str) -> None:
    if not isinstance(value, bool):
        raise TableAccuracyReportError(f"{field_name} must be true or false")


def _require_number(value: Any, field_name: str, *, minimum: float, maximum: float | None = None) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TableAccuracyReportError(f"{field_name} must be a number")
    if value < minimum:
        raise TableAccuracyReportError(f"{field_name} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise TableAccuracyReportError(f"{field_name} must be <= {maximum}")


def _require_json_output(path: Path) -> None:
    if path.suffix.lower() != ".json":
        raise TableAccuracyReportError("summary-output must be a .json file")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
