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
    """Calibration/source configuration for one UTYM camera."""

    camera_id: str
    resolution: Resolution
    tables: tuple[TablePolygon, ...]
    source_type: str = "rtsp"
    stream_url: str | None = None
    utym_id: str | None = None


@dataclass(frozen=True)
class UtymConfig:
    """Top-level configuration for one UTYM containing multiple cameras."""

    utym_id: str
    cameras: tuple[CameraConfig, ...]
