from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
R4_CENTER = ROOT / "app" / "ui" / "static" / "tutym2_r4_acceptance_center.html"
INDEX = ROOT / "app" / "ui" / "static" / "index.html"
DEBUG = ROOT / "app" / "ui" / "static" / "debug.html"
RELEASE_CHECKLIST = ROOT / "docs" / "deployment" / "tutym2_release_readiness_checklist.md"
R4_GATE_EXAMPLE = ROOT / "configs" / "templates" / "tutym2_r4_acceptance_gate.example.json"


def test_r4_acceptance_center_has_terminal_free_acceptance_flow():
    html = R4_CENTER.read_text(encoding="utf-8")

    assert "T.UTYM#2 R4 Saha Kabul Merkezi" in html
    assert "Terminalsiz JSON Hızlı Kontrol" in html
    assert "1. Dashboard Durum Raporu seç" in html
    assert "2. Saha Teslim Özeti seç" in html
    assert "R4 Bitince Söylenecek Kapanış" in html
    assert "3. R4 Final Karar Raporu seç" in html
    assert "Dosya adlarını bilmiyorsan" in html
    assert "Bu 3 Dosya Nedir?" in html
    assert "Dashboard'un okuyacağı güvenli özet dosyadır" in html
    assert "R4'ün kapatılıp kapatılamayacağını gösteren son karar dosyasıdır" in html
    assert "Bu Dosyalar Nereden Gelecek?" in html
    assert "Senin görevin" in html
    assert "Operatör bunu elle yazmaz" in html
    assert "Dosyalar Yoksa Ne Anlama Gelir?" in html
    assert "R4 kapatılamaz" in html
    assert "gerçek R4 tamamlandı denmemelidir" in html
    assert "report_type" in html
    assert "Merge Sonrası Senin Kontrol Listen" in html
    assert "tutym2_r4_operator_checklist" in html
    assert "Toplu R4 Görsel Sonuç" in html
    assert "R4 GÖRSEL SONUÇ: KONTROLLÜ SAHA KABULÜNE HAZIR" in html
    assert "Güvenli Örnekle Dene" in html
    assert "gerçek R4 kapanışı için saha dosyaları seçilmelidir" in html
    assert "Dosyaları İsterken Kullanılacak Kısa Metin" in html
    assert "Bu İstek Metnini Kopyala" in html
    assert "navigator.clipboard.writeText" in html


def test_r4_acceptance_center_checks_safety_and_14_tables():
    html = R4_CENTER.read_text(encoding="utf-8")

    assert "payload.tables.length !== 14" in html
    assert "contains_rtsp_url" in html
    assert "contains_credentials" in html
    assert "contains_image_or_video" in html
    assert "contains_full_local_path" in html
    assert "hasUnsafeText" in html
    assert "requiredGateSafetyKeys" in html
    assert "ready_for_controlled_field_acceptance" in html
    assert "quickCheckState" in html
    assert "updateAggregateResult" in html


def test_r4_acceptance_center_is_linked_from_static_pages_and_docs():
    for path in (INDEX, DEBUG, RELEASE_CHECKLIST):
        assert "tutym2_r4_acceptance_center.html" in path.read_text(encoding="utf-8")


def test_r4_acceptance_gate_example_is_safe_and_documented():
    import json

    payload = json.loads(R4_GATE_EXAMPLE.read_text(encoding="utf-8"))

    assert payload["report_type"] == "r4_acceptance_gate"
    assert payload["site"] == "T.UTYM#2"
    assert payload["camera_id"] == "TUTYM2-CAM-001"
    assert payload["ready_for_controlled_field_acceptance"] is True
    assert payload["summary"]["table_count"] == 14
    assert not payload["blockers"]
    assert all(value is False for value in payload["safety"].values())
    assert "tutym2_r4_acceptance_gate.example.json" in RELEASE_CHECKLIST.read_text(encoding="utf-8")
