"""Table listing routes for the FastAPI application."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.calibration.service import (
    CameraConfigError,
    camera_config_to_dict,
    save_camera_config,
)
from app.database.models import Table

router = APIRouter(tags=["tables"])


def _parse_polygon(polygon_json: str) -> Any:
    """Decode a stored table polygon, preserving invalid legacy values as text."""

    try:
        return json.loads(polygon_json)
    except json.JSONDecodeError:
        return polygon_json


@router.get("/tables")
def list_tables(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Return configured tables ordered by their primary key."""

    tables = db.execute(select(Table).order_by(Table.id)).scalars().all()
    return [
        {
            "id": table.id,
            "utym_id": table.utym_id,
            "camera_id": table.camera_id,
            "name": table.name,
            "capacity": table.capacity,
            "polygon": _parse_polygon(table.polygon_json),
            "created_at": table.created_at.isoformat(),
        }
        for table in tables
    ]


def _default_calibration_config_path() -> Path:
    return Path(os.getenv("FTMC_CALIBRATION_CONFIG_PATH", "camera-config.json"))


def _calibration_config_dir() -> Path:
    return Path(os.getenv("FTMC_CALIBRATION_CONFIG_DIR", "configs"))


def _safe_config_filename_part(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return sanitized.strip(".-") or "unknown"


def _calibration_save_path(config: dict[str, Any]) -> Path:
    utym_id = _safe_config_filename_part(str(config.get("utym_id", "unknown")))
    camera_id = _safe_config_filename_part(str(config.get("camera_id", "unknown")))
    return _calibration_config_dir() / f"{utym_id}-{camera_id}.json"


@router.post("/calibration/config", status_code=status.HTTP_201_CREATED)
def save_calibration_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate and save a calibration config JSON payload."""

    config_path = _default_calibration_config_path()
    try:
        saved_config = save_camera_config(str(config_path), config)
    except CameraConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    return {
        "path": str(config_path),
        "config": camera_config_to_dict(saved_config),
    }


@router.post("/calibration/save", status_code=status.HTTP_201_CREATED)
def save_calibration_tables_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate and save a table calibration config under the configs directory."""

    config_path = _calibration_save_path(config)
    try:
        saved_config = save_camera_config(str(config_path), config)
    except CameraConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    return {
        "path": str(config_path),
        "config": camera_config_to_dict(saved_config),
    }
