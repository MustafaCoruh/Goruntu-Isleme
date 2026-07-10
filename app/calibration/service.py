"""Services for loading camera calibration configuration files."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from app.calibration.models import (
    CameraConfig,
    Point,
    Resolution,
    TablePolygon,
    UtymConfig,
)


class CameraConfigError(ValueError):
    """Raised when a camera calibration config cannot be loaded or validated."""


def load_camera_config(path: str) -> UtymConfig | CameraConfig:
    """Load, validate, and convert a camera calibration JSON file.

    Parameters
    ----------
    path:
        Path to a JSON file containing top-level ``utym_id`` and ``cameras`` fields.
        Legacy single-camera files with ``camera_id``, ``resolution`` and ``tables``
        are also accepted for backward compatibility.

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


def parse_camera_config(raw_config: Mapping[str, Any]) -> UtymConfig | CameraConfig:
    """Validate and convert a raw calibration config mapping to models.

    The preferred shape is a top-level UTYM config with a ``cameras`` list.
    Legacy single-camera configs are still parsed as ``CameraConfig`` so older
    callers and saved calibration files keep working during migration.
    """

    if not isinstance(raw_config, Mapping):
        raise CameraConfigError("Camera config root must be a JSON object")

    if "cameras" not in raw_config:
        return _parse_legacy_camera_config(raw_config)

    utym_id = _require_non_empty_string(raw_config, "utym_id")
    raw_cameras = _require_sequence(raw_config, "cameras")
    if not raw_cameras:
        raise CameraConfigError("Field 'cameras' must contain at least one camera")

    cameras: list[CameraConfig] = []
    for index, raw_camera in enumerate(raw_cameras):
        cameras.append(_parse_camera(raw_camera, f"cameras[{index}]", utym_id))

    return UtymConfig(utym_id=utym_id, cameras=tuple(cameras))


def save_camera_config(
    path: str, raw_config: Mapping[str, Any]
) -> UtymConfig | CameraConfig:
    """Validate a calibration config and persist it as pretty-printed JSON."""

    config = parse_camera_config(raw_config)
    config_path = Path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(camera_config_to_dict(config), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return config


def camera_config_to_dict(config: UtymConfig | CameraConfig) -> dict[str, Any]:
    """Serialize a calibration config model to JSON-compatible data."""

    if isinstance(config, UtymConfig):
        return {
            "utym_id": config.utym_id,
            "cameras": [_camera_to_dict(camera) for camera in config.cameras],
        }

    data = _camera_to_dict(config)
    if config.utym_id is not None:
        return {"utym_id": config.utym_id, **data}
    return data


def _camera_to_dict(camera: CameraConfig) -> dict[str, Any]:
    data: dict[str, Any] = {
        "camera_id": camera.camera_id,
        "source_type": camera.source_type,
        "resolution": {
            "width": camera.resolution.width,
            "height": camera.resolution.height,
        },
        "tables": [
            {
                "table_id": table.table_id,
                "name": table.name,
                "capacity": table.capacity,
                "polygon": [[point.x, point.y] for point in table.polygon],
            }
            for table in camera.tables
        ],
    }
    if camera.stream_url is not None:
        data["stream_url"] = camera.stream_url
    return data


def _parse_legacy_camera_config(raw_config: Mapping[str, Any]) -> CameraConfig:
    utym_id = _require_non_empty_string(raw_config, "utym_id")
    return _parse_camera(raw_config, "", utym_id)


def _parse_camera(raw_camera: Any, field_prefix: str, utym_id: str) -> CameraConfig:
    if not isinstance(raw_camera, Mapping):
        raise CameraConfigError(f"Field '{field_prefix or 'camera'}' must be an object")

    def field(name: str) -> str:
        return f"{field_prefix}.{name}" if field_prefix else name

    source_type = str(raw_camera.get("source_type", "rtsp"))
    stream_url = raw_camera.get("stream_url")
    if stream_url is not None and not isinstance(stream_url, str):
        raise CameraConfigError(f"Field '{field('stream_url')}' must be a string")

    return CameraConfig(
        utym_id=utym_id,
        camera_id=_require_non_empty_string(raw_camera, field("camera_id")),
        source_type=source_type,
        stream_url=(
            stream_url.strip()
            if isinstance(stream_url, str) and stream_url.strip()
            else None
        ),
        resolution=_parse_resolution(
            _require_mapping(raw_camera, field("resolution")), field("resolution")
        ),
        tables=_parse_tables(
            _require_sequence(raw_camera, field("tables")), field("tables")
        ),
    )


def _parse_resolution(
    raw_resolution: Mapping[str, Any], field_prefix: str = "resolution"
) -> Resolution:
    width = _require_positive_int(raw_resolution, f"{field_prefix}.width")
    height = _require_positive_int(raw_resolution, f"{field_prefix}.height")
    return Resolution(width=width, height=height)


def _parse_tables(
    raw_tables: Sequence[Any], field_name: str = "tables"
) -> tuple[TablePolygon, ...]:
    if isinstance(raw_tables, (str, bytes)):
        raise CameraConfigError(f"Field '{field_name}' must be a list of table objects")
    if not raw_tables:
        raise CameraConfigError(f"Field '{field_name}' must contain at least one table")

    tables: list[TablePolygon] = []
    for index, raw_table in enumerate(raw_tables):
        field_prefix = f"{field_name}[{index}]"
        if not isinstance(raw_table, Mapping):
            raise CameraConfigError(f"Field '{field_prefix}' must be an object")

        tables.append(
            TablePolygon(
                table_id=_require_non_empty_string(
                    raw_table, f"{field_prefix}.table_id"
                ),
                name=_require_non_empty_string(raw_table, f"{field_prefix}.name"),
                capacity=_require_positive_int(raw_table, f"{field_prefix}.capacity"),
                polygon=_parse_polygon(
                    _require_sequence(raw_table, f"{field_prefix}.polygon"),
                    field_prefix,
                ),
            )
        )

    return tuple(tables)


def _parse_polygon(raw_polygon: Sequence[Any], field_prefix: str) -> tuple[Point, ...]:
    if isinstance(raw_polygon, (str, bytes)):
        raise CameraConfigError(
            f"Field '{field_prefix}.polygon' must be a list of points"
        )
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
            raise CameraConfigError(
                f"Field '{point_field}' coordinates must be integers"
            )
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
