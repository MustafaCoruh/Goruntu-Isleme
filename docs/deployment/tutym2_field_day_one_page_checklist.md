# T.UTYM#2 Saha Günü Tek Sayfa Kontrol Listesi

Bu kontrol listesi, T.UTYM#2 saha test günü operatör ve yetkili teknik kişi tarafından hızlıca takip edilmek için hazırlanmıştır.

Amaç:

```text
Saha testine başlamadan önce her şey hazır mı?
Güvenli raporlar üretildi mi?
Dashboard state üretildi ve doğrulandı mı?
Statik dashboard açılıp dashboard_state.json yüklendi mi?
Uyarılar ve kritikler not edildi mi?
```

Bu liste gerçek görüntü, video, RTSP URL, IP adresi, kullanıcı adı/parola veya tam lokal path paylaşımı gerektirmez.



## 0. Ana Runbook Bağlantısı

Bu tek sayfalık checklist hızlı saha kullanımı içindir. Tüm akışın detaylı ve sıralı anlatımı için önce şu dosya referans alınmalıdır:

```text
docs/deployment/tutym2_operator_master_runbook.md
```

## 1. PR / VS Code Kontrolü

| Kontrol | Durum |
| --- | --- |
| Son PR'lar GitHub'da merge edildi | `[ ] Evet` `[ ] Hayır` |
| VS Code sync/pull yapıldı | `[ ] Evet` `[ ] Hayır` |
| `app/ui/static/tutym2_dashboard.html` var | `[ ] Evet` `[ ] Hayır` |
| `app/dashboard_state.py` var | `[ ] Evet` `[ ] Hayır` |
| `app/dashboard_state_validator.py` var | `[ ] Evet` `[ ] Hayır` |
| `scripts/build_tutym2_dashboard_state.py` var | `[ ] Evet` `[ ] Hayır` |
| `scripts/validate_tutym2_dashboard_state.py` var | `[ ] Evet` `[ ] Hayır` |

## 2. Lokal Saha Klasörleri

| Klasör | Durum |
| --- | --- |
| `C:\FTMC_FIELD_DATA\configs\` var | `[ ] Evet` `[ ] Hayır` |
| `C:\FTMC_FIELD_DATA\inputs\` var | `[ ] Evet` `[ ] Hayır` |
| `C:\FTMC_FIELD_DATA\models\` var | `[ ] Evet` `[ ] Hayır` |
| `C:\FTMC_FIELD_DATA\reports\` var | `[ ] Evet` `[ ] Hayır` |

Bu klasörler repo dışında olmalıdır.

## 3. Lokal Dosyalar

| Dosya | Durum |
| --- | --- |
| Lokal config dosyası hazır | `[ ] Evet` `[ ] Hayır` |
| Lokal RTSP config dosyası hazır | `[ ] Evet` `[ ] Hayır` |
| ONNX model dosyası lokal models klasöründe | `[ ] Evet` `[ ] Hayır` |
| Gerçek görüntü/video repo içinde değil | `[ ] Evet` `[ ] Hayır` |
| Gerçek RTSP URL repo içinde değil | `[ ] Evet` `[ ] Hayır` |

## 4. Güvenli Rapor Üretim Sırası

Yetkili teknik kişi sırayla şu çıktıları üretmelidir.

| Sıra | Rapor | Beklenen dosya | Durum |
| --- | --- | --- | --- |
| 1 | Offline readiness | `offline_readiness.json` | `[ ] Üretildi` `[ ] Üretilmedi` |
| 2 | Config doğrulama özeti | `config_validation_summary.json` | `[ ] Üretildi` `[ ] Üretilmedi` |
| 3 | RTSP bağlantı testi | `rtsp_connection_test.json` | `[ ] Üretildi` `[ ] Üretilmedi` |
| 4 | Masa doğruluk raporu | `tutym2_table_accuracy_report.json` | `[ ] Üretildi` `[ ] Gerekli değil` `[ ] Üretilmedi` |
| 5 | Dashboard state | `dashboard_state.json` | `[ ] Üretildi` `[ ] Üretilmedi` |

## 5. Dashboard State Kontrolü

| Kontrol | Beklenen | Durum |
| --- | --- | --- |
| `dashboard_state.json` var | Evet | `[ ] Evet` `[ ] Hayır` |
| Dashboard state validator çalıştı | Evet | `[ ] Evet` `[ ] Hayır` |
| Validator sonucu `valid` | Evet | `[ ] Evet` `[ ] Hayır` |
| Safety alanlarının tamamı false | Evet | `[ ] Evet` `[ ] Hayır` |
| 14 masa kartı var | Evet | `[ ] Evet` `[ ] Hayır` |

Validator geçmeden dashboard sonucuna güvenilmemelidir.

## 6. Statik Dashboard Kontrolü

| Kontrol | Durum |
| --- | --- |
| `app/ui/static/tutym2_dashboard.html` açıldı | `[ ] Evet` `[ ] Hayır` |
| `dashboard_state.json` dashboard'a yüklendi | `[ ] Evet` `[ ] Hayır` |
| Genel durum görüldü | `[ ] Evet` `[ ] Hayır` |
| Bağlantı durumu görüldü | `[ ] Evet` `[ ] Hayır` |
| FPS görüldü | `[ ] Evet` `[ ] Hayır` |
| 14 masa kartı görüldü | `[ ] Evet` `[ ] Hayır` |
| Uyarılar okundu | `[ ] Evet` `[ ] Hayır` |
| Kritikler okundu | `[ ] Evet` `[ ] Hayır` |

## 7. Hızlı Karar

| Dashboard sonucu | Karar |
| --- | --- |
| `overall_status = normal` | Teste devam edilebilir |
| `overall_status = warning` | Uyarılar okunmalı, teknik kişi değerlendirmeli |
| `overall_status = critical` | Canlı teste devam edilmemeli |
| `overall_status = not_ready` | Önce eksik raporlar üretilmeli |

Seçilen karar:

```text
[ ] Devam
[ ] Uyarıyla devam
[ ] Durdur
[ ] Eksik hazırlık var
```

## 8. Paylaşılabilir Güvenli Özet

Aşağıdaki bilgiler görüntü veya RTSP paylaşmadan iletilebilir:

```text
UTYM: T.UTYM#2
overall_status: ...
connection_status: ...
average_fps: ...
table_summary.total: 14
table_summary.occupied: ...
table_summary.empty: ...
table_summary.unknown: ...
table_summary.no_data: ...
warnings count: ...
criticals count: ...
safety flags all false: Evet/Hayır
Son karar: Devam / Uyarıyla devam / Durdur / Eksik hazırlık var
```

## 9. Kesinlikle Paylaşılmayacaklar

```text
Gerçek görüntü
Gerçek video
RTSP URL
Kamera IP adresi
Kamera kullanıcı adı/parolası
Tam lokal path
Kişi adı
Yüz görüntüsü
```

## 10. Saha Günü Son Not

Eğer herhangi bir adımda emin olunmazsa canlı teste geçilmemelidir.

Öncelik sırası:

```text
Güvenlik > Doğruluk > Hız > Görsellik
```

## 11. Saha Sonu Teslim Özeti

Saha günü sonunda birden fazla güvenli rapor oluştuysa tek bir paylaşılabilir özet üretmek için şu dokümana bakılmalıdır:

```text
docs/deployment/tutym2_field_handoff_summary.md
```

İlgili script:

```text
scripts/build_tutym2_field_handoff_summary.py
```

Bu özet; RTSP URL, kamera IP, credential, gerçek görüntü/video veya tam lokal path paylaşmadan gün sonu durumunu tek JSON içinde toplamak için kullanılır.
