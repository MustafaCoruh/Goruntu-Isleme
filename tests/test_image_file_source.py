from pathlib import Path

import pytest

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

from app.camera.capture import ImageFileSource, ImageFileSourceError


def test_image_file_source_reads_png_as_single_frame(tmp_path: Path) -> None:
    image_path = tmp_path / "frame.png"
    frame = np.zeros((3, 4, 3), dtype=np.uint8)
    frame[:, :] = [10, 20, 30]
    assert cv2.imwrite(str(image_path), frame)

    with ImageFileSource(image_path) as source:
        assert source.is_opened
        read_frame = source.read_frame()
        assert read_frame.shape == frame.shape
        np.testing.assert_array_equal(read_frame, frame)

        with pytest.raises(ImageFileSourceError, match="No more frames"):
            source.read_frame()

    assert not source.is_opened


def test_image_file_source_rejects_unsupported_extension(tmp_path: Path) -> None:
    image_path = tmp_path / "frame.bmp"
    image_path.write_bytes(b"not used")

    source = ImageFileSource(image_path)

    with pytest.raises(ImageFileSourceError, match="Unsupported image file extension"):
        source.open()


def test_image_file_source_reports_unreadable_image(tmp_path: Path) -> None:
    image_path = tmp_path / "broken.jpg"
    image_path.write_bytes(b"not a real image")

    source = ImageFileSource(image_path)

    with pytest.raises(ImageFileSourceError, match="Could not read image file"):
        source.open()
