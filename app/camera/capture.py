"""Utilities for reading frames from video files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


DEFAULT_SAMPLE_VIDEO_PATH = Path("sample_data/utym_001/videos/sample_session.mp4")


class VideoFileSourceError(RuntimeError):
    """Raised when a video file source cannot be opened or read."""


@dataclass(frozen=True)
class VideoMetadata:
    """Basic metadata reported by OpenCV for a video source."""

    fps: float
    width: int
    height: int
    frame_count: int


class VideoFileSource:
    """Read frames and metadata from a video file using OpenCV.

    Parameters
    ----------
    path:
        Path to the video file. Defaults to the sample session path documented
        for the project.
    """

    def __init__(self, path: str | Path = DEFAULT_SAMPLE_VIDEO_PATH) -> None:
        self.path = Path(path)
        self._capture: cv2.VideoCapture | None = None

    def open(self) -> None:
        """Open the configured video file.

        Raises
        ------
        FileNotFoundError
            If the configured path does not exist.
        VideoFileSourceError
            If OpenCV cannot open the file as a video stream.
        """

        if not self.path.exists():
            raise FileNotFoundError(f"Video file does not exist: {self.path}")

        self.close()
        self._capture = cv2.VideoCapture(str(self.path))
        if not self._capture.isOpened():
            self.close()
            raise VideoFileSourceError(f"Could not open video file: {self.path}")

    @property
    def is_opened(self) -> bool:
        """Return whether the underlying OpenCV capture is currently open."""

        return self._capture is not None and self._capture.isOpened()

    @property
    def metadata(self) -> VideoMetadata:
        """Return FPS, dimensions, and frame count for the opened video."""

        capture = self._require_open_capture()
        return VideoMetadata(
            fps=float(capture.get(cv2.CAP_PROP_FPS)),
            width=int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
            height=int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            frame_count=int(capture.get(cv2.CAP_PROP_FRAME_COUNT)),
        )

    def read_frame(self) -> np.ndarray[Any, Any]:
        """Read the next video frame.

        Raises
        ------
        VideoFileSourceError
            If the source is not open or OpenCV fails to read a frame.
        """

        capture = self._require_open_capture()
        success, frame = capture.read()
        if not success or frame is None:
            raise VideoFileSourceError(
                f"Could not read frame from video file: {self.path}"
            )
        return frame

    def close(self) -> None:
        """Release the underlying OpenCV video capture if it exists."""

        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def _require_open_capture(self) -> cv2.VideoCapture:
        if not self.is_opened or self._capture is None:
            raise VideoFileSourceError(f"Video file is not open: {self.path}")
        return self._capture

    def __enter__(self) -> "VideoFileSource":
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
