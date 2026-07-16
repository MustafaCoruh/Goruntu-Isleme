"""T.UTYM#2 camera configuration validator.

This validator checks local or template camera configs without printing RTSP URLs,
credentials, full paths, or polygon details. It is intended to catch operator
mistakes before local/RTSP demos are run.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

EXPECTED_UTYM_ID = "T.UTYM#2"
EXPECTED_CAMERA_ID = "TUTYM2-CAM-001"
EXPECTED_SOURCE_TYPE = "rtsp"
EXPECTED_WIDTH = 1920
EXPECTED_HEIGHT = 1080
EXPECTED_TABLE_COUNT = 14
EXPECTED_CAPACITY = 1
LOCAL_ONLY_STREAM_PLACEHOLDER = "LOCAL_ONLY_DO_NOT_COMMIT_REAL_RTSP_URL"
RTSP_TEMPLATE_PATTERN = "rtsp://<USER>:<PASSWORD>@<CAMERA_IP>/<STREAM_PATH>"

RTSP_URL_PATTERN = re.compile(r"^rtsp://", re.IGNORECASE)


class Tutym2ConfigValidationError(ValueError):
    """Raised when a T.UTYM#2 config is structurally invalid or unsafe."""


@dataclass(frozen=True)
class ConfigValidationResult:
    """Safe validation summary that never includes stream URLs or polygons."""

    utym_id: str
    camera_id: str
    source_type: str
    width: int
    height: int
    table_count: int
    stream_url_mode: str
    status: str = "valid"

    def to_safe_dict(self) -> dict[str, Any]:
        return {
            "utym_id": self.utym_id,
            "camera_id": self.camera_id,
            "source_type": self.source_type,
            "resolution": {"width": self.width, "height": self.height},
            "table_count": self.table_count,
            "stream_url_mode": self.stream_url_mode,
            "status": self.status,
        }


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a T.UTYM#2 camera config without printing stream URLs, "
            "credentials, full paths, or polygon coordinates."
        )
    )
    parser.add_argument("--config", required=True, help="Path to config JSON to validate.")
    parser.add_argument(
        "--allow-real-rtsp",
        action="store_true",
        help="Allow a real RTSP URL in a local-only config. Never use for repository templates.",
    )
    parser.add_argument("--summary-output", help="Optional safe validation summary JSON path.")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    try:
        result = validate_config_file(Path(args.config).expanduser(), allow_real_rtsp=args.allow_real_rtsp)
        safe_summary = result.to_safe_dict()
        if args.summary_output:
            summary_output = Path(args.summary_output).expanduser()
            if summary_output.suffix.lower() != ".json":
                raise Tutym2ConfigValidationError("summary-output must be a .json file")
            summary_output.parent.mkdir(parents=True, exist_ok=True)
            summary_output.write_text(json.dumps(safe_summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(safe_summary, ensure_ascii=False, indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, Tutym2ConfigValidationError) as error:
        parser.exit(status=2, message=f"T.UTYM#2 config validation failed: {error}\n")
    return 0


def validate_config_file(path: Path, *, allow_real_rtsp: bool = False) -> ConfigValidationResult:
    if path.suffix.lower() != ".json":
        raise Tutym2ConfigValidationError(f"Config must be a .json file, got: {path.name}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return validate_config(payload, allow_real_rtsp=allow_real_rtsp)


def validate_config(payload: Mapping[str, Any], *, allow_real_rtsp: bool = False) -> ConfigValidationResult:
    _require_equal(payload.get("utym_id"), EXPECTED_UTYM_ID, "utym_id")
    _require_equal(payload.get("camera_id"), EXPECTED_CAMERA_ID, "camera_id")
    _require_equal(payload.get("source_type"), EXPECTED_SOURCE_TYPE, "source_type")

    resolution = _require_mapping(payload.get("resolution"), "resolution")
    _require_equal(resolution.get("width"), EXPECTED_WIDTH, "resolution.width")
    _require_equal(resolution.get("height"), EXPECTED_HEIGHT, "resolution.height")

    stream_url = _require_non_empty_string(payload.get("stream_url"), "stream_url")
    stream_url_mode = _classify_stream_url(stream_url, allow_real_rtsp=allow_real_rtsp)

    tables = _require_list(payload.get("tables"), "tables")
    if len(tables) != EXPECTED_TABLE_COUNT:
        raise Tutym2ConfigValidationError(f"tables must contain {EXPECTED_TABLE_COUNT} records")
    _validate_tables(tables)

    return ConfigValidationResult(
        utym_id=EXPECTED_UTYM_ID,
        camera_id=EXPECTED_CAMERA_ID,
        source_type=EXPECTED_SOURCE_TYPE,
        width=EXPECTED_WIDTH,
        height=EXPECTED_HEIGHT,
        table_count=len(tables),
        stream_url_mode=stream_url_mode,
    )


def _classify_stream_url(stream_url: str, *, allow_real_rtsp: bool) -> str:
    if stream_url == LOCAL_ONLY_STREAM_PLACEHOLDER:
        return "local_only_placeholder"
    if stream_url == RTSP_TEMPLATE_PATTERN:
        return "rtsp_template_placeholder"
    if RTSP_URL_PATTERN.match(stream_url):
        if not allow_real_rtsp:
            raise Tutym2ConfigValidationError(
                "Real RTSP URL detected. Use --allow-real-rtsp only for local-only field configs; "
                "never commit real RTSP URLs."
            )
        return "real_rtsp_local_only"
    raise Tutym2ConfigValidationError("stream_url must be a known placeholder or RTSP URL")


def _validate_tables(tables: list[Any]) -> None:
    seen_ids: set[str] = set()
    for index, item in enumerate(tables, start=1):
        table = _require_mapping(item, f"tables[{index}]")
        table_id = _require_non_empty_string(table.get("table_id"), f"tables[{index}].table_id")
        if table_id in seen_ids:
            raise Tutym2ConfigValidationError(f"Duplicate table_id: {table_id}")
        seen_ids.add(table_id)
        if table.get("capacity") != EXPECTED_CAPACITY:
            raise Tutym2ConfigValidationError(f"{table_id}.capacity must be {EXPECTED_CAPACITY}")
        polygon = _require_list(table.get("polygon"), f"{table_id}.polygon")
        if len(polygon) < 3:
            raise Tutym2ConfigValidationError(f"{table_id}.polygon must contain at least 3 points")
        for point_index, point in enumerate(polygon, start=1):
            _validate_point(point, table_id, point_index)


def _validate_point(point: Any, table_id: str, point_index: int) -> None:
    if not isinstance(point, list) or len(point) != 2:
        raise Tutym2ConfigValidationError(f"{table_id}.polygon[{point_index}] must be [x, y]")
    x, y = point
    for coordinate_name, coordinate, maximum in (("x", x, EXPECTED_WIDTH), ("y", y, EXPECTED_HEIGHT)):
        if not isinstance(coordinate, (int, float)) or isinstance(coordinate, bool):
            raise Tutym2ConfigValidationError(f"{table_id}.polygon[{point_index}].{coordinate_name} must be a number")
        if coordinate < 0 or coordinate > maximum:
            raise Tutym2ConfigValidationError(
                f"{table_id}.polygon[{point_index}].{coordinate_name} must be between 0 and {maximum}"
            )


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise Tutym2ConfigValidationError(f"{field_name} must be an object")
    return value


def _require_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise Tutym2ConfigValidationError(f"{field_name} must be a list")
    return value


def _require_equal(value: Any, expected: Any, field_name: str) -> None:
    if value != expected:
        raise Tutym2ConfigValidationError(f"{field_name} must be {expected!r}, got {value!r}")


def _require_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Tutym2ConfigValidationError(f"{field_name} must be a non-empty string")
    return value


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
