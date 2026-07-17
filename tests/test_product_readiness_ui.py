from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "app" / "ui" / "static"


def test_dashboard_displays_product_readiness():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    script = (STATIC / "app.js").read_text(encoding="utf-8")

    assert 'id="readiness-panel"' in html
    assert "Video testi hazırlığı" in html
    assert 'fetch("/product/readiness"' in script
    assert "Video testine hazır" in script
    assert "Video testi için eksikler var" in script
    assert "Videodan yalnızca 14 masanın" in html
    assert "Kişi kimliği ve manuel masa ataması yapılmaz" in html
