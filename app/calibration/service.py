"""Services for loading camera calibration configuration files."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from app.calibration.models import CameraConfig, Point, Resolution, TablePolygon


class CameraConfigError(ValueError):
    """Raised when a camera calibration config cannot be loaded or validated."""


def load_camera_config(path: str) -> CameraConfig:
    """Load, validate, and convert a camera calibration JSON file.

    Parameters
    ----------
    path:
        Path to a JSON file containing ``utym_id``, ``camera_id``,
        ``resolution`` and ``tables`` fields.

    Raises
    ------
    FileNotFoundError
        If the config file does not exist.
    CameraConfigError
        If JSON parsing fails or a required field has an invalid shape/type.
    """

    config_path = Path(path)
    try:
        raw_config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CameraConfigError(
            f"Invalid JSON in camera config {config_path}: {exc.msg}"
        ) from exc

    return parse_camera_config(raw_config)


def parse_camera_config(raw_config: Mapping[str, Any]) -> CameraConfig:
    """Validate and convert a raw calibration config mapping to models."""

    if not isinstance(raw_config, Mapping):
        raise CameraConfigError("Camera config root must be a JSON object")

    return CameraConfig(
        utym_id=_require_non_empty_string(raw_config, "utym_id"),
        camera_id=_require_non_empty_string(raw_config, "camera_id"),
        resolution=_parse_resolution(_require_mapping(raw_config, "resolution")),
        tables=_parse_tables(_require_sequence(raw_config, "tables")),
    )


def save_camera_config(path: str, raw_config: Mapping[str, Any]) -> CameraConfig:
    """Validate a calibration config and persist it as pretty-printed JSON."""

    config = parse_camera_config(raw_config)
    config_path = Path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(camera_config_to_dict(config), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return config


def camera_config_to_dict(config: CameraConfig) -> dict[str, Any]:
    """Serialize a camera calibration config model to JSON-compatible data."""

    return {
        "utym_id": config.utym_id,
        "camera_id": config.camera_id,
        "resolution": {
            "width": config.resolution.width,
            "height": config.resolution.height,
        },
        "tables": [
            {
                "table_id": table.table_id,
                "name": table.name,
                "capacity": table.capacity,
                "polygon": [[point.x, point.y] for point in table.polygon],
            }
            for table in config.tables
        ],
    }


def _parse_resolution(raw_resolution: Mapping[str, Any]) -> Resolution:
    width = _require_positive_int(raw_resolution, "resolution.width")
    height = _require_positive_int(raw_resolution, "resolution.height")
    return Resolution(width=width, height=height)


def _parse_tables(raw_tables: Sequence[Any]) -> tuple[TablePolygon, ...]:
    if isinstance(raw_tables, (str, bytes)):
        raise CameraConfigError("Field 'tables' must be a list of table objects")
    if not raw_tables:
        raise CameraConfigError("Field 'tables' must contain at least one table")

    tables: list[TablePolygon] = []
    table_ids: set[str] = set()
    for index, raw_table in enumerate(raw_tables):
        field_prefix = f"tables[{index}]"
        if not isinstance(raw_table, Mapping):
            raise CameraConfigError(f"Field '{field_prefix}' must be an object")

        table_id = _require_non_empty_string(raw_table, f"{field_prefix}.table_id")
        if table_id in table_ids:
            raise CameraConfigError(f"Field '{field_prefix}.table_id' must be unique")
        table_ids.add(table_id)

        tables.append(
            TablePolygon(
                table_id=table_id,
                name=_require_non_empty_string(raw_table, f"{field_prefix}.name"),
                capacity=_require_positive_int(raw_table, f"{field_prefix}.capacity"),
                polygon=_parse_polygon(
                    _require_sequence(raw_table, f"{field_prefix}.polygon"), field_prefix
                ),
            )
        )

    return tuple(tables)


def _parse_polygon(raw_polygon: Sequence[Any], field_prefix: str) -> tuple[Point, ...]:
    if isinstance(raw_polygon, (str, bytes)):
        raise CameraConfigError(f"Field '{field_prefix}.polygon' must be a list of points")
    if len(raw_polygon) < 3:
        raise CameraConfigError(
            f"Field '{field_prefix}.polygon' must contain at least 3 points"
        )

    points: list[Point] = []
    for index, raw_point in enumerate(raw_polygon):
        point_field = f"{field_prefix}.polygon[{index}]"
        if (
            not isinstance(raw_point, Sequence)
            or isinstance(raw_point, (str, bytes))
            or len(raw_point) != 2
        ):
            raise CameraConfigError(
                f"Field '{point_field}' must be a two-item [x, y] coordinate"
            )

        x, y = raw_point
        if not _is_int(x) or not _is_int(y):
            raise CameraConfigError(f"Field '{point_field}' coordinates must be integers")
        if x < 0 or y < 0:
            raise CameraConfigError(
                f"Field '{point_field}' coordinates must be greater than or equal to 0"
            )
        points.append(Point(x=x, y=y))

    return tuple(points)


def _require_mapping(data: Mapping[str, Any], field: str) -> Mapping[str, Any]:
    value = _require_field(data, field)
    if not isinstance(value, Mapping):
        raise CameraConfigError(f"Field '{field}' must be an object")
    return value


def _require_sequence(data: Mapping[str, Any], field: str) -> Sequence[Any]:
    value = _require_field(data, field)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise CameraConfigError(f"Field '{field}' must be a list")
    return value


def _require_non_empty_string(data: Mapping[str, Any], field: str) -> str:
    value = _require_field(data, field)
    if not isinstance(value, str) or not value.strip():
        raise CameraConfigError(f"Field '{field}' must be a non-empty string")
    return value


def _require_positive_int(data: Mapping[str, Any], field: str) -> int:
    value = _require_field(data, field)
    if not _is_int(value) or value <= 0:
        raise CameraConfigError(f"Field '{field}' must be a positive integer")
    return value


def _require_field(data: Mapping[str, Any], field: str) -> Any:
    key = field.rsplit(".", maxsplit=1)[-1]
    if key not in data:
        raise CameraConfigError(f"Missing required field '{field}'")
    return data[key]


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
