from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_windows_launcher_starts_product_and_opens_dashboard():
    launcher = (ROOT / "TUTYM2_KONTROL.bat").read_text(encoding="utf-8")

    assert "python -m uvicorn app.api.app:app" in launcher
    assert "--host 127.0.0.1 --port 8000" in launcher
    assert "http://127.0.0.1:8000/ui/index.html" in launcher
    assert "timeout /t 3" in launcher


def test_readme_explains_double_click_product_control():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Her PR sonrasında ürünü kontrol etme" in readme
    assert "TUTYM2_KONTROL.bat" in readme
    assert "çift tıklayın" in readme
