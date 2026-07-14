# T.UTYM#2 Operatör Dashboard İlk Tasarım Dokümanı

Bu doküman, T.UTYM#2 görüntü işleme sisteminin ürünleşme aşamasında operatöre nasıl bir ekran sunması gerektiğini tarif eder.

Amaç:

```text
Operatör kod veya terminal bilmeden sistemi anlayabilsin.
UTYM ve kamera durumunu görebilsin.
14 masanın dolu/boş durumunu tek ekranda izleyebilsin.
RTSP bağlantı, FPS, config ve model durumunu anlayabilsin.
Hata varsa ne yapacağını görebilsin.
Güvenli rapor indirebilsin.
```

Bu doküman tasarım dokümanıdır; gerçek görüntü, RTSP URL, IP adresi, kullanıcı adı/parola veya kişisel veri içermez.

## 1. Dashboard'un İlk Hedefi

İlk dashboard karmaşık olmamalıdır.

İlk hedef:

```text
Bir operatör T.UTYM#2 seçer.
Kamera durumunu görür.
14 masa durumunu görür.
Sistem sağlıklı mı, değil mi anlar.
Güvenli rapor alır.
```

Yüz tanıma, kişi ismi, uçuş testi entegrasyonu ve geçmiş analiz daha sonraki aşamalardır.

## 2. Ana Ekran Bölümleri

Önerilen ilk ekran bölümleri:

| Bölüm | Amaç |
| --- | --- |
| Üst durum çubuğu | UTYM, kamera, bağlantı ve genel sistem durumu |
| Masa durum paneli | 14 masanın dolu/boş/belirsiz durumu |
| Kamera sağlık paneli | RTSP bağlantı, FPS, çözünürlük, son frame zamanı |
| Config/model paneli | Config doğrulama, model varlığı, model versiyonu |
| Uyarılar paneli | Operatörün aksiyon alması gereken konular |
| Rapor paneli | Güvenli rapor üretme/indirme |

## 3. Üst Durum Çubuğu

Üst çubukta şu bilgiler görünmelidir:

```text
UTYM: T.UTYM#2
Kamera: TUTYM2-CAM-001
Bağlantı: Bağlı / Kopuk / Test edilmedi
Mod: Lokal Video / RTSP Canlı / Bağlantı Testi
Genel Durum: Normal / Uyarı / Kritik
Son Güncelleme: YYYY-MM-DD HH:MM:SS
```

Renk önerisi:

| Durum | Renk |
| --- | --- |
| Normal | Yeşil |
| Uyarı | Sarı |
| Kritik | Kırmızı |
| Test edilmedi | Gri |

## 4. Masa Durum Paneli

T.UTYM#2 için 14 masa gösterilmelidir.

Her masa kartında şu bilgiler olmalıdır:

```text
Masa ID
Durum: Dolu / Boş / Belirsiz
Güven skoru
Son karar zamanı
Uyarı işareti varsa nedeni
```

Örnek kart:

```text
Masa 01
Durum: Dolu
Güven: 0.91
Son karar: 14:32:10
```

Durum renkleri:

| Durum | Renk |
| --- | --- |
| Dolu | Kırmızı veya koyu turuncu |
| Boş | Yeşil |
| Belirsiz | Sarı |
| Veri yok | Gri |

## 5. Masa Durumu Sayısal Özet

Masa panelinin üstünde kısa özet olmalıdır:

```text
Toplam masa: 14
Dolu: ...
Boş: ...
Belirsiz: ...
Veri yok: ...
```

Bu özet operatörün genel tabloyu hızlı anlamasını sağlar.

## 6. Kamera Sağlık Paneli

Kamera panelinde şu bilgiler olmalıdır:

```text
RTSP bağlantı durumu
Son bağlantı testi sonucu
frames_read / requested_frames
Çözünürlük
Ortalama FPS
Son başarılı frame zamanı
```

Örnek:

```text
Bağlantı: Bağlı
Çözünürlük: 1920x1080
FPS: 8.3
Son frame: 14:32:11
```

Eğer FPS düşükse dashboard açık uyarı vermelidir:

```text
FPS düşük. Kamera stream profili, ağ veya GPU kullanımı kontrol edilmeli.
```

## 7. Config ve Model Paneli

Bu panel operatör hatalarını azaltmak için önemlidir.

Gösterilecek bilgiler:

```text
Config doğrulama: Geçti / Uyarı / Hata
Masa sayısı: 14/14
Çözünürlük: 1920x1080
Model dosyası: Var / Yok
Model versiyonu: ...
Offline readiness: pass / warn / fail
```

Config hatası varsa örnek mesaj:

```text
Config içinde 14 masa bekleniyor, 13 masa bulundu. Canlı teste geçmeyin.
```

Model hatası varsa örnek mesaj:

```text
Model dosyası bulunamadı. C:\FTMC_FIELD_DATA\models klasörü kontrol edilmeli.
```

Dashboard gerçek lokal path'i rapora yazmamalıdır; operatöre ekranda kontrollü uyarı gösterebilir.

## 8. Uyarılar Paneli

Uyarılar paneli operatörün ne yapacağını anlatmalıdır.

Örnek uyarılar:

| Uyarı | Operatör aksiyonu |
| --- | --- |
| RTSP bağlantısı yok | Ağ, kamera ve yetki bilgileri lokal kontrol edilmeli |
| FPS düşük | Stream profili veya GPU kullanımı kontrol edilmeli |
| Config geçersiz | Config validator sonucu incelenmeli |
| Model yok | Model dosyası lokal models klasörüne koyulmalı |
| Masa belirsiz | Kalibrasyon veya kamera açısı kontrol edilmeli |
| Rapor güvenli değil | Rapor paylaşılmamalı, teknik kişi bilgilendirilmeli |

## 9. Rapor Paneli

Dashboard güvenli raporlar üretmelidir.

İlk aşamada desteklenecek raporlar:

```text
Offline readiness raporu
RTSP bağlantı raporu
Config doğrulama özeti
Masa doğruluk raporu
Canlı demo özet raporu
```

Raporlarda olmaması gerekenler:

```text
Gerçek görüntü
Gerçek video
RTSP URL
Kamera IP adresi
Kullanıcı adı/parola
Kişi adı
Yüz görüntüsü
Tam lokal path
```

## 10. Operatör İçin Ana Butonlar

İlk dashboard için önerilen butonlar:

```text
Offline Hazırlık Kontrolü Çalıştır
Config Doğrula
RTSP Bağlantı Testi Çalıştır
Lokal Foto/Video Demo Başlat
Canlı RTSP Demo Başlat
Güvenli Rapor Oluştur
```

Her butonun yanında kısa açıklama olmalıdır.

Örnek:

```text
Config Doğrula
Seçili config dosyasında 14 masa, çözünürlük ve polygon değerleri doğru mu kontrol eder.
```

## 11. Hata Mesajı Tasarım İlkeleri

Hata mesajları teknik olmayan operatör için anlaşılır olmalıdır.

Kötü mesaj:

```text
ValidationError: invalid polygon
```

İyi mesaj:

```text
Masa 05 polygon noktası görüntü sınırları dışında. Kalibrasyonu tekrar kontrol edin.
```

Her hata mesajı şu üç parçayı içermelidir:

```text
Ne oldu?
Neden önemli?
Ne yapmalıyım?
```

## 12. İlk Dashboard Veri Kaynakları

Dashboard ilk aşamada şu mevcut araçların güvenli çıktılarından beslenebilir:

| Veri | Kaynak |
| --- | --- |
| Offline readiness | `app/offline_readiness.py` |
| Config doğrulama | `app/tutym2_config_validator.py` |
| RTSP bağlantı raporu | `app/rtsp_field_demo.py` |
| Masa doğruluk raporu | `app/table_accuracy_report.py` |
| Kalibrasyon config | Lokal config JSON |

Bu yaklaşım dashboard'u doğrudan gerçek görüntüye veya RTSP URL'ye bağımlı yapmadan güvenli şekilde başlatır.

## 13. İlk Ürün Dashboard Wireframe

Metinsel ilk wireframe:

```text
+--------------------------------------------------------------------------------+
| T.UTYM#2 | Kamera: TUTYM2-CAM-001 | Bağlantı: Bağlı | FPS: 8.3 | Durum: Normal |
+--------------------------------------------------------------------------------+
| Dolu: 6 | Boş: 7 | Belirsiz: 1 | Veri yok: 0                              |
+--------------------------------------------------------------------------------+
| [Masa 01 Dolu 0.91] [Masa 02 Boş 0.88] [Masa 03 Belirsiz 0.42]               |
| [Masa 04 Boş 0.93]  [Masa 05 Dolu 0.86] ...                                  |
+--------------------------------------------------------------------------------+
| Kamera Sağlığı              | Config/Model Durumu                             |
| RTSP: Bağlı                 | Config: Geçti                                  |
| Çözünürlük: 1920x1080       | Masa: 14/14                                    |
| Son frame: 14:32:11         | Model: Var                                     |
+--------------------------------------------------------------------------------+
| Uyarılar                                                                       |
| - Masa 03 belirsiz. Kalibrasyon veya görüş açısı kontrol edilebilir.           |
+--------------------------------------------------------------------------------+
| [Offline Kontrol] [Config Doğrula] [RTSP Test] [Canlı Demo] [Rapor Oluştur]    |
+--------------------------------------------------------------------------------+
```

## 14. Ürünleşme İçin Dashboard Aşamaları

| Aşama | İçerik |
| --- | --- |
| Dashboard 0 | Sadece statik tasarım ve veri alanları |
| Dashboard 1 | Güvenli JSON raporlarını okuyup gösterme |
| Dashboard 2 | Lokal demo/RTSP runner butonları |
| Dashboard 3 | Çoklu kamera desteği |
| Dashboard 4 | Çoklu UTYM seçimi |
| Dashboard 5 | Harici uçuş testi/katılımcı entegrasyonu |

## 15. Sonraki Teknik Adım

Bu dokümandan sonra sıradaki teknik adım dashboard veri sözleşmesini hazırlamaktır.

Veri sözleşmesi şunları tanımlar:

```text
Dashboard hangi JSON dosyalarını okuyacak?
Hangi alanları bekleyecek?
Eksik alan olursa ne yapacak?
Durum renklerini hangi değerlere göre belirleyecek?
Uyarıları nasıl üretecek?
```

Bu sözleşme hazır olmadan doğrudan UI koduna geçmek önerilmez.
