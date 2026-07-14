# T.UTYM#2 Release Readiness Checklist

Bu checklist, T.UTYM#2 uygulamasının saha öncesi **sunuma / operatör kullanımına / kontrollü demo paketine** hazır olup olmadığını hızlıca değerlendirmek için hazırlanmıştır.

Bu doküman şu soruya cevap verir:

```text
Bu noktada sistemi kullanabilir miyiz, sunabilir miyiz, yoksa hangi eksikler tamamlanmadan release dememeliyiz?
```

## 1. Release Seviyeleri

| Seviye | Anlam | Kullanım durumu |
| --- | --- | --- |
| R0 - Dokümantasyon hazır | Akış, komutlar ve güvenlik kuralları yazılı | Teknik/operatör incelemesi |
| R1 - Lokal demo hazır | Lokal fotoğraf/video ile güvenli demo çalışabilir | Kontrollü iç demo |
| R2 - RTSP bağlantı testi hazır | Canlı kameradan güvenli bağlantı raporu üretilebilir | Saha teknik doğrulama |
| R3 - Dashboard demo hazır | Güvenli dashboard_state ile statik dashboard gösterilebilir | Yönetici/operatör sunumu |
| R4 - Saha kabul adayı | Readiness, config, RTSP, doğruluk, dashboard ve handoff raporları tamam | Kontrollü saha kabul denemesi |
| R5 - Çoklu UTYM adayı | T.UTYM#2 standardı başka UTYM'lere kopyalanabilir | Ürünleşme/yayılım |

Şu anki hedefimiz hızlıca **R3 - Dashboard demo hazır** seviyesine ulaşmaktır. R4 için gerçek lokal saha raporları ve doğruluk ölçümü gerekir.

## 2. Kod ve Araç Hazırlığı

| Kontrol | Beklenen | Durum |
| --- | --- | --- |
| Local demo runner var | `app/field_demo.py` | `[ ]` |
| RTSP runner var | `app/rtsp_field_demo.py` | `[ ]` |
| Offline readiness var | `app/offline_readiness.py` | `[ ]` |
| Config validator var | `app/tutym2_config_validator.py` | `[ ]` |
| Dashboard state builder var | `app/dashboard_state.py` | `[ ]` |
| Dashboard state validator var | `app/dashboard_state_validator.py` | `[ ]` |
| Field handoff summary var | `app/field_handoff_summary.py` | `[ ]` |
| Offline package manifest validator var | `app/offline_package_manifest.py` | `[ ]` |

Bu kontroller eksikse release adayı olunmaz.

## 3. Script Hazırlığı

| Kontrol | Beklenen script | Durum |
| --- | --- | --- |
| Offline readiness script | `scripts/check_tutym2_offline_readiness.py` | `[ ]` |
| Lokal demo script | `scripts/run_tutym2_local_demo.py` | `[ ]` |
| RTSP demo script | `scripts/run_tutym2_rtsp_demo.py` | `[ ]` |
| Config validator script | `scripts/validate_tutym2_config.py` | `[ ]` |
| Dashboard build script | `scripts/build_tutym2_dashboard_state.py` | `[ ]` |
| Dashboard validate script | `scripts/validate_tutym2_dashboard_state.py` | `[ ]` |
| Table accuracy validator script | `scripts/validate_tutym2_table_accuracy_report.py` | `[ ]` |
| Handoff summary script | `scripts/build_tutym2_field_handoff_summary.py` | `[ ]` |
| Offline package manifest script | `scripts/validate_tutym2_offline_package_manifest.py` | `[ ]` |

Scriptler yoksa operatör akışı tamam değildir.

## 4. UI ve Template Hazırlığı

| Kontrol | Beklenen dosya | Durum |
| --- | --- | --- |
| Statik dashboard var | `app/ui/static/tutym2_dashboard.html` | `[ ]` |
| Dashboard linkleri var | `app/ui/static/index.html` / `debug.html` | `[ ]` |
| Kalibrasyon UI güncel | `app/ui/static/calibration.html` | `[ ]` |
| Lokal config template var | `configs/templates/tutym2_cam_001.template.json` | `[ ]` |
| RTSP config template var | `configs/templates/tutym2_cam_001.rtsp.template.json` | `[ ]` |
| Dashboard state example var | `configs/templates/tutym2_dashboard_state.example.json` | `[ ]` |
| Table accuracy template var | `configs/templates/tutym2_table_accuracy_report.template.json` | `[ ]` |
| Offline package manifest template var | `configs/templates/tutym2_offline_package_manifest.template.json` | `[ ]` |
| Field handoff summary example var | `configs/templates/tutym2_field_handoff_summary.example.json` | `[ ]` |

Bu bölüm R3 dashboard demo için kritiktir.

## 5. Dokümantasyon Hazırlığı

| Kontrol | Beklenen doküman | Durum |
| --- | --- | --- |
| Ana runbook var | `docs/deployment/tutym2_operator_master_runbook.md` | `[ ]` |
| Komut kataloğu var | `docs/deployment/tutym2_operator_command_catalog.md` | `[ ]` |
| Hata/çözüm rehberi var | `docs/deployment/tutym2_operator_troubleshooting_guide.md` | `[ ]` |
| Saha günü checklist var | `docs/deployment/tutym2_field_day_one_page_checklist.md` | `[ ]` |
| Offline kurulum planı var | `docs/deployment/tutym2_offline_installation_plan.md` | `[ ]` |
| RTSP operator guide var | `docs/deployment/tutym2_rtsp_operator_guide.md` | `[ ]` |
| Dashboard workflow var | `docs/deployment/tutym2_dashboard_operator_workflow.md` | `[ ]` |
| Static dashboard guide var | `docs/deployment/tutym2_static_dashboard_operator_guide.md` | `[ ]` |
| Handoff summary guide var | `docs/deployment/tutym2_field_handoff_summary.md` | `[ ]` |
| Non-shareable data workflow var | `docs/requirements/non_shareable_real_data_workflow.md` | `[ ]` |

Dokümantasyon eksikse operatör hatasına dayanıklılık zayıflar.

## 6. Güvenlik Release Kapıları

Aşağıdaki kapılardan biri başarısızsa release yapılmamalıdır:

| Kapı | Release için şart |
| --- | --- |
| Gerçek görüntü/video repo'da yok | Zorunlu |
| Gerçek RTSP URL repo'da yok | Zorunlu |
| Kamera IP/credential repo'da yok | Zorunlu |
| Model dosyası politikaya uygun yerde | Zorunlu |
| Raporlar tam lokal path yazmıyor | Zorunlu |
| Dashboard state safety flag değerleri false | Zorunlu |
| `safe_to_share=false` rapor paylaşılmıyor | Zorunlu |

Bu kapılar güvenlik açısından doğruluk/hız/görsellikten önce gelir.

## 7. Saha Öncesi Çalıştırılacak Minimum Akış

R3 dashboard demo için minimum güvenli akış:

```text
1. Offline package manifest kontrolü
2. Offline readiness kontrolü
3. Config validation
4. RTSP connection test veya lokal demo report
5. Dashboard state build
6. Dashboard state validation
7. Static dashboard görüntüleme
8. Field handoff summary üretimi
```

Bu minimum akış tamamlanmadan “sunuma hazır” denmemelidir.

## 8. Ne Zaman Kullanabilirsin?

Pratik cevap:

```text
VS Code'a son PR'lar geldikten sonra R3 demo hazırlığı yapılabilir.
```

R3 için gerekenler:

- Kod ve dokümanlar merge edilmiş olacak.
- Lokal saha klasörü hazırlanacak.
- Model lokal klasöre konacak.
- Lokal config hazırlanacak.
- En az bir güvenli demo/connection raporu üretilecek.
- Dashboard state üretilecek ve validate edilecek.
- Statik dashboard açılıp güvenli JSON yüklenecek.

Gerçek saha kabulü yani R4 için ayrıca gerçek T.UTYM#2 lokal test verisiyle doğruluk raporu gerekir.

## 9. Sunum İçin Minimum Paket

Sunumda gösterilebilecek güvenli öğeler:

```text
Ana runbook
Komut kataloğu
Troubleshooting guide
Offline package manifest
Dashboard state example
Static dashboard
Field handoff summary example
Validation/checklist dokümanları
```

Sunumda gösterilmemesi gerekenler:

```text
Gerçek kamera görüntüsü
Gerçek RTSP URL
Kamera IP
Kullanıcı adı/parola
Gerçek katılımcı bilgisi
Tam lokal path
```

## 10. Kalan Kritik İşler

R3 için kalan kritik işler:

```text
1. Son PR'ların VS Code'a çekildiğini kontrol etmek.
2. Offline saha klasörünü oluşturmak.
3. Model dosyasını lokal models klasörüne koymak.
4. Lokal config dosyasını oluşturmak.
5. Bir güvenli local demo veya RTSP connection report üretmek.
6. dashboard_state.json üretmek ve validate etmek.
7. Statik dashboard'da sonucu göstermek.
```

R4 için ek işler:

```text
1. Gerçek T.UTYM#2 sahasında kontrollü test yapmak.
2. Masa bazlı doğruluk raporu üretmek.
3. False positive / false negative sayıları değerlendirmek.
4. Operatör kabul checklist'ini tamamlamak.
5. Handoff summary ile güvenli kapanış yapmak.
```

## 11. Hızlandırma Kararı

Bundan sonra küçük dokümantasyon PR'ları yerine şu sıraya geçmek önerilir:

```text
1. R3 dashboard demo smoke package
2. Lokal demo için örnek komut seti
3. Dashboard state örnek yükleme akışı
4. Saha bilgisayarında ilk offline readiness sonucu
5. İlk gerçek lokal config validation sonucu
```

Yani artık hedef, belge üretmekten çok **ilk kontrollü demo koşusunu** hazırlamaktır.

## 12. Release Kararı

| Şart | R3 demo için gerekli mi? | R4 saha kabul için gerekli mi? |
| --- | --- | --- |
| Ana runbook | Evet | Evet |
| Komut kataloğu | Evet | Evet |
| Troubleshooting guide | Evet | Evet |
| Offline package manifest | Evet | Evet |
| Offline readiness pass/warn | Evet | Evet |
| Config validation pass | Evet | Evet |
| RTSP connection report | Tercihen | Evet |
| Local demo report | Evet | Evet |
| Dashboard state validation pass | Evet | Evet |
| Table accuracy report | Tercihen | Evet |
| Field handoff summary | Evet | Evet |

R3 demo, operatör/yönetici sunumu için yeterlidir. R4 ise gerçek saha kabulüne daha yakındır.


## 13. R3 Dashboard Demo Smoke Plan

R3 dashboard demosunu hızlı ve güvenli yapmak için şu plan kullanılmalıdır:

```text
docs/deployment/tutym2_r3_dashboard_demo_smoke_plan.md
```

Bu plan gerçek görüntü veya RTSP URL göstermeden statik dashboard sunumu yapmaya odaklanır.

## 14. Terminalsiz R4 Kabul Merkezi

R4'e odaklanmak için terminalsiz bir statik kabul merkezi eklendi:

```text
app/ui/static/tutym2_r4_acceptance_center.html
```

Bu sayfa şu amaçlarla kullanılmalıdır:

- R4 için zorunlu çıktıları tek ekranda görmek.
- `dashboard_state.json` dosyasını tarayıcı içinde hızlı kontrol etmek.
- `field_handoff_summary.json` dosyasını tarayıcı içinde hızlı kontrol etmek.
- R4 ile R3 arasındaki farkı net anlatmak.
- Gerçek görüntü, RTSP URL, kamera IP, credential ve tam lokal path göstermeden saha kabul paketini kapatmak.

Bu sayfa tek başına gerçek saha testinin yerine geçmez. R4'ün tamamlanması için gerçek saha makinesinde üretilmiş güvenli raporların bu merkezde ve Python validator'larında başarılı olması gerekir.

## 15. R4 Acceptance Gate JSON

R4 kapanışını tek dosyada özetlemek için güvenli acceptance gate raporu üretilebilir:

```text
scripts/build_tutym2_r4_acceptance.py
```

Bu araç şu üç güvenli JSON dosyasını birlikte değerlendirir:

- `dashboard_state.json`
- `field_handoff_summary.json`
- `table_accuracy_report.json`

Çıktı olarak `r4_acceptance_gate` raporu üretir. Bu raporda sadece güvenli özetler, durum, blocker/warning listeleri ve safety flag değerleri bulunur. Gerçek görüntü, RTSP URL, IP, credential veya tam lokal path yazılmaz.

## 16. R4 Final Kapanış Dosyası

R4'ü kapatırken bakılacak son güvenli dosya:

```text
r4_acceptance_gate.json
```

Örnek güvenli format:

```text
configs/templates/tutym2_r4_acceptance_gate.example.json
```

Terminal kullanamayan operatör için bu dosya `app/ui/static/tutym2_r4_acceptance_center.html` içinde seçilip hızlı kontrol edilebilir. `overall_status=ready` veya `ready_with_warnings`, `ready_for_controlled_field_acceptance=true`, boş `blockers` listesi ve tüm safety flag değerlerinin `false` olması beklenir.
