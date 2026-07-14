"""Validate safe T.UTYM#2 dashboard_state.json files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

EXPECTED_REPORT_TYPE = "dashboard_state"
EXPECTED_SITE = "T.UTYM#2"
EXPECTED_CAMERA_ID = "TUTYM2-CAM-001"
EXPECTED_TABLE_COUNT = 14
# MERGE-CHECK: dashboard-state-validator must validate 14 T.UTYM#2 table cards.
ALLOWED_OVERALL_STATUS = frozenset({"normal", "warning", "critical", "not_ready"})
ALLOWED_CONNECTION_STATUS = frozenset({"connected", "disconnected", "not_tested"})
ALLOWED_TABLE_STATES = frozenset({"occupied", "empty", "unknown", "no_data"})
ALLOWED_COLORS = frozenset({"red_or_orange", "green", "yellow", "gray"})
ALLOWED_SOURCE_STATUS = frozenset({"loaded", "missing", "invalid_json"})
EXPECTED_SOURCE_KEYS = frozenset({"offline_readiness", "config_validation", "rtsp_connection", "table_accuracy"})
EXPECTED_SAFETY_KEYS = frozenset({"contains_rtsp_url", "contains_credentials", "contains_image_or_video", "contains_full_local_path"})


class DashboardStateValidationError(ValueError):
    """Raised when dashboard_state.json is invalid or unsafe."""


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a safe T.UTYM#2 dashboard_state.json file.")
    parser.add_argument("--state", required=True, help="Path to dashboard_state.json to validate.")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    try:
        validate_dashboard_state_file(Path(args.state).expanduser())
    except (OSError, json.JSONDecodeError, DashboardStateValidationError) as error:
        parser.exit(status=2, message=f"T.UTYM#2 dashboard state validation failed: {error}\n")
    print(json.dumps({"status": "valid", "site": EXPECTED_SITE, "camera_id": EXPECTED_CAMERA_ID}, ensure_ascii=False, indent=2))
    return 0


def validate_dashboard_state_file(path: Path) -> None:
    if path.suffix.lower() != ".json":
        raise DashboardStateValidationError(f"Dashboard state must be a .json file, got: {path.name}")
    validate_dashboard_state(json.loads(path.read_text(encoding="utf-8")))


def validate_dashboard_state(payload: Mapping[str, Any]) -> None:
    _require_equal(payload.get("report_type"), EXPECTED_REPORT_TYPE, "report_type")
    _require_equal(payload.get("site"), EXPECTED_SITE, "site")
    _require_equal(payload.get("camera_id"), EXPECTED_CAMERA_ID, "camera_id")
    _require_in(payload.get("overall_status"), ALLOWED_OVERALL_STATUS, "overall_status")
    _require_in(payload.get("connection_status"), ALLOWED_CONNECTION_STATUS, "connection_status")
    average_fps = payload.get("average_fps")
    if average_fps is not None:
        _require_number(average_fps, "average_fps", minimum=0)
    _validate_table_summary(_require_mapping(payload.get("table_summary"), "table_summary"))
    _validate_tables(_require_list(payload.get("tables"), "tables"), payload["table_summary"])
    _validate_string_list(payload.get("warnings"), "warnings")
    _validate_string_list(payload.get("criticals"), "criticals")
    _validate_sources(_require_mapping(payload.get("sources"), "sources"))
    _validate_safety(_require_mapping(payload.get("safety"), "safety"))


def _validate_table_summary(summary: Mapping[str, Any]) -> None:
    expected_keys = {"total", "occupied", "empty", "unknown", "no_data"}
    missing = expected_keys - set(summary)
    if missing:
        raise DashboardStateValidationError(f"table_summary missing keys: {sorted(missing)}")
    if summary.get("total") != EXPECTED_TABLE_COUNT:
        raise DashboardStateValidationError("table_summary.total must be 14")
    for key in expected_keys:
        value = summary.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise DashboardStateValidationError(f"table_summary.{key} must be a non-negative integer")
    counted = summary["occupied"] + summary["empty"] + summary["unknown"] + summary["no_data"]
    if counted != EXPECTED_TABLE_COUNT:
        raise DashboardStateValidationError("table_summary counts must add up to 14")


def _validate_tables(tables: list[Any], summary: Mapping[str, Any]) -> None:
    if len(tables) != EXPECTED_TABLE_COUNT:
        raise DashboardStateValidationError("tables must contain 14 records")
    seen_ids: set[str] = set()
    counts = {"occupied": 0, "empty": 0, "unknown": 0, "no_data": 0}
    for index, item in enumerate(tables, start=1):
        table = _require_mapping(item, f"tables[{index}]")
        expected_id = f"table_{index:02d}"
        table_id = _require_string(table.get("table_id"), f"tables[{index}].table_id")
        if table_id in seen_ids:
            raise DashboardStateValidationError(f"Duplicate table_id: {table_id}")
        seen_ids.add(table_id)
        if table_id != expected_id:
            raise DashboardStateValidationError(f"Expected {expected_id}, got {table_id}")
        _require_string(table.get("display_name"), f"{table_id}.display_name")
        state = _require_in(table.get("state"), ALLOWED_TABLE_STATES, f"{table_id}.state")
        counts[state] += 1
        confidence = table.get("confidence")
        if confidence is not None:
            _require_number(confidence, f"{table_id}.confidence", minimum=0, maximum=1)
        label = table.get("label")
        if label is not None and not isinstance(label, str):
            raise DashboardStateValidationError(f"{table_id}.label must be string or null")
        _require_in(table.get("color"), ALLOWED_COLORS, f"{table_id}.color")
        warning = table.get("warning")
        if warning is not None and not isinstance(warning, str):
            raise DashboardStateValidationError(f"{table_id}.warning must be string or null")
    for key, value in counts.items():
        if summary.get(key) != value:
            raise DashboardStateValidationError(f"table_summary.{key} must match table states")


def _validate_string_list(value: Any, field_name: str) -> None:
    if not isinstance(value, list):
        raise DashboardStateValidationError(f"{field_name} must be a list")
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise DashboardStateValidationError(f"{field_name}[{index}] must be a string")


def _validate_sources(sources: Mapping[str, Any]) -> None:
    missing = EXPECTED_SOURCE_KEYS - set(sources)
    if missing:
        raise DashboardStateValidationError(f"sources missing keys: {sorted(missing)}")
    for key in EXPECTED_SOURCE_KEYS:
        source = _require_mapping(sources.get(key), f"sources.{key}")
        _require_string(source.get("name"), f"sources.{key}.name")
        _require_in(source.get("status"), ALLOWED_SOURCE_STATUS, f"sources.{key}.status")


def _validate_safety(safety: Mapping[str, Any]) -> None:
    missing = EXPECTED_SAFETY_KEYS - set(safety)
    if missing:
        raise DashboardStateValidationError(f"safety missing keys: {sorted(missing)}")
    for key in EXPECTED_SAFETY_KEYS:
        if safety.get(key) is not False:
            raise DashboardStateValidationError(f"safety.{key} must be false")


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise DashboardStateValidationError(f"{field_name} must be an object")
    return value


def _require_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise DashboardStateValidationError(f"{field_name} must be a list")
    return value


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DashboardStateValidationError(f"{field_name} must be a non-empty string")
    return value


def _require_equal(value: Any, expected: Any, field_name: str) -> None:
    if value != expected:
        raise DashboardStateValidationError(f"{field_name} must be {expected!r}, got {value!r}")


def _require_in(value: Any, allowed: frozenset[str], field_name: str) -> str:
    if value not in allowed:
        raise DashboardStateValidationError(f"{field_name} must be one of {sorted(allowed)}, got {value!r}")
    return str(value)


def _require_number(value: Any, field_name: str, *, minimum: float, maximum: float | None = None) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise DashboardStateValidationError(f"{field_name} must be a number")
    if value < minimum:
        raise DashboardStateValidationError(f"{field_name} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise DashboardStateValidationError(f"{field_name} must be <= {maximum}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
