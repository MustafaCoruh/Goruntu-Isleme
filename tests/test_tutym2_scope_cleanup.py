from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_removed_acceptance_workflow_files_do_not_return():
    removed_paths = [
        "app/r3_demo_smoke.py",
        "app/r4_acceptance.py",
        "app/field_handoff_summary.py",
        "app/tutym2_project_status.py",
        "app/ui/static/tutym2_r3_demo_launcher.html",
        "app/ui/static/tutym2_r3_presentation.html",
        "app/ui/static/tutym2_r4_acceptance_center.html",
    ]

    assert all(not (ROOT / path).exists() for path in removed_paths)


def test_main_navigation_contains_only_product_screens():
    index = (ROOT / "app" / "ui" / "static" / "index.html").read_text(encoding="utf-8")
    debug = (ROOT / "app" / "ui" / "static" / "debug.html").read_text(encoding="utf-8")
    combined = index + debug

    assert "calibration.html" in combined
    assert "debug.html" in index
    assert "R3" not in combined
    assert "R4" not in combined
    assert "Saha Kabul" not in combined
