from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def test_readme_explains_video_first_tutym2_workflow():
    text = README.read_text(encoding="utf-8")

    assert "T.UTYM#2 için gerçek çalışma akışı" in text
    assert "Geliştirme aşaması" in text
    assert "14 masanın her biri için **dolu/boş**" in text
    assert "canlı kamera akışıyla veya kameradan alınmış eski bir video kaydıyla" in text
    assert "Fotoğraf ve elle seçilen JSON raporları bu akışın girdisi değildir" in text
    assert "scripts/run_tutym2_local_demo.py" in text
    assert "scripts/run_tutym2_rtsp_demo.py" in text


def test_readme_uses_video_validation_to_finish_product():
    text = README.read_text(encoding="utf-8")

    assert "Lokal geçmiş videoda 14 masanın" in text
    assert "Canlı kamera akışında veya eski kamera kaydında" in text
    assert "field_handoff_summary" not in text
    assert "dashboard_state.json" not in text
