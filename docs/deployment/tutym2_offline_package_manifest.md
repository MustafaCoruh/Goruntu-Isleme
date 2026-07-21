# T.UTYM#2 Offline Paket Manifesti

Bu doküman, T.UTYM#2 saha bilgisayarına aktarılacak offline paketin **ne içermesi gerektiğini** ve **ne içermemesi gerektiğini** tek yerde toplar.

Amaç, operatör veya teknik sorumlu için şu soruyu net cevaplamaktır:

```text
Bu paket sahaya taşınmaya hazır mı ve içinde hassas veri var mı?
```

## 1. Neden Manifest Gerekli?

Sistem ürün gibi kullanılacaksa her saha kurulumunda aynı şeyler kontrol edilmelidir:

- Gerekli kod dosyaları pakette var mı?
- Gerekli scriptler pakette var mı?
- Dashboard dosyaları pakette var mı?
- Config template dosyaları pakette var mı?
- Gerçek RTSP URL, kamera IP, parola, görüntü veya video yanlışlıkla pakete girmiş mi?
- Model ve gerçek saha verisi repo dışında mı tutuluyor?

Bu yüzden repo içinde güvenli bir manifest template'i tutulur:

```text
configs/templates/tutym2_offline_package_manifest.template.json
```

Bu dosya gerçek kamera bilgisi içermez. Sadece güvenli dosya isimlerini, görevleri ve operatör kontrollerini listeler.

## 2. Manifest İçinde Olması Gereken Repo Dosyaları

Manifest, en az şu kategorileri kapsamalıdır:

| Kategori | Örnek dosya | Amaç |
| --- | --- | --- |
| Lokal demo runner | `app/field_demo.py` | Video testi |
| RTSP runner | `app/rtsp_field_demo.py` | Canlı kamera veya bağlantı testi |
| Offline readiness | `app/offline_readiness.py` | Kurulum ön kontrolü |
| Dashboard state builder | `app/dashboard_state.py` | Güvenli dashboard JSON üretimi |
| Dashboard validator | `app/dashboard_state_validator.py` | Dashboard JSON doğrulama |
| Config template | `configs/templates/tutym2_cam_001.template.json` | Lokal kalibrasyon başlangıcı |
| RTSP template | `configs/templates/tutym2_cam_001.rtsp.template.json` | Lokal RTSP config başlangıcı |
| Dashboard UI | `app/ui/static/tutym2_dashboard.html` | Statik operatör ekranı |
| Saha checklist | `docs/deployment/tutym2_field_day_one_page_checklist.md` | Tek sayfalık saha akışı |

## 3. Sadece Lokal Kalması Gerekenler

Aşağıdaki dosyalar veya veri grupları manifestte yalnızca kategori olarak anılır; gerçek değerleri repo'ya yazılmaz:

| Lokal öğe | Örnek güvenli ad | Repo'ya konur mu? |
| --- | --- | --- |
| Lokal config | `tutym2_cam_001.local.json` | Hayır |
| Model dosyası | `person_detector.onnx` | Kurum politikasına göre; varsayılan hayır |
| Gerçek video | Operatör seçimi | Hayır |
| Lokal raporlar | `offline_readiness.json`, `dashboard_state.json` | Sadece güvenli özetse paylaşılabilir |

## 4. Manifestte Bile Yazılmaması Gerekenler

Manifest güvenli bir dosya olsa bile içine şunlar yazılmamalıdır:

```text
Gerçek kamera stream bilgisi
Kamera ağ adresi
Kamera kullanıcı adı
Kamera parolası
Gerçek oda videosu adı
Gerçek video dosya adı
Tam lokal Windows/Linux path bilgisi
Katılımcı kimliği veya kişisel veri
```

## 5. Manifest Validator

Bu PR ile manifesti kontrol etmek için şu validator eklenmiştir:

```text
app/offline_package_manifest.py
scripts/validate_tutym2_offline_package_manifest.py
```

Validator şu kontrolleri yapar:

- `package_name` doğru mu?
- `site` değeri `T.UTYM#2` mi?
- Zorunlu repo dosyaları listelenmiş mi?
- Zorunlu lokal-only kategorileri listelenmiş mi?
- En az temel yasaklı veri kategorileri yazılmış mı?
- En az temel handoff kontrolleri var mı?
- Manifest içinde RTSP benzeri değer, credential kelimesi, IP adresi veya tam lokal path var mı?

## 6. Örnek Kullanım

Terminal erişimi olan yetkili kişi şu mantıkta çalıştırır:

```powershell
python scripts/validate_tutym2_offline_package_manifest.py `
  configs/templates/tutym2_offline_package_manifest.template.json `
  --report-output C:\FTMC_FIELD_DATA\reports\offline_package_manifest_validation.json
```

Çıktı güvenli JSON özetidir. Gerçek RTSP URL, kamera IP, parola, görüntü veya tam lokal path içermez.

## 7. Operatör İçin Basit Karar

| Sonuç | Anlamı | Ne yapılır? |
| --- | --- | --- |
| `pass` | Manifest güvenli ve temel olarak tamam | Offline paket hazırlığına devam edilebilir |
| Hata | Eksik dosya/kategori veya hassas veri riski var | Paket sahaya taşınmadan önce düzeltilir |

## 8. Ürünleşme Notu

Bu manifest yaklaşımı T.UTYM#2 için başlamıştır ama ileride çoklu UTYM yapısına genişletilebilir.

İleride her UTYM için ayrı manifest üretilebilir:

```text
tutym2_offline_package_manifest.json
tutym3_offline_package_manifest.json
tutym4_offline_package_manifest.json
```

Böylece her UTYM kurulumu aynı standartla kontrol edilir.
