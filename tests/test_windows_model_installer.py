from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_windows_model_installer_accepts_dragged_onnx_file():
    installer = (ROOT / "TUTYM2_MODEL_KUR.bat").read_text(encoding="utf-8")

    assert 'if "%~1"==""' in installer
    assert "surukleyip birakin" in installer
    assert 'scripts\\install_tutym2_person_model.py "%~1"' in installer
    assert '.venv\\Scripts\\python.exe' in installer
    assert "py -3 --version" in installer
    assert "TUTYM2_KONTROL.bat" in installer
