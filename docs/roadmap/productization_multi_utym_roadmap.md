# Ürünleşme ve Çoklu UTYM Yaygınlaştırma Yol Haritası

Bu yol haritası, T.UTYM#2 prototipini zamanla operatör hatasına dayanıklı, ürün gibi kullanılabilir ve birden fazla UTYM'ye yayılabilir bir sisteme dönüştürmek için hazırlanmıştır.

Önemli ayrım:

```text
Prototip: Bir UTYM'de kontrollü şekilde çalıştığını kanıtlar.
Ürün: Farklı UTYM'lerde, farklı operatörlerle, hata durumlarında ve uzun süreli kullanımda güvenilir çalışır.
```

Bu doküman gerçek görüntü, RTSP URL, IP adresi, kullanıcı adı, parola veya saha config dosyası içermez.

## 1. Hedef Ürün Tanımı

Nihai hedef sistem şunu yapabilmelidir:

```text
Birden fazla UTYM tanımlanır.
Her UTYM'nin bir veya daha fazla kamerası olabilir.
Her kameranın masa bölgeleri kalibre edilir.
Sistem masaların dolu/boş durumunu canlı veya kayıtlı görüntüden çıkarır.
Operatör güvenli ekrandan durumu görür.
Sistem güvenli rapor üretir.
Hassas veri repo'ya veya yetkisiz ortama taşınmaz.
```

İleride yüz tanıma veya katılımcı eşleştirme istenirse bu ürün katmanı üzerine ayrıca güvenlik, hukuk, yetki ve kayıt politikası eklenmelidir.

## 2. Ürünleşme Aşamaları

| Aşama | Amaç | Çıktı |
| --- | --- | --- |
| Aşama 0 | Güvenli prototip altyapısı | Lokal/RTSP runner, template, kılavuzlar |
| Aşama 1 | T.UTYM#2 saha doğrulama | Kalibrasyon, bağlantı testi, ilk canlı demo |
| Aşama 2 | Model performans ölçümü | Masa bazlı doğruluk raporu |
| Aşama 3 | Operatör dayanıklılığı | Hata mesajları, kurulum kontrolü, güvenli UI |
| Aşama 4 | Çoklu UTYM mimarisi | UTYM/kamera/config kayıt yapısı |
| Aşama 5 | Ürün paketi | Offline kurulum, sürümleme, loglama, dokümantasyon |
| Aşama 6 | Kurumsal entegrasyon | Harici platformlardan uçuş testi/katılımcı verisi alma |

Şu an proje Aşama 0 ile Aşama 1 arasındadır.

## 3. Ürün Gibi Kullanılabilir Olmak Ne Demek?

Bir sistemin ürün gibi kullanılabilir olması için sadece çalışması yetmez.

Aşağıdakiler gerekir:

| Gereksinim | Açıklama |
| --- | --- |
| Kolay kurulum | Operatör veya teknik personel karmaşık komutlarla uğraşmamalı |
| Net hata mesajı | Hata olunca sebep ve aksiyon anlaşılmalı |
| Güvenli varsayılanlar | RTSP URL, görüntü ve model yanlışlıkla repo'ya girmemeli |
| Kalibrasyon yönetimi | Her UTYM/kamera için config takip edilebilmeli |
| Raporlama | Hassas veri içermeyen JSON/CSV raporları üretilebilmeli |
| Loglama | Sorun olduğunda ne olduğu anlaşılmalı |
| Sürümleme | Hangi model, hangi config, hangi kod sürümü kullanıldı bilinmeli |
| Offline çalışma | Program internetsiz ortamda çalışabilmeli |
| Çoklu kamera | UTYM'de birden fazla kamera desteklenebilmeli |
| Çoklu UTYM | Farklı UTYM'ler ayrı ayrı yönetilebilmeli |

## 4. Operatör Hatasına Dayanıklılık Gereksinimleri

Operatör yanlış dosya seçebilir, config'i eksik bırakabilir veya yanlış kamerayı çalıştırabilir. Sistem bunları yakalamalıdır.

| Risk | Sistem davranışı |
| --- | --- |
| Config dosyası yok | Çalışmayı durdur, net hata yaz |
| Model dosyası yok | Çalışmayı durdur, model klasörünü tarif et |
| RTSP URL placeholder kalmış | Canlı teste başlama |
| 14 masa yerine daha az masa var | Uyarı ver, eksik masa sayısını yaz |
| Masa kapasitesi yanlış | Uyarı ver |
| Rapor klasörü yok | Gerekirse oluştur veya net hata ver |
| Görüntü dosyası desteklenmiyor | Desteklenen uzantıları yaz |
| RTSP bağlantısı yok | URL/ağ/yetki kontrolü öner |
| FPS çok düşük | Stream/GPU/model önerisi ver |
| Rapor hassas bilgi içerebilir | Rapor üretimini güvenli sınırlarda tut |

Bu davranışlar ürünleşme sırasında otomatik preflight kontrollerine dönüştürülmelidir.

## 5. Çoklu UTYM İçin Önerilen Veri Modeli

İleride tek `T.UTYM#2` yerine birden fazla UTYM olacaksa sistemin kavramları ayrılmalıdır.

```text
Site / UTYM
  -> Camera
      -> Calibration config
      -> Stream config
      -> Table definitions
      -> Runtime reports
```

Örnek güvenli yapı:

```json
{
  "site_id": "TUTYM2",
  "site_name": "T.UTYM#2",
  "cameras": [
    {
      "camera_id": "TUTYM2-CAM-001",
      "resolution": {
        "width": 1920,
        "height": 1080
      },
      "table_count": 14,
      "config_name": "tutym2_cam_001.local.json"
    }
  ]
}
```

Bu örnek RTSP URL içermez. Gerçek stream bilgisi lokal ve kontrollü config dosyasında kalmalıdır.

## 6. Önerilen Repo Yapısı

Ürünleşme için zamanla şu yapıya geçilebilir:

```text
app/
  runners/
  services/
  ui/
  validation/
configs/
  templates/
docs/
  deployment/
  requirements/
  validation/
  roadmap/
models/
  README.md
scripts/
tests/
```

İleride büyüdükçe `app/field_demo.py` ve `app/rtsp_field_demo.py` içindeki bazı parçalar servis katmanına ayrılabilir.

## 7. Config Yönetimi Stratejisi

Config yönetimi ürünleşmenin en kritik konularından biridir.

| Config türü | Repo'da olabilir mi? | Açıklama |
| --- | --- | --- |
| Template config | Evet | Placeholder içerir, güvenlidir |
| Lokal saha config | Hayır | Gerçek kalibrasyon veya RTSP bilgisi içerebilir |
| RTSP URL config | Hayır | Gizli bilgi sayılır |
| Test fixture config | Evet | Sentetik ve anonim olmalı |
| Model config | Kısmen | Model adı/versiyon olabilir, binary olmaz |

Her config dosyasında mümkünse şu metadata olmalıdır:

```text
site_id
camera_id
resolution
table_count
created_at
created_by_role
config_version
notes
```

Kişisel veri veya gizli bağlantı bilgisi metadata içinde olmamalıdır.

## 8. Model Yönetimi Stratejisi

Model dosyaları büyük ve hassas olabileceği için repo'ya konmamalıdır.

Ürünleşme için model yönetiminde şunlar gerekir:

```text
Model dosya adı
Model versiyonu
Model hash/checksum
Beklenen input boyutu
Hedef donanım CPU/GPU
Performans notları
Geri dönüş planı
```

Örnek güvenli model kaydı:

```json
{
  "model_name": "person_detector.onnx",
  "model_version": "initial-field-test",
  "sha256": "LOCAL_ONLY_RECORDED_BY_OPERATOR",
  "target_runtime": "onnxruntime-gpu",
  "notes": "Model binary repo'ya eklenmez."
}
```

## 9. Raporlama Stratejisi

Raporlar ürünleşmede üç seviyeye ayrılmalıdır.

| Rapor | Amaç | Hassas veri içerir mi? |
| --- | --- | --- |
| Bağlantı raporu | RTSP bağlantısı/FPS/çözünürlük | Hayır |
| Demo raporu | Masa bazlı dolu/boş özet | Hayır |
| Performans raporu | Doğruluk/hata sayıları | Hayır |

Raporlarda olmaması gerekenler:

```text
RTSP URL
Kamera IP adresi
Kullanıcı adı/parola
Gerçek görüntü/video
Tam lokal path
Yüz görüntüsü
Kişisel veri
```

## 10. UI / Dashboard Yol Haritası

İlk ürün ekranı basit olmalıdır.

Minimum ekran:

```text
UTYM seçimi
Kamera seçimi
Masa listesi
Dolu/boş durumu
Son güncelleme zamanı
FPS/bağlantı durumu
Güvenli rapor indir
```

Daha sonra eklenebilecekler:

```text
Çoklu kamera görünümü
Geçmiş durum grafiği
Belirsiz karar uyarısı
Operatör notu
Config doğrulama ekranı
Model versiyon gösterimi
```

Yüz tanıma veya katılımcı eşleştirme UI'a eklenmeden önce ayrıca yetkilendirme ve veri saklama politikası hazırlanmalıdır.

## 11. Offline Kurulum Stratejisi

Programın çalışacağı ortamda internet olmayacağı için kurulum paketi önceden hazırlanmalıdır.

Offline pakette şunlar bulunmalıdır:

```text
Python runtime veya kurulum yönergesi
Gerekli Python paketleri / wheel dosyaları
Uygulama kodu
Model dosyası
Template config dosyaları
Operatör kılavuzları
Kurulum doğrulama scripti
```

Offline pakette şunlar bulunmamalıdır:

```text
Gerçek RTSP URL
Kamera parolası
Gerçek saha görüntüsü
Yetkisiz kişisel veri
```

## 12. Çoklu UTYM Yaygınlaştırma Planı

Çoklu UTYM'ye yayılmak için önerilen sıra:

```text
1. T.UTYM#2 prototipi doğrulanır.
2. T.UTYM#2 için minimum doğruluk hedefi belirlenir.
3. İkinci UTYM için sadece template/config çoğaltılır.
4. Her UTYM için ayrı kamera ve masa kalibrasyonu yapılır.
5. Ortak kod, farklı lokal config ile çalıştırılır.
6. Her UTYM için güvenli rapor formatı aynı kalır.
7. Dashboard çoklu UTYM seçecek hale getirilir.
```

Burada amaç kodu her UTYM için kopyalamak değil, aynı kodu farklı güvenli config dosyalarıyla çalıştırmaktır.

## 13. Entegrasyon Yol Haritası

İleride başka platformdan şu bilgi gelebilir:

```text
X hava aracı
Y uçuş testi
Planlanan katılımcılar
Gerçek katılım durumu
Oturma/masa bilgisi
```

Bu entegrasyon için önerilen aşamalar:

| Aşama | Açıklama |
| --- | --- |
| 1 | Görüntü işleme sistemi sadece masa dolu/boş üretir |
| 2 | Harici platform uçuş testi ve katılımcı listesini sağlar |
| 3 | Sistem masa doluluk bilgisini zaman damgası ile eşleştirir |
| 4 | Yetki varsa kişi/masa eşleştirme yapılır |
| 5 | Denetim ve raporlama katmanı eklenir |

Kişi tanıma veya yüz tanıma eklenmeden önce ayrıca açık hukuki ve kurumsal onay gerekir.

## 14. Başarı Metrikleri

Ürünleşme için takip edilecek metrikler:

```text
RTSP bağlantı başarı oranı
Ortalama FPS
Masa bazlı dolu/boş doğruluğu
Yanlış dolu sayısı
Yanlış boş sayısı
Belirsiz karar sayısı
Operatör müdahalesi gerektiren hata sayısı
Kurulum süresi
Config doğrulama hata sayısı
```

İlk hedefler:

```text
RTSP bağlantı testi: Başarılı
Canlı FPS: >= 5
Masa sayısı: 14/14 tanımlı
Güvenli rapor: Hassas veri yok
İlk doğruluk hedefi: Saha verisi sonrası belirlenecek
```

## 15. Önerilen Sonraki PR Sırası

Bu yol haritasından sonra önerilen küçük PR sırası:

```text
1. Model performans değerlendirme şablonu
2. Masa bazlı doğruluk raporu formatı
3. Config doğrulama kuralları dokümanı
4. Offline kurulum paketleme planı
5. Çoklu UTYM config registry taslağı
6. Operatör dashboard ilk tasarım dokümanı
```

Bu sıralama ürünleşmeye kontrollü şekilde gitmeyi sağlar.

## 16. Hazır Olma Tanımı

Sistem şu koşullarda ilk ürünleşme adayı sayılabilir:

```text
[ ] En az bir UTYM'de canlı demo çalıştı.
[ ] 14 masa için dolu/boş kararı üretildi.
[ ] RTSP bağlantısı stabil görüldü.
[ ] Güvenli raporlar üretildi.
[ ] Model performansı masa bazlı ölçüldü.
[ ] Operatör kurulum adımlarını takip edebildi.
[ ] Hata durumlarında sistem anlaşılır mesaj verdi.
[ ] Aynı kod başka UTYM için yeni config ile çalışabilecek hale geldi.
```

Bu maddeler tamamlandığında proje prototipten ürünleşme adayına geçer.
