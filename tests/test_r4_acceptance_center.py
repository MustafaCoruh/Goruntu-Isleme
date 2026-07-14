from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
R4_CENTER = ROOT / "app" / "ui" / "static" / "tutym2_r4_acceptance_center.html"
INDEX = ROOT / "app" / "ui" / "static" / "index.html"
DEBUG = ROOT / "app" / "ui" / "static" / "debug.html"
RELEASE_CHECKLIST = ROOT / "docs" / "deployment" / "tutym2_release_readiness_checklist.md"


def test_r4_acceptance_center_has_terminal_free_acceptance_flow():
    html = R4_CENTER.read_text(encoding="utf-8")

    assert "T.UTYM#2 R4 Saha Kabul Merkezi" in html
    assert "Terminalsiz JSON Hızlı Kontrol" in html
    assert "dashboard_state.json seç" in html
    assert "field_handoff_summary.json seç" in html
    assert "R4 Bitince Söylenecek Kapanış" in html


def test_r4_acceptance_center_checks_safety_and_14_tables():
    html = R4_CENTER.read_text(encoding="utf-8")

    assert "payload.tables.length !== 14" in html
    assert "contains_rtsp_url" in html
    assert "contains_credentials" in html
    assert "contains_image_or_video" in html
    assert "contains_full_local_path" in html
    assert "hasUnsafeText" in html


def test_r4_acceptance_center_is_linked_from_static_pages_and_docs():
    for path in (INDEX, DEBUG, RELEASE_CHECKLIST):
        assert "tutym2_r4_acceptance_center.html" in path.read_text(encoding="utf-8")
