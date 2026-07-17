from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_active_product_has_no_legacy_release_stage_labels():
    active_files = [
        ROOT / "README.md",
        *sorted((ROOT / "app").rglob("*.py")),
        *sorted((ROOT / "app" / "ui" / "static").glob("*.html")),
        *sorted((ROOT / "app" / "ui" / "static").glob("*.js")),
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in active_files)

    for stage in (2, 3, 4):
        assert f"R{stage}" not in combined


def test_main_navigation_contains_only_product_screens():
    index = (ROOT / "app" / "ui" / "static" / "index.html").read_text(encoding="utf-8")
    debug = (ROOT / "app" / "ui" / "static" / "debug.html").read_text(encoding="utf-8")
    combined = index + debug

    assert "calibration.html" in combined
    assert "debug.html" in index
    assert "Saha Kabul" not in combined


def test_removed_non_occupancy_features_do_not_return():
    removed_paths = [
        ROOT / "app" / "database" / "importers.py",
        ROOT / "app" / "api" / "routes_import.py",
        ROOT / "app" / "api" / "routes_reports.py",
        ROOT / "app" / "api" / "routes_sessions.py",
        ROOT / "app" / "ui" / "static" / "session_assignment.html",
    ]

    assert all(not path.exists() for path in removed_paths)
