# Paylaşılamayan Gerçek UTYM Verisiyle Çalışma Akışı

Bu doküman, T.UTYM#2 gerçek kamera görüntüleri veya videoları repository'ye eklenemediğinde izlenecek güvenli geliştirme ve doğrulama akışını tanımlar.

## 1. Temel İlke

Gerçek T.UTYM#2 görüntüleri, videoları ve kamera bağlantı bilgileri repository'ye eklenmez; asistanla veya dış ortamla paylaşılmaz. Repository yalnızca kod, sentetik test verisi, dokümantasyon, config şablonları ve güvenli örnek dosyalar içerir.

## 2. Lokal Saha Akışı

1. Kod ve bağımlılıklar Windows saha makinesine offline yöntemle aktarılır.
2. Gerçek IP video kaynağına yalnızca saha makinesi üzerinden erişilir.
3. Kalibrasyon, gerçek görüntü dışarı çıkarılmadan lokal arayüzde yapılır.
4. Oluşturulan masa poligon config dosyası hassas kabul edilir; kamera görüntüsü içermese bile tesis düzenini yansıtabileceği için kontrollü paylaşılır.
5. Test sonuçları görüntü içermeyen metrikler olarak raporlanır.

## 3. Repository'de Tutulabilecek Güvenli Çıktılar

Aşağıdaki çıktılar görüntü içermediği sürece repository'de tutulabilir:

- Masa sayısı, sandalye sayısı ve işletim sistemi gibi gereksinim bilgileri.
- Sentetik veya çizim tabanlı örnek görüntüler.
- Gerçek kamera görüntüsü içermeyen JSON config şablonları.
- Görüntü içermeyen doğrulama metrikleri.
- Hata türleri ve sayısal performans raporları.

## 4. Repository'de Tutulmaması Gereken Veriler

Aşağıdakiler repository'ye eklenmemelidir:

- Gerçek kamera görüntüleri.
- Gerçek kamera videoları.
- RTSP URL, kullanıcı adı, parola veya IP adresi gibi bağlantı sırları.
- Kişileri tanımlayabilecek kimlik bilgileri.
- Yüz, badge, ekran, belge veya hassas operasyon görüntüsü içeren dosyalar.

## 5. Saha Doğrulama Raporu Formatı

Gerçek görüntü paylaşmadan şu metrikler raporlanabilir:

| Metrik | Açıklama |
| --- | --- |
| Test edilen kare/video sayısı | Gerçek dosya adı verilmeden adet bazlı yazılır |
| Masa bazlı doğruluk | Doğru masa kararları / toplam masa kararları |
| False occupied | Boş masayı dolu gösterme oranı |
| False empty | Dolu masayı boş gösterme oranı |
| Belirsiz karar oranı | `uncertain` kararlarının oranı |
| Ortalama inference süresi | Frame başına ms |
| FPS | Saniye başına işlenen kare |
| CPU/RAM/GPU | Hedef Windows makinedeki kaynak kullanımı |

## 6. Önerilen Sonraki Uygulama Adımları

1. Windows için offline kurulum paketini doğrula.
2. `opencv-python-headless` ve GUI gereksinimini ayır.
3. Gerçek ONNX person detector modelini saha makinesinde konumlandır.
4. T.UTYM#2 için 14 masa poligonunu lokal kalibrasyon ekranından oluştur.
5. Gerçek IP video üzerinde görüntü paylaşmadan doğrulama metriklerini çıkar.
