from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def test_readme_explains_terminal_free_tutym2_r4_flow():
    text = README.read_text(encoding="utf-8")

    assert "T.UTYM#2 için terminalsiz hızlı yol" in text
    assert "app/ui/static/tutym2_r4_acceptance_center.html" in text
    assert "Güvenli Örnek JSON Dosyalarını İndir" in text
    assert "Dashboard Durum Raporu" in text
    assert "Saha Teslim Özeti" in text
    assert "R4 Final Karar Raporu" in text
    assert "KONTROLLÜ SAHA KABULÜNE HAZIR" in text
    assert "Güvenli örnek dosyalar resmi kapanış değildir" in text
