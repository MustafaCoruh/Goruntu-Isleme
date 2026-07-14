# T.UTYM#2 Operatör Hata ve Çözüm Rehberi

Bu rehber, T.UTYM#2 saha akışında operatörün veya yetkili teknik kişinin görebileceği tipik hata/uyarı durumlarını açıklar.

Amaç:

```text
Hata görüldüğünde panik yapmadan:
1. Bu ne demek?
2. Devam edebilir miyim?
3. Kime ne bilgi vermeliyim?
4. Hassas veri paylaşmadan nasıl raporlarım?
```

## 1. Genel Güvenlik Kuralı

Hata çözmeye çalışırken bile aşağıdaki bilgiler paylaşılmamalıdır:

```text
Gerçek RTSP URL
Kamera IP adresi
Kamera kullanıcı adı/parolası
Gerçek görüntü/video
Tam lokal path
Katılımcı/yüz/kimlik bilgisi
```

Teknik kişiye bilgi verirken sadece güvenli özet paylaşılmalıdır:

```text
Hata tipi
Script adı
Rapor dosya adı
overall_status
safe_to_share değeri
Eksik dosya kategorisi
```

## 2. Hızlı Hata Karar Tablosu

| Belirti | Muhtemel anlam | Devam edilir mi? | Aksiyon |
| --- | --- | --- | --- |
| Dosya bulunamadı | Sync/pull eksik veya lokal dosya yanlış yerde | Hayır | Dosya ağacı/lokal klasör kontrol edilir |
| Model bulunamadı | ONNX model lokal klasörde yok | Hayır | Model yetkili kişi tarafından lokal models klasörüne konur |
| Config invalid | Masa, çözünürlük veya polygon hatalı | Hayır | Config yeniden kalibre edilir/doğrulanır |
| RTSP placeholder kaldı | Gerçek lokal RTSP config hazırlanmadı | Hayır | Lokal RTSP config yetkili kişi tarafından hazırlanır |
| RTSP frame okunamadı | Kamera/network/credential problemi olabilir | Hayır | RTSP bağlantısı teknik kişiyle kontrol edilir |
| Dashboard state invalid | Dashboard'a yüklenecek JSON güvenilir değil | Hayır | Dashboard state yeniden üretilir/validate edilir |
| `safe_to_share=false` | Rapor paylaşım için güvenli değil | Hayır | Rapor paylaşılmaz, teknik kişi inceler |
| `overall_status=critical` | Kritik hata var | Hayır | Canlı/demo kararında kullanılmaz |
| `overall_status=warning` | Uyarı var | Koşullu | Teknik kişi onayı gerekir |
| `libGL.so.1` hatası | Ortamda OpenCV sistem bağımlılığı eksik | Hayır | Kurulum paketi/BT bağımlılık kontrolü yapılır |

## 3. `file was not found` / Dosya Bulunamadı

Anlamı:

```text
Scriptin beklediği dosya verilen konumda yok.
```

Sık nedenler:

- PR merge edilmemiştir.
- VS Code sync/pull yapılmamıştır.
- Lokal saha klasörü oluşturulmamıştır.
- Dosya repo içinde değil, lokal klasörde olmalıdır ama oluşturulmamıştır.
- Dosya adı yanlış yazılmıştır.

Operatör ne yapmalı?

```text
1. VS Code dosya ağacında repo dosyası var mı kontrol et.
2. Lokal saha klasöründe beklenen dosya var mı kontrol et.
3. Dosya gerçek saha verisi içeriyorsa chat/GitHub'a yükleme.
4. Teknik kişiye sadece dosya kategorisini söyle.
```

Paylaşılabilir örnek:

```text
config_file bulunamadı.
Beklenen kategori: lokal config.
Gerçek path paylaşılmadı.
```

## 4. Model Dosyası Yok

Anlamı:

```text
Algılama için gerekli ONNX model dosyası lokal models klasöründe bulunamadı.
```

Devam edilir mi?

```text
Hayır. Model olmadan gerçek demo sonucu güvenilir değildir.
```

Operatör ne yapmalı?

- `models/README.md` dosyasına bakmalı.
- Modelin repo dışında, lokal saha klasöründe olması gerektiğini bilmelidir.
- Model dosyasını chat'e veya GitHub'a yüklememelidir.

Teknik kişiye güvenli bilgi:

```text
Model file check failed.
Beklenen dosya kategorisi: local_model.
```

## 5. Config Validation Hatası

Anlamı:

```text
Kamera/config dosyası T.UTYM#2 beklenen yapısına uymuyor.
```

Sık nedenler:

```text
site yanlış
camera_id yanlış
14 masa yok
çözünürlük 1920x1080 değil
polygon koordinatları görüntü sınırı dışında
masa id formatı tutarsız
```

Devam edilir mi?

```text
Hayır. Config doğrulanmadan demo veya dashboard kararına geçilmemelidir.
```

Çözüm:

- Kalibrasyon tekrar yapılır.
- Lokal config dosyası yeniden oluşturulur.
- `scripts/validate_tutym2_config.py` tekrar çalıştırılır.

## 6. RTSP Placeholder Kalmış

Anlamı:

```text
RTSP config hâlâ template/placeholder değeri içeriyor.
```

Devam edilir mi?

```text
Hayır. Canlı kameraya bağlanılamaz.
```

Önemli güvenlik notu:

```text
Gerçek RTSP URL sadece lokal RTSP config kopyasına yazılır.
Repo'ya, PR'a veya chat'e yazılmaz.
```

Operatör teknik kişiye sadece şunu söylemelidir:

```text
RTSP config placeholder kontrolü geçmedi.
Gerçek RTSP değeri paylaşılmadı.
```

## 7. RTSP Frame Okunamadı

Anlamı:

```text
Kamera bağlantısı var gibi görünse bile frame alınamamış olabilir.
```

Sık nedenler:

```text
Kamera erişim yetkisi yok
Network erişimi yok
RTSP credential yanlış
Kamera stream formatı uyumsuz
Kamera kapalı veya erişilemez
```

Devam edilir mi?

```text
Hayır. Canlı demo sonucuna güvenilmez.
```

Güvenli paylaşım örneği:

```text
RTSP connection test failed.
connection_test_frames = 5
frames_read = 0
RTSP URL/IP paylaşılmadı.
```

## 8. Dashboard State Validation Hatası

Anlamı:

```text
dashboard_state.json statik dashboard'a güvenli şekilde yüklenmeye hazır değil.
```

Sık nedenler:

```text
site yanlış
camera_id yanlış
14 table card yok
safety flag true
status alanı beklenmeyen değer içeriyor
```

Devam edilir mi?

```text
Hayır. Dashboard üzerinden karar verilmemelidir.
```

Çözüm:

- Dashboard state yeniden üretilir.
- `scripts/validate_tutym2_dashboard_state.py` tekrar çalıştırılır.
- Hata devam ederse teknik kişi inceler.

## 9. `safe_to_share=false`

Anlamı:

```text
Rapor paylaşım için güvenli kabul edilmemiştir.
```

Devam edilir mi?

```text
Rapor paylaşılmaz. Demo/analiz için teknik kişi incelemesi gerekir.
```

Operatörün yapmaması gerekenler:

```text
Raporu chat'e atma
GitHub'a ekleme
E-posta ile dağıtma
Ekran görüntüsüyle paylaşma
```

Paylaşılabilir güvenli cümle:

```text
Rapor safe_to_share=false döndü. Hassas içerik riski nedeniyle paylaşılmadı.
```

## 10. `overall_status=critical`

Anlamı:

```text
Sistemin ilgili adımı kritik hata durumunda.
```

Devam edilir mi?

```text
Hayır. Kritik durum canlı karar veya kabul için kullanılamaz.
```

Aksiyon:

- Hangi raporun critical verdiği bulunur.
- İlgili validator/komut tekrar kontrol edilir.
- Teknik kişi onayı olmadan saha kabulüne geçilmez.

## 11. `overall_status=warning`

Anlamı:

```text
Sistem tamamen başarısız değil ama eksik veya şüpheli bir durum var.
```

Devam edilir mi?

```text
Sadece teknik kişi onayıyla.
```

Örnek:

```text
Opsiyonel modül eksik olabilir.
RTSP FPS düşük olabilir.
Table accuracy beklenen eşiğin altında olabilir.
```

## 12. `libGL.so.1` / `cv2 import failed`

Anlamı:

```text
OpenCV kurulmuş olabilir ama işletim sisteminde gerekli grafik/sistem kütüphanesi eksiktir.
```

Bu durum özellikle test veya görüntü işleme modülleri import edilirken görülebilir.

Devam edilir mi?

```text
Hayır. Görüntü işleme akışı doğru çalışmayabilir.
```

Çözüm:

- Offline kurulum paketi bağımlılıkları kontrol edilir.
- BT/geliştirme sorumlusu OpenCV sistem bağımlılıklarını ekler.
- Offline readiness tekrar çalıştırılır.

Operatörün paylaşabileceği güvenli bilgi:

```text
cv2 import failed.
Eksik sistem bağımlılığı: libGL.so.1
Gerçek görüntü veya path paylaşılmadı.
```

## 13. JSON Format Hatası

Anlamı:

```text
Rapor veya config JSON olarak okunamıyor.
```

Sık nedenler:

```text
Virgül eksik/fazla
Tırnak hatası
Dosya yarım kaydedilmiş
Yanlış dosya seçilmiş
```

Devam edilir mi?

```text
Hayır. Dosya düzeltilmeden validator veya dashboard kullanılmamalıdır.
```

## 14. Operatörün Teknik Kişiye Vereceği Güvenli Bilgi Formatı

Şu format önerilir:

```text
Script: <script adı>
Adım: <readiness/config/rtsp/dashboard/handoff>
Güvenli durum: <pass/warning/critical/fail>
Rapor dosya adı: <sadece dosya adı>
Hassas veri paylaşıldı mı: Hayır
Kısa hata: <hata mesajının hassas veri içermeyen özeti>
```

Örnek:

```text
Script: validate_tutym2_dashboard_state.py
Adım: dashboard validation
Güvenli durum: critical
Rapor dosya adı: dashboard_state.json
Hassas veri paylaşıldı mı: Hayır
Kısa hata: 14 table card beklenirken eksik kayıt var.
```

## 15. Ana Doküman Bağlantıları

Detaylı akış:

```text
docs/deployment/tutym2_operator_master_runbook.md
```

Komut kataloğu:

```text
docs/deployment/tutym2_operator_command_catalog.md
```

Saha günü tek sayfa checklist:

```text
docs/deployment/tutym2_field_day_one_page_checklist.md
```
