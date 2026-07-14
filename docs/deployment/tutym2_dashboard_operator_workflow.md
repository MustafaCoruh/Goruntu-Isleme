# T.UTYM#2 Dashboard Operatör Kullanım Akışı

Bu kılavuz, T.UTYM#2 operatör dashboard'unu güvenli şekilde kullanmak için izlenecek sırayı anlatır.

Amaç:

```text
Önce güvenli raporlar üretilir.
Sonra dashboard_state.json oluşturulur.
Ardından dashboard_state.json doğrulanır.
En son statik dashboard açılır ve state dosyası yüklenir.
```

Bu akış gerçek görüntü, RTSP URL, IP adresi, kullanıcı adı/parola veya tam lokal path paylaşmadan ilerlemek için tasarlanmıştır.

## 1. Gerekli Dosyalar

VS Code içinde şu dosyalar bulunmalıdır:

```text
app/offline_readiness.py
app/tutym2_config_validator.py
app/rtsp_field_demo.py
app/dashboard_state.py
app/dashboard_state_validator.py
app/ui/static/tutym2_dashboard.html
scripts/check_tutym2_offline_readiness.py
scripts/validate_tutym2_config.py
scripts/run_tutym2_rtsp_demo.py
scripts/build_tutym2_dashboard_state.py
scripts/validate_tutym2_dashboard_state.py
```

Bu dosyalar yoksa ilgili PR merge/pull işlemi kontrol edilmelidir.

## 2. Lokal Rapor Klasörü

Dashboard akışında raporlar şu lokal klasörde toplanır:

```text
C:\FTMC_FIELD_DATA\reports\
```

Bu klasör repo dışında olmalıdır.

## 3. Adım 1 — Offline Readiness Raporu Üret

Yetkili teknik kişi şu komutu çalıştırır:

```powershell
python scripts/check_tutym2_offline_readiness.py `
  --field-root C:\FTMC_FIELD_DATA `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx `
  --report-output C:\FTMC_FIELD_DATA\reports\offline_readiness.json
```

Beklenen çıktı dosyası:

```text
C:\FTMC_FIELD_DATA\reports\offline_readiness.json
```

## 4. Adım 2 — Config Doğrulama Özeti Üret

Lokal config dosyasını doğrulamak için:

```powershell
python scripts/validate_tutym2_config.py `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --summary-output C:\FTMC_FIELD_DATA\reports\config_validation_summary.json
```

Eğer lokal RTSP config içinde gerçek RTSP URL varsa sadece yetkili teknik kişi lokal ortamda şu parametreyi kullanabilir:

```text
--allow-real-rtsp
```

Gerçek RTSP URL hiçbir zaman repo'ya eklenmemelidir.

## 5. Adım 3 — RTSP Bağlantı Testi Raporu Üret

RTSP bağlantı testi için:

```powershell
python scripts/run_tutym2_rtsp_demo.py `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.rtsp.local.json `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx `
  --report-output C:\FTMC_FIELD_DATA\reports\rtsp_connection_test.json `
  --connection-test-frames 10
```

Bu test kamera frame okuyabilir ama rapora görüntü veya RTSP URL yazmamalıdır.

## 6. Adım 4 — Masa Doğruluk Raporu Hazırla

Model performans değerlendirmesi yapıldıysa şu dosya lokal olarak hazırlanabilir:

```text
C:\FTMC_FIELD_DATA\reports\tutym2_table_accuracy_report.json
```

Bu raporun formatı için:

```text
docs/validation/tutym2_table_accuracy_report_format.md
```

Bu raporu doğrulamak için:

```powershell
python scripts/validate_tutym2_table_accuracy_report.py `
  --report C:\FTMC_FIELD_DATA\reports\tutym2_table_accuracy_report.json
```

## 7. Adım 5 — Dashboard State Üret

Güvenli dashboard state üretmek için:

```powershell
python scripts/build_tutym2_dashboard_state.py `
  --reports-dir C:\FTMC_FIELD_DATA\reports `
  --output C:\FTMC_FIELD_DATA\reports\dashboard_state.json
```

Beklenen çıktı:

```text
C:\FTMC_FIELD_DATA\reports\dashboard_state.json
```

## 8. Adım 6 — Dashboard State Doğrula

UI'a yüklemeden önce state dosyasını doğrula:

```powershell
python scripts/validate_tutym2_dashboard_state.py `
  --state C:\FTMC_FIELD_DATA\reports\dashboard_state.json
```

Başarılıysa şu mantıkta güvenli çıktı görülür:

```json
{
  "status": "valid",
  "site": "T.UTYM#2",
  "camera_id": "TUTYM2-CAM-001"
}
```

## 9. Adım 7 — Statik Dashboard'u Aç

VS Code veya tarayıcı üzerinden şu dosyayı aç:

```text
app/ui/static/tutym2_dashboard.html
```

Dashboard üzerinde:

```text
1. dashboard_state.json yükle butonunu kullan.
2. C:\FTMC_FIELD_DATA\reports\dashboard_state.json dosyasını seç.
3. Genel durum, FPS, masa özeti, 14 masa kartı, uyarılar ve kritikler ekranda görünür.
```

## 10. Operatör Ne Paylaşabilir?

Güvenli paylaşılabilir özet:

```text
overall_status: normal/warning/critical/not_ready
connection_status: connected/disconnected/not_tested
average_fps: ...
table_summary: total/occupied/empty/unknown/no_data
warnings count: ...
criticals count: ...
safety flags all false: Evet
```

Paylaşılmaması gerekenler:

```text
Gerçek görüntü
Gerçek video
RTSP URL
Kamera IP adresi
Kullanıcı adı/parola
Tam lokal path
Kişi adı
Yüz görüntüsü
```

## 11. Hızlı Karar

| Durum | Anlamı | Aksiyon |
| --- | --- | --- |
| `overall_status = normal` | Temel durum iyi | Teste devam edilebilir |
| `overall_status = warning` | Kontrol gereken konu var | Uyarılar okunmalı |
| `overall_status = critical` | Ciddi sorun var | Canlı teste devam edilmemeli |
| `overall_status = not_ready` | Rapor yok veya akış başlamadı | Önce raporlar üretilmeli |

## 12. Terminal Kullanamayan Operatör İçin Not

Eğer terminal kullanamıyorsanız bu komutları siz çalıştırmayacaksınız. Yetkili BT/geliştirme sorumlusu çalıştıracak.

Sizin yapmanız gereken:

```text
1. PR'ların VS Code'a geldiğini kontrol etmek.
2. Statik dashboard dosyasını açmak.
3. Yetkili kişinin ürettiği dashboard_state.json dosyasını dashboard'a yüklemek.
4. Genel durum, uyarılar ve kritikler alanlarını okumak.
```
