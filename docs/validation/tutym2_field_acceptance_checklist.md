# T.UTYM#2 Saha Kabul Kontrol Listesi

Bu kontrol listesi, T.UTYM#2 için ilk saha demosuna geçmeden önce her şeyin hazır olup olmadığını güvenli ve adım adım kontrol etmek için hazırlanmıştır.

Amaç şudur:

```text
Kod hazır mı?
Config hazır mı?
Model lokal makinede mi?
RTSP bağlantısı çalışıyor mu?
14 masa doğru tanımlandı mı?
Gerçek görüntü, RTSP URL veya gizli bilgi repo'ya girmedi mi?
Canlı demo testine geçebilir miyiz?
```

Bu dosya gerçek görüntü, video, IP adresi, RTSP URL, kullanıcı adı veya parola içermez.

## 1. Genel Durum

| Kontrol | Beklenen | Durum |
| --- | --- | --- |
| UTYM adı/kodu belli mi? | `T.UTYM#2` | `[ ] Tamam` `[ ] Eksik` |
| İşletim sistemi belli mi? | Windows | `[ ] Tamam` `[ ] Eksik` |
| Kamera tipi belli mi? | IP video / RTSP | `[ ] Tamam` `[ ] Eksik` |
| Çözünürlük belli mi? | 1920x1080 | `[ ] Tamam` `[ ] Eksik` |
| Masa sayısı belli mi? | 14 | `[ ] Tamam` `[ ] Eksik` |
| Her masada sandalye sayısı belli mi? | 1 | `[ ] Tamam` `[ ] Eksik` |

Bu bölüm tamamlanmadan teknik teste geçilmemelidir.

## 2. Repo İçinde Bulunması Gereken Dosyalar

Aşağıdaki dosyaların VS Code içinde göründüğünü kontrol edin.

| Dosya | Ne işe yarar? | Durum |
| --- | --- | --- |
| `app/field_demo.py` | Lokal foto/video demo runner | `[ ] Var` `[ ] Yok` |
| `app/rtsp_field_demo.py` | RTSP canlı/bağlantı testi runner | `[ ] Var` `[ ] Yok` |
| `scripts/run_tutym2_local_demo.py` | Lokal demo kısa çalıştırma scripti | `[ ] Var` `[ ] Yok` |
| `scripts/run_tutym2_rtsp_demo.py` | RTSP demo kısa çalıştırma scripti | `[ ] Var` `[ ] Yok` |
| `configs/templates/tutym2_cam_001.template.json` | 14 masalı lokal config şablonu | `[ ] Var` `[ ] Yok` |
| `configs/templates/tutym2_cam_001.rtsp.template.json` | RTSP config şablonu | `[ ] Var` `[ ] Yok` |
| `docs/deployment/tutym2_rtsp_operator_guide.md` | RTSP operatör kılavuzu | `[ ] Var` `[ ] Yok` |
| `docs/deployment/tutym2_rtsp_connection_report_guide.md` | RTSP bağlantı raporu okuma kılavuzu | `[ ] Var` `[ ] Yok` |
| `docs/deployment/tutym2_calibration_operator_guide.md` | Kalibrasyon operatör kılavuzu | `[ ] Var` `[ ] Yok` |
| `models/README.md` | Model dosyası yerleşim açıklaması | `[ ] Var` `[ ] Yok` |

Bu dosyalardan biri eksikse önce PR merge/pull süreci kontrol edilmelidir.

## 3. Repo İçinde Bulunmaması Gereken Hassas Veriler

Aşağıdaki bilgiler repo içinde kesinlikle bulunmamalıdır.

| Hassas veri | Repo içinde olabilir mi? | Durum |
| --- | --- | --- |
| Gerçek kamera görüntüsü | Hayır | `[ ] Yok` `[ ] Var - Temizlenmeli` |
| Gerçek video kaydı | Hayır | `[ ] Yok` `[ ] Var - Temizlenmeli` |
| Gerçek RTSP URL | Hayır | `[ ] Yok` `[ ] Var - Temizlenmeli` |
| Kamera IP adresi | Hayır | `[ ] Yok` `[ ] Var - Temizlenmeli` |
| Kullanıcı adı/parola | Hayır | `[ ] Yok` `[ ] Var - Temizlenmeli` |
| Gerçek model binary dosyası | Hayır | `[ ] Yok` `[ ] Var - Temizlenmeli` |
| Lokal saha config dosyası | Hayır | `[ ] Yok` `[ ] Var - Temizlenmeli` |

Eğer bu tablodaki hassas verilerden biri repo içinde görülürse saha testine geçilmemelidir.

## 4. Lokal Saha Klasörleri Hazır mı?

Sahadaki veya kontrollü geliştirme bilgisayarındaki lokal klasörler şu mantıkta olmalıdır:

```text
C:\FTMC_FIELD_DATA\configs\
C:\FTMC_FIELD_DATA\inputs\
C:\FTMC_FIELD_DATA\models\
C:\FTMC_FIELD_DATA\reports\
```

| Klasör | İçerik | Durum |
| --- | --- | --- |
| `configs` | Lokal `.local.json` config dosyaları | `[ ] Hazır` `[ ] Eksik` |
| `inputs` | Lokal test foto/video dosyaları | `[ ] Hazır` `[ ] Eksik` |
| `models` | Lokal ONNX model dosyası | `[ ] Hazır` `[ ] Eksik` |
| `reports` | Güvenli JSON test raporları | `[ ] Hazır` `[ ] Eksik` |

Bu klasörler repo dışında olmalıdır.

## 5. Kalibrasyon Kabul Kontrolü

Kalibrasyonun amacı kamera görüntüsü üzerinde 14 masanın bölgelerini doğru şekilde tanımlamaktır.

| Kontrol | Beklenen | Durum |
| --- | --- | --- |
| Kalibrasyon UI açılıyor mu? | Evet | `[ ] Evet` `[ ] Hayır` |
| Hedef masa sayısı 14 görünüyor mu? | Evet | `[ ] Evet` `[ ] Hayır` |
| 14 masa çizildi mi? | Evet | `[ ] Evet` `[ ] Hayır` |
| Her masa için kapasite 1 mi? | Evet | `[ ] Evet` `[ ] Hayır` |
| Masa ID'leri anlaşılır mı? | `table_01` ... `table_14` benzeri | `[ ] Evet` `[ ] Hayır` |
| İndirilen dosya lokal yerde mi tutuldu? | Evet | `[ ] Evet` `[ ] Hayır` |
| İndirilen config repo'ya eklenmedi mi? | Evet | `[ ] Evet` `[ ] Hayır` |

Kalibrasyon dosyasında gerçek RTSP URL veya gizli bilgi bulunmamalıdır.

## 6. Lokal Foto/Video Demo Kabul Kontrolü

Bu test gerçek RTSP canlı yayına geçmeden önce geçmiş fotoğraf veya video üzerinde yapılır.

| Kontrol | Beklenen | Durum |
| --- | --- | --- |
| Lokal config dosyası var mı? | Evet | `[ ] Evet` `[ ] Hayır` |
| Lokal test foto/video dosyası var mı? | Evet | `[ ] Evet` `[ ] Hayır` |
| Model dosyası lokal `models` klasöründe mi? | Evet | `[ ] Evet` `[ ] Hayır` |
| Demo runner hata vermeden başlıyor mu? | Evet | `[ ] Evet` `[ ] Hayır` |
| Güvenli rapor üretiliyor mu? | Evet | `[ ] Evet` `[ ] Hayır` |
| Raporda tam path/görüntü/RTSP URL yok mu? | Evet | `[ ] Evet` `[ ] Hayır` |

Bu test geçmeden canlı RTSP testine geçmek önerilmez.

## 7. RTSP Bağlantı Testi Kabul Kontrolü

RTSP bağlantı testinde amaç yalnızca kameradan frame okunabildiğini doğrulamaktır.

| Kontrol | Beklenen | Durum |
| --- | --- | --- |
| RTSP lokal config dosyası hazır mı? | Evet | `[ ] Evet` `[ ] Hayır` |
| RTSP config içinde placeholder kalmadı mı? | Evet | `[ ] Evet` `[ ] Hayır` |
| RTSP URL repo dışında mı tutuluyor? | Evet | `[ ] Evet` `[ ] Hayır` |
| `rtsp_connection_test.json` üretildi mi? | Evet | `[ ] Evet` `[ ] Hayır` |
| `status` değeri `connection_test_completed` mı? | Evet | `[ ] Evet` `[ ] Hayır` |
| `frames_read = requested_frames` mı? | Evet | `[ ] Evet` `[ ] Hayır` |
| Çözünürlük 1920x1080 mi? | Evet | `[ ] Evet` `[ ] Hayır` |
| `average_fps >= 5` mi? | Evet | `[ ] Evet` `[ ] Hayır` |

Bu bölüm geçerse canlı RTSP demo testine geçilebilir.

## 8. Canlı RTSP Demo Kabul Kontrolü

Bu aşama artık gerçek canlı kamera görüntüsüyle çalışır. Görüntü ve RTSP bilgileri paylaşılmaz.

| Kontrol | Beklenen | Durum |
| --- | --- | --- |
| Canlı demo runner başlıyor mu? | Evet | `[ ] Evet` `[ ] Hayır` |
| Program masalar için dolu/boş kararı üretiyor mu? | Evet | `[ ] Evet` `[ ] Hayır` |
| Karar üretilemeyen masa var mı? | Mümkünse hayır | `[ ] Yok` `[ ] Var` |
| FPS kabul edilebilir mi? | İlk hedef en az 5 FPS | `[ ] Evet` `[ ] Hayır` |
| Demo raporu güvenli mi? | Evet | `[ ] Evet` `[ ] Hayır` |
| Raporda görüntü/RTSP URL/IP/parola yok mu? | Evet | `[ ] Evet` `[ ] Hayır` |

Canlı demo sonucu kötü çıkarsa önce kalibrasyon, sonra kamera açısı/çözünürlük, sonra model performansı incelenmelidir.

## 9. İlk Kabul İçin Başarı Kriterleri

İlk saha kabulü için minimum kriterler:

```text
[ ] 14 masa config içinde tanımlı.
[ ] Her masanın kapasitesi 1.
[ ] Lokal foto/video demo çalışıyor.
[ ] RTSP bağlantı testi başarılı.
[ ] RTSP bağlantı raporunda URL/IP/parola yok.
[ ] Canlı RTSP demo başlıyor.
[ ] En az temel dolu/boş çıktısı alınabiliyor.
[ ] Güvenli rapor üretilebiliyor.
```

Bu maddeler tamamlanırsa sistem ilk saha prototipi için hazır kabul edilebilir.

## 10. Sorun Çıkarsa Karar Ağacı

```text
Demo başlamıyor
  -> Config/model/source yolu kontrol edilir.

RTSP bağlanmıyor
  -> RTSP URL, ağ erişimi, kamera yetkisi lokal olarak kontrol edilir.

Frame okunuyor ama çözünürlük yanlış
  -> Kamera stream profili kontrol edilir.

Masalar yanlış dolu/boş görünüyor
  -> Kalibrasyon polygonları kontrol edilir.

FPS düşük
  -> Kamera stream ayarı, GPU kullanımı, model boyutu ve çözünürlük kontrol edilir.

Rapor hassas bilgi içeriyor
  -> Rapor paylaşılmaz, kod/config temizlenir.
```

## 11. Paylaşılabilir Saha Özeti

Gerçek görüntü veya RTSP bilgisi paylaşmadan şu formatta özet verilebilir:

```text
UTYM: T.UTYM#2
Masa sayısı: 14
Kamera tipi: RTSP IP kamera
Çözünürlük: 1920x1080
Kalibrasyon: Tamam/Eksik
Lokal foto/video demo: Başarılı/Başarısız
RTSP bağlantı testi: Başarılı/Başarısız
frames_read/requested_frames: ... / ...
average_fps: ...
Canlı RTSP demo: Başarılı/Başarısız
Hassas veri paylaşılmadı: Evet
Sonraki karar: ...
```

## 12. Sonraki Teknik Aşama

Bu kontrol listesi tamamlandıktan sonra sıradaki teknik aşama model performansını ölçmektir.

Model performansında şu sorulara cevap aranır:

```text
Kişi algılama doğru mu?
Masa dolu/boş kararı doğru mu?
Yanlış dolu kararı var mı?
Yanlış boş kararı var mı?
Işık değişince sonuç bozuluyor mu?
Farklı oturma pozisyonlarında sonuç bozuluyor mu?
```

Bu aşama için ayrıca güvenli, görüntüsüz bir performans değerlendirme şablonu hazırlanmalıdır.
