"""Camera source implementations for live streams."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import cv2
import numpy as np


class RtspCameraSourceError(RuntimeError):
    """Raised when an RTSP camera source cannot connect or read frames."""


class RtspCameraSource:
    """Read frames from an RTSP camera stream through OpenCV.

    The stream URL is supplied through configuration rather than being embedded
    in application code. A minimal expected configuration looks like::

        {
            "camera_id": "CAM-01",
            "source_type": "rtsp",
            "stream_url": "rtsp://username:password@camera-ip/stream",
        }

    The class reports connection/read failures with ``RtspCameraSourceError``
    and keeps a dedicated ``reconnect`` method as the extension point for more
    advanced retry/backoff behavior.
    """

    def __init__(self, config: Mapping[str, Any]) -> None:
        self.camera_id = str(config.get("camera_id", "unknown"))
        self.source_type = str(config.get("source_type", "rtsp"))
        stream_url = config.get("stream_url")

        if self.source_type != "rtsp":
            raise RtspCameraSourceError(
                f"Unsupported source_type for {self.camera_id}: {self.source_type}"
            )

        if not isinstance(stream_url, str) or not stream_url.strip():
            raise RtspCameraSourceError(
                f"Missing RTSP stream_url in config for camera {self.camera_id}"
            )

        self.stream_url = stream_url
        self._capture: cv2.VideoCapture | None = None
        self.last_error: str | None = None

    def open(self) -> None:
        """Connect to the configured RTSP stream.

        Raises
        ------
        RtspCameraSourceError
            If OpenCV cannot open the RTSP stream.
        """

        self.close()
        capture = cv2.VideoCapture(self.stream_url)
        if not capture.isOpened():
            capture.release()
            self.last_error = f"Could not connect to RTSP stream for {self.camera_id}"
            raise RtspCameraSourceError(self.last_error)

        self._capture = capture
        self.last_error = None

    @property
    def is_opened(self) -> bool:
        """Return whether the underlying OpenCV capture is currently open."""

        return self._capture is not None and self._capture.isOpened()

    def read_frame(self) -> np.ndarray[Any, Any]:
        """Read the next frame from the RTSP stream.

        Raises
        ------
        RtspCameraSourceError
            If the source is not connected or OpenCV cannot read the next frame.
        """

        if not self.is_opened or self._capture is None:
            self.last_error = f"RTSP stream is not connected for {self.camera_id}"
            raise RtspCameraSourceError(self.last_error)

        ok, frame = self._capture.read()
        if not ok or frame is None:
            self.last_error = f"Lost RTSP frame stream for {self.camera_id}"
            raise RtspCameraSourceError(self.last_error)

        self.last_error = None
        return frame

    def reconnect(self) -> None:
        """Reconnect to the RTSP stream.

        This method is intentionally small so retry policies, exponential
        backoff, or maximum retry counts can be layered on top without changing
        the frame-reading API.
        """

        self.open()

    def close(self) -> None:
        """Release the OpenCV capture if it is open."""

        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def __enter__(self) -> "RtspCameraSource":
        self.open()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
