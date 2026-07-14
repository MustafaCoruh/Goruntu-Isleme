# T.UTYM#2 Operatör Komut Kataloğu

Bu katalog, T.UTYM#2 saha akışında kullanılan scriptleri tek tek açıklar.

Hedef:

```text
Operatör veya yetkili teknik kişi hangi iş için hangi script kullanılır, ne girdi ister, ne çıktı üretir ve hangi durumda durulmalıdır sorularına tek dosyadan cevap bulsun.
```

> Not: Kurum politikası terminal kullanımını kısıtlıyorsa bu komutları operatör değil, yetkili BT/geliştirme sorumlusu çalıştırmalıdır.

## 1. Komut Güvenlik Kuralları

Hiçbir komut satırına veya rapora şu değerler yazılmamalıdır:

```text
Gerçek RTSP URL
Kamera IP adresi
Kamera kullanıcı adı/parolası
Gerçek görüntü/video içeriği
Tam lokal path paylaşımı
Katılımcı/yüz/kimlik bilgisi
```

Komutlarda lokal path kullanılması gerekebilir; fakat üretilen güvenli raporlar tam lokal path yazmamalıdır.

## 2. Hızlı Komut Haritası

| İhtiyaç | Script | Çıktı tipi |
| --- | --- | --- |
| Offline makine hazır mı? | `scripts/check_tutym2_offline_readiness.py` | `offline_readiness.json` |
| Offline paket manifesti güvenli mi? | `scripts/validate_tutym2_offline_package_manifest.py` | manifest validation JSON |
| Lokal config geçerli mi? | `scripts/validate_tutym2_config.py` | config validation sonucu |
| Lokal fotoğraf/video demo | `scripts/run_tutym2_local_demo.py` | local demo report |
| RTSP bağlantı/demo | `scripts/run_tutym2_rtsp_demo.py` | RTSP report |
| Table accuracy raporu geçerli mi? | `scripts/validate_tutym2_table_accuracy_report.py` | table report validation sonucu |
| Dashboard state üret | `scripts/build_tutym2_dashboard_state.py` | `dashboard_state.json` |
| Dashboard state doğrula | `scripts/validate_tutym2_dashboard_state.py` | dashboard validation sonucu |
| Saha teslim özeti üret | `scripts/build_tutym2_field_handoff_summary.py` | `field_handoff_summary.json` |

## 3. `check_tutym2_offline_readiness.py`

Amaç:

```text
Saha bilgisayarının temel offline çalışmaya hazır olup olmadığını kontrol eder.
```

Kontrol ettiği şeyler:

```text
Python sürümü
Temel importlar
Opsiyonel runtime importları
Lokal klasörler
Config dosyası var mı?
Model dosyası var mı?
Rapor yazılabiliyor mu?
```

Örnek kullanım:

```powershell
python scripts/check_tutym2_offline_readiness.py `
  --field-root C:\FTMC_FIELD_DATA `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx `
  --report-output C:\FTMC_FIELD_DATA\reports\offline_readiness.json
```

Durulması gereken durum:

```text
overall_status = fail
```

Fail varsa demo veya RTSP testine geçilmemelidir.

## 4. `validate_tutym2_offline_package_manifest.py`

Amaç:

```text
Offline saha paketinin gerekli dosya/kategori listesini ve hassas veri riskini kontrol eder.
```

Örnek kullanım:

```powershell
python scripts/validate_tutym2_offline_package_manifest.py `
  configs/templates/tutym2_offline_package_manifest.template.json `
  --report-output C:\FTMC_FIELD_DATA\reports\offline_package_manifest_validation.json
```

Durulması gereken durum:

```text
Manifest eksik zorunlu repo dosyası söylüyorsa
Manifest içinde RTSP URL, IP veya credential riski söylüyorsa
```

Bu durumda paket sahaya taşınmadan önce düzeltilmelidir.

## 5. `validate_tutym2_config.py`

Amaç:

```text
T.UTYM#2 kamera/config dosyasının beklenen yapıda olup olmadığını kontrol eder.
```

Beklenenler:

```text
site = T.UTYM#2
camera_id = TUTYM2-CAM-001
resolution = 1920x1080
masa sayısı = 14
polygon değerleri görüntü sınırları içinde
```

Örnek kullanım:

```powershell
python scripts/validate_tutym2_config.py C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json
```

Durulması gereken durum:

```text
14 masa yoksa
Çözünürlük yanlışsa
Polygon değerleri hatalıysa
Hassas RTSP bilgisi beklenmeyen yerdeyse
```

## 6. `run_tutym2_local_demo.py`

Amaç:

```text
Canlı kameraya geçmeden önce lokal fotoğraf veya video ile masa doluluk akışını test eder.
```

Örnek kullanım:

```powershell
python scripts/run_tutym2_local_demo.py `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --source C:\FTMC_FIELD_DATA\inputs\sample.mp4 `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx `
  --report-output C:\FTMC_FIELD_DATA\reports\local_demo_report.json
```

Durulması gereken durum:

```text
Model yoksa
Source dosyası desteklenmiyorsa
Config doğrulanmadıysa
Rapor güvenli değilse
```

## 7. `run_tutym2_rtsp_demo.py`

Amaç:

```text
RTSP canlı kamera bağlantısını veya canlı demo akışını güvenli şekilde test eder.
```

Örnek bağlantı testi mantığı:

```powershell
python scripts/run_tutym2_rtsp_demo.py `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.rtsp.local.json `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx `
  --connection-test-frames 5 `
  --report-output C:\FTMC_FIELD_DATA\reports\rtsp_connection_report.json
```

Durulması gereken durum:

```text
RTSP config placeholder kalmışsa
Kamera frame vermiyorsa
Rapor RTSP URL veya IP içeriyorsa
```

RTSP URL hiçbir zaman repo'ya veya paylaşılan rapora yazılmamalıdır.

## 8. `validate_tutym2_table_accuracy_report.py`

Amaç:

```text
Masa bazlı doğruluk raporunun güvenli ve tutarlı olup olmadığını kontrol eder.
```

Örnek kullanım:

```powershell
python scripts/validate_tutym2_table_accuracy_report.py C:\FTMC_FIELD_DATA\reports\table_accuracy_report.json
```

Durulması gereken durum:

```text
14 masa yoksa
Özet metrikler masa detaylarıyla uyuşmuyorsa
Rapor hassas veri içeriyorsa
```

## 9. `build_tutym2_dashboard_state.py`

Amaç:

```text
Birden fazla güvenli rapordan tek dashboard_state.json üretir.
```

Örnek kullanım mantığı:

```powershell
python scripts/build_tutym2_dashboard_state.py `
  --offline-readiness C:\FTMC_FIELD_DATA\reports\offline_readiness.json `
  --rtsp-report C:\FTMC_FIELD_DATA\reports\rtsp_connection_report.json `
  --table-accuracy C:\FTMC_FIELD_DATA\reports\table_accuracy_report.json `
  --output C:\FTMC_FIELD_DATA\reports\dashboard_state.json
```

Durulması gereken durum:

```text
Input raporlardan biri eksikse
Dashboard state critical üretiyorsa
Güvenlik bayraklarından biri true ise
```

## 10. `validate_tutym2_dashboard_state.py`

Amaç:

```text
Statik dashboard'a yüklenmeden önce dashboard_state.json dosyasını doğrular.
```

Örnek kullanım:

```powershell
python scripts/validate_tutym2_dashboard_state.py C:\FTMC_FIELD_DATA\reports\dashboard_state.json
```

Durulması gereken durum:

```text
site T.UTYM#2 değilse
camera_id beklenen değilse
14 table card yoksa
safety flag true ise
```

Dashboard state doğrulanmadan dashboard üzerinden karar verilmemelidir.

## 11. `build_tutym2_field_handoff_summary.py`

Amaç:

```text
Saha sonunda birden fazla güvenli raporu tek paylaşılabilir saha teslim özetine çevirir.
```

Örnek kullanım:

```powershell
python scripts/build_tutym2_field_handoff_summary.py `
  --input offline_readiness=C:\FTMC_FIELD_DATA\reports\offline_readiness.json `
  --input dashboard_state_validation=C:\FTMC_FIELD_DATA\reports\dashboard_state_validation.json `
  --input table_accuracy=C:\FTMC_FIELD_DATA\reports\table_accuracy_report.json `
  --output C:\FTMC_FIELD_DATA\reports\field_handoff_summary.json
```

Durulması gereken durum:

```text
overall_status = critical
safe_to_share = false
Input raporlardan biri hassas veri içeriyor
```

## 12. Komutların Çalışma Sırası

Önerilen güvenli sıra:

```text
1. validate_tutym2_offline_package_manifest.py
2. check_tutym2_offline_readiness.py
3. validate_tutym2_config.py
4. run_tutym2_rtsp_demo.py --connection-test-frames ...
5. run_tutym2_local_demo.py veya run_tutym2_rtsp_demo.py
6. validate_tutym2_table_accuracy_report.py
7. build_tutym2_dashboard_state.py
8. validate_tutym2_dashboard_state.py
9. build_tutym2_field_handoff_summary.py
```

## 13. Operatör İçin Son Karar Tablosu

| Sonuç | Anlam | Aksiyon |
| --- | --- | --- |
| Komut `pass/normal` | İlgili adım uygun | Sıradaki adıma geçilebilir |
| Komut `warn/warning` | Eksik/şüpheli durum var | Teknik kişi kontrol eder |
| Komut `fail/critical` | Adım güvenilir değil | Canlı/demo kararında kullanılmaz |
| Rapor `safe_to_share=false` | Paylaşım güvenli değil | Rapor paylaşılmaz |
| Güvenlik flag `true` | Hassas veri riski var | Akış durdurulur |

## 14. Ana Runbook Bağlantısı

Bu katalog komutları anlatır. Tüm saha akışının baştan sona açıklaması için ana runbook kullanılmalıdır:

```text
docs/deployment/tutym2_operator_master_runbook.md
```


## 15. Hata ve Çözüm Rehberi

Komutlardan hata alındığında veya `warning/critical/fail` sonucu görüldüğünde şu rehber kullanılmalıdır:

```text
docs/deployment/tutym2_operator_troubleshooting_guide.md
```
