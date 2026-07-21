from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_windows_launcher_starts_product_and_opens_dashboard():
    launcher = (ROOT / "TUTYM2_KONTROL.bat").read_text(encoding="utf-8")

    assert '.venv\\Scripts\\python.exe' in launcher
    assert "python --version" in launcher
    assert "py -3 --version" in launcher
    assert "%PYTHON_LAUNCH% -m uvicorn app.api.app:app" in launcher
    assert "--host 127.0.0.1 --port 8000" in launcher
    assert "http://127.0.0.1:8000/ui/index.html" in launcher
    assert "AddSeconds(20)" in launcher
    assert "Start-Sleep -Milliseconds 500" in launcher
    assert "netstat -ano" in launcher
    assert "taskkill /PID %%P /F" in launcher
    assert "openapi.json" in launcher
    assert "'/product/calibration-frame'" in launcher
    assert "Tarayici yine de acilacak" in launcher
    assert "exit /b 1" not in launcher.split("echo Guncel API hazir olana kadar bekleniyor...", 1)[1]
    assert "?v=%RANDOM%" in launcher
    assert 'app\\ui\\static\\tutym2_*.html' in launcher
    assert "for /r %%F in (.gitkeep)" in launcher


def test_windows_launcher_can_install_missing_dependencies():
    launcher = (ROOT / "TUTYM2_KONTROL.bat").read_text(encoding="utf-8")

    assert '%PYTHON_LAUNCH% -c "import uvicorn"' in launcher
    assert "choice /M" in launcher
    assert "%PYTHON_LAUNCH% -m pip install -r requirements.txt" in launcher


def test_readme_explains_double_click_product_control():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Her PR sonrasında ürünü kontrol etme" in readme
    assert "TUTYM2_KONTROL.bat" in readme
    assert "çift tıklayın" in readme
