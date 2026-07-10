import json
from pathlib import Path

import pytest

from app.calibration.models import CameraConfig, Point, Resolution, TablePolygon
from app.calibration.service import CameraConfigError, load_camera_config


def test_load_camera_config_converts_json_to_models(tmp_path: Path) -> None:
    config_path = tmp_path / "camera.json"
    config_path.write_text(
        json.dumps(
            {
                "utym_id": "UTYM-001",
                "camera_id": "CAM-001",
                "resolution": {"width": 1920, "height": 1080},
                "tables": [
                    {
                        "table_id": "T-001",
                        "name": "Masa 1",
                        "capacity": 4,
                        "polygon": [[100, 200], [300, 200], [320, 420]],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    config = load_camera_config(str(config_path))

    assert config == CameraConfig(
        utym_id="UTYM-001",
        camera_id="CAM-001",
        resolution=Resolution(width=1920, height=1080),
        tables=(
            TablePolygon(
                table_id="T-001",
                name="Masa 1",
                capacity=4,
                polygon=(Point(100, 200), Point(300, 200), Point(320, 420)),
            ),
        ),
    )


@pytest.mark.parametrize(
    ("config", "message"),
    [
        ({"camera_id": "CAM-001", "resolution": {}, "tables": []}, "utym_id"),
        (
            {
                "utym_id": "UTYM-001",
                "camera_id": "",
                "resolution": {"width": 1920, "height": 1080},
                "tables": [],
            },
            "camera_id.*non-empty string",
        ),
        (
            {
                "utym_id": "UTYM-001",
                "camera_id": "CAM-001",
                "resolution": {"width": 0, "height": 1080},
                "tables": [],
            },
            "resolution.width.*positive integer",
        ),
        (
            {
                "utym_id": "UTYM-001",
                "camera_id": "CAM-001",
                "resolution": {"width": 1920, "height": 1080},
                "tables": [],
            },
            "tables.*at least one table",
        ),
        (
            {
                "utym_id": "UTYM-001",
                "camera_id": "CAM-001",
                "resolution": {"width": 1920, "height": 1080},
                "tables": [
                    {
                        "table_id": "T-001",
                        "name": "Masa 1",
                        "capacity": 4,
                        "polygon": [[100, 200], [300, 200]],
                    }
                ],
            },
            "polygon.*at least 3 points",
        ),
        (
            {
                "utym_id": "UTYM-001",
                "camera_id": "CAM-001",
                "resolution": {"width": 1920, "height": 1080},
                "tables": [
                    {
                        "table_id": "T-001",
                        "name": "Masa 1",
                        "capacity": 4,
                        "polygon": [[100, 200], [300, "200"], [320, 420]],
                    }
                ],
            },
            "coordinates must be integers",
        ),
    ],
)
def test_load_camera_config_reports_invalid_fields(
    tmp_path: Path, config: dict[str, object], message: str
) -> None:
    config_path = tmp_path / "camera.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(CameraConfigError, match=message):
        load_camera_config(str(config_path))


def test_load_camera_config_reports_invalid_json(tmp_path: Path) -> None:
    config_path = tmp_path / "camera.json"
    config_path.write_text("{not valid", encoding="utf-8")

    with pytest.raises(CameraConfigError, match="Invalid JSON"):
        load_camera_config(str(config_path))


def test_save_camera_config_validates_and_writes_json(tmp_path: Path) -> None:
    from app.calibration.service import save_camera_config

    config_path = tmp_path / "saved" / "camera.json"
    saved = save_camera_config(
        str(config_path),
        {
            "utym_id": "UTYM-001",
            "camera_id": "CAM-001",
            "resolution": {"width": 640, "height": 480},
            "tables": [
                {
                    "table_id": "T-001",
                    "name": "Masa 1",
                    "capacity": 4,
                    "polygon": [[1, 2], [3, 4], [5, 6]],
                }
            ],
        },
    )

    assert saved.resolution.width == 640
    assert json.loads(config_path.read_text(encoding="utf-8"))["tables"][0]["name"] == "Masa 1"
