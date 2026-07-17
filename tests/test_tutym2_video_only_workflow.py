from pathlib import Path

from app.field_demo import SUPPORTED_SOURCE_EXTENSIONS
from app.table_accuracy_report import ALLOWED_TEST_TYPES


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "app" / "main.py"


def test_tutym2_local_demo_is_video_only():
    assert SUPPORTED_SOURCE_EXTENSIONS == {".avi", ".m4v", ".mkv", ".mov", ".mp4"}
    assert ".jpg" not in SUPPORTED_SOURCE_EXTENSIONS
    assert ".png" not in SUPPORTED_SOURCE_EXTENSIONS


def test_main_demo_has_no_still_image_input_path():
    text = MAIN.read_text(encoding="utf-8")

    assert "Path to a local video source" in text
    assert "SUPPORTED_IMAGE_EXTENSIONS" not in text
    assert "ImageFileSource" not in text
    assert "Supported image extensions" not in text


def test_table_accuracy_test_types_are_video_or_live_only():
    assert ALLOWED_TEST_TYPES == {"local_video", "rtsp_live"}
    assert "local_photo" not in ALLOWED_TEST_TYPES


def test_operator_docs_do_not_advertise_photo_inputs():
    docs = [
        ROOT / "docs" / "deployment" / "windows_field_demo.md",
        ROOT / "docs" / "deployment" / "windows_quick_start_for_operator.md",
        ROOT / "docs" / "validation" / "tutym2_local_field_validation_template.md",
        ROOT / "docs" / "validation" / "tutym2_table_accuracy_report_format.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in docs).lower()

    assert "local_photo" not in combined
    assert "fotoğraf/video" not in combined
    assert "fotoğraf testi" not in combined
    assert "input\\photos" not in combined
