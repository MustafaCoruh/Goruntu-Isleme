import pytest

np = pytest.importorskip("numpy")

from app.camera.sources import RtspCameraSource, RtspCameraSourceError


class FakeVideoCapture:
    instances = []

    def __init__(self, url: str) -> None:
        self.url = url
        self.opened = not url.endswith("/closed")
        self.released = False
        self.frames = [(True, np.zeros((2, 3, 3), dtype=np.uint8))]
        FakeVideoCapture.instances.append(self)

    def isOpened(self) -> bool:
        return self.opened and not self.released

    def read(self):
        if self.frames:
            return self.frames.pop(0)
        return False, None

    def release(self) -> None:
        self.released = True
        self.opened = False


def test_rtsp_camera_source_uses_configured_stream_url(monkeypatch) -> None:
    FakeVideoCapture.instances = []
    monkeypatch.setattr("app.camera.sources.cv2.VideoCapture", FakeVideoCapture)
    config = {
        "camera_id": "CAM-01",
        "source_type": "rtsp",
        "stream_url": "rtsp://username:password@camera-ip/stream",
    }

    with RtspCameraSource(config) as source:
        assert source.is_opened
        assert FakeVideoCapture.instances[-1].url == config["stream_url"]
        frame = source.read_frame()
        assert frame.shape == (2, 3, 3)
        assert source.last_error is None

    assert not source.is_opened


def test_rtsp_camera_source_reports_connection_failure(monkeypatch) -> None:
    FakeVideoCapture.instances = []
    monkeypatch.setattr("app.camera.sources.cv2.VideoCapture", FakeVideoCapture)
    source = RtspCameraSource(
        {
            "camera_id": "CAM-02",
            "source_type": "rtsp",
            "stream_url": "rtsp://camera-ip/closed",
        }
    )

    with pytest.raises(RtspCameraSourceError, match="Could not connect"):
        source.open()

    assert source.last_error == "Could not connect to RTSP stream for CAM-02"
    assert FakeVideoCapture.instances[-1].released


def test_rtsp_camera_source_reports_read_failure(monkeypatch) -> None:
    FakeVideoCapture.instances = []
    monkeypatch.setattr("app.camera.sources.cv2.VideoCapture", FakeVideoCapture)
    source = RtspCameraSource(
        {
            "camera_id": "CAM-03",
            "source_type": "rtsp",
            "stream_url": "rtsp://camera-ip/stream",
        }
    )
    source.open()
    FakeVideoCapture.instances[-1].frames = [(False, None)]

    with pytest.raises(RtspCameraSourceError, match="Lost RTSP frame stream"):
        source.read_frame()

    assert source.last_error == "Lost RTSP frame stream for CAM-03"
    source.close()


def test_rtsp_camera_source_validates_config() -> None:
    with pytest.raises(RtspCameraSourceError, match="Missing RTSP stream_url"):
        RtspCameraSource({"camera_id": "CAM-04", "source_type": "rtsp"})
