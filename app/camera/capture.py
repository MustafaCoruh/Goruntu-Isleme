"""Utilities for reading frames from camera-like file sources."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np


SUPPORTED_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png"})


class ImageFileSourceError(RuntimeError):
    """Raised when an image file source cannot be opened or read."""


class ImageFileSource:
    """Read a still image as a single frame using an interface like video sources.

    The returned frame is an OpenCV image array in BGR channel order, matching
    frames read from ``cv2.VideoCapture``.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._frame: np.ndarray[Any, Any] | None = None
        self._has_been_read = False

    def open(self) -> None:
        """Open and decode the configured image file.

        Raises
        ------
        FileNotFoundError
            If the configured path does not exist.
        ImageFileSourceError
            If the extension is unsupported or OpenCV cannot decode the image.
        """

        if self.path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            supported = ", ".join(sorted(SUPPORTED_IMAGE_EXTENSIONS))
            raise ImageFileSourceError(
                f"Unsupported image file extension for {self.path}. "
                f"Supported extensions: {supported}"
            )

        if not self.path.exists():
            raise FileNotFoundError(f"Image file does not exist: {self.path}")

        frame = cv2.imread(str(self.path), cv2.IMREAD_COLOR)
        if frame is None:
            raise ImageFileSourceError(f"Could not read image file: {self.path}")

        self._frame = frame
        self._has_been_read = False

    @property
    def is_opened(self) -> bool:
        """Return whether the image has been successfully opened."""

        return self._frame is not None

    def read_frame(self) -> np.ndarray[Any, Any]:
        """Return the image as a single frame.

        Raises
        ------
        ImageFileSourceError
            If the source is not open or the single image frame was already read.
        """

        if self._frame is None:
            raise ImageFileSourceError(f"Image file is not open: {self.path}")

        if self._has_been_read:
            raise ImageFileSourceError(
                f"No more frames available from image file: {self.path}"
            )

        self._has_been_read = True
        return self._frame.copy()

    def close(self) -> None:
        """Release the decoded image frame."""

        self._frame = None
        self._has_been_read = False

    def __enter__(self) -> "ImageFileSource":
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
