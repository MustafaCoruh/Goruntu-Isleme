"""Data models for camera calibration configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    """A two-dimensional pixel coordinate in an image."""

    x: int
    y: int


@dataclass(frozen=True)
class Resolution:
    """Camera image dimensions in pixels."""

    width: int
    height: int


@dataclass(frozen=True)
class TablePolygon:
    """A calibrated dining table area described by a polygon."""

    table_id: str
    name: str
    capacity: int
    polygon: tuple[Point, ...]


@dataclass(frozen=True)
class CameraConfig:
    """Calibration configuration for one UTYM camera."""

    utym_id: str
    camera_id: str
    resolution: Resolution
    tables: tuple[TablePolygon, ...]
