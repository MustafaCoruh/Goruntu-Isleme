# UTYM-001 Doğrulama Raporu

**Tarih:** 2026-07-10  
**Kapsam:** Etiketli gerçek UTYM görüntüleri üzerinde masa doluluk başarımı ölçümü  
**Durum:** Gerçek, etiketli UTYM görüntüleri bu repoda bulunmadığı için nihai saha doğrulaması tamamlanamadı.

## 1. Veri seti durumu

Repoda `sample_data/utym_001` altında yalnızca sentetik ve anonimleştirilmiş SVG örnekleri bulunmaktadır. Aynı dizindeki video notu, güvenli gerçek kayıt hazır olana kadar ilk prototip veri setinin sentetik statik karelerden oluştuğunu belirtir. Bu nedenle bu rapordaki gerçek-görüntü metrikleri **ölçülemedi / N/A** olarak işaretlenmiştir.

Ek olarak `sample_data/validation` altında beklenen masa durumlarıyla eşleşen sentetik doğrulama seti bulunmaktadır. Bu set, gerçek UTYM görüntülerinin yerine geçmez; yalnızca mevcut masa doluluk hesaplama hattının temel fonksiyonel ve performans duman testi için kullanılmıştır.

## 2. Ölçüm yöntemi

### 2.1 Gerçek UTYM doğrulaması

Gerçek doğrulama için beklenen minimum girişler:

- Kamera ve masa kalibrasyonu ile eşleşen gerçek UTYM kareleri veya kısa video kesitleri.
- Her kare için masa bazında `empty` / `occupied` etiketi.
- Belirsiz/etiketlenemeyen kareler için ayrı işaretleme politikası.
- Test cihazı bilgileri: CPU modeli, RAM, GPU modeli, işletim sistemi ve runtime.

Bu girişler repoda olmadığı için gerçek veri üzerinde inference çalıştırılmadı.

### 2.2 Sentetik duman testi

Sentetik duman testinde `sample_data/validation/*_expected.json` etiketleri kullanıldı. Her `occupied` masa için masa poligon merkezine temsili bir `person` tespiti yerleştirildi ve `app.vision.occupancy.compute_table_occupancy` fonksiyonu çalıştırıldı. Bu yöntem model dedektör başarısını ölçmez; yalnızca masa eşleme, karar mantığı ve CPU tabanlı hesaplama maliyetini kontrol eder.

Çalıştırılan komut:

```bash
python - <<'PY'
import json, time, resource
from pathlib import Path
from app.calibration.models import TablePolygon
from app.vision.detector import Detection
from app.vision.occupancy import compute_table_occupancy
# sample_data/validation beklenen etiketleri okunarak sentetik person tespitleri üretildi.
# 4 kare x 8 masa için doğruluk; 10.000 inference çağrısı için süre/kaynak ölçüldü.
PY
```

## 3. Metrik tanımları

| Metrik | Tanım |
| --- | --- |
| Masa bazlı doğruluk oranı | Doğru tahmin edilen masa kararları / toplam masa kararı |
| False occupied oranı | Gerçekte boş olup `occupied` tahmin edilen masa kararları / toplam masa kararı |
| False empty oranı | Gerçekte dolu olup `empty` tahmin edilen masa kararları / toplam masa kararı |
| Belirsiz karar oranı | `uncertain` tahmin edilen masa kararları / toplam masa kararı |
| Ortalama inference süresi | Tek kare/karar hattı çağrısı için ortalama süre |
| FPS | Saniye başına işlenen kare/hattı çağrısı |
| CPU/RAM/GPU kullanımı | Test süresindeki CPU oranı, maksimum RSS ve GPU durumu |

## 4. Gerçek etiketli UTYM görüntüleri sonuçları

| Metrik | Sonuç | Not |
| --- | ---: | --- |
| Masa bazlı doğruluk oranı | N/A | Gerçek etiketli UTYM görüntüsü yok |
| False occupied oranı | N/A | Gerçek etiketli UTYM görüntüsü yok |
| False empty oranı | N/A | Gerçek etiketli UTYM görüntüsü yok |
| Belirsiz karar oranı | N/A | Gerçek etiketli UTYM görüntüsü yok |
| Ortalama inference süresi | N/A | Gerçek kamera/model inference çalıştırılamadı |
| FPS | N/A | Gerçek kamera/model inference çalıştırılamadı |
| CPU kullanımı | N/A | Gerçek test yok |
| RAM kullanımı | N/A | Gerçek test yok |
| GPU kullanımı | N/A | Gerçek test yok |

## 5. Sentetik duman testi sonuçları

| Metrik | Sonuç |
| --- | ---: |
| Test kare sayısı | 4 |
| Masa kararı sayısı | 32 |
| Masa bazlı doğruluk oranı | %100.00 |
| False occupied oranı | %0.00 |
| False empty oranı | %0.00 |
| Belirsiz karar oranı | %0.00 |
| Ortalama inference süresi | 0.381 ms |
| FPS | 2619.27 |
| CPU kullanımı | Tek çekirdek eşdeğeri %99.82 |
| Maksimum RAM / RSS | 28.96 MB |
| GPU kullanımı | GPU kullanılmadı / ortamda ölçülebilir GPU yok |

> Not: Bu değerler gerçek görüntü/model performansı değildir. Sentetik tespitler doğrudan beklenen masa durumlarından üretildiği için dedektör kaçırma, yanlış kişi tespiti, perspektif, aydınlatma, örtüşme ve kamera sıkıştırması risklerini ölçmez.

## 6. Minimum kabul kriteri değerlendirmesi

| Kriter | Durum | Açıklama |
| --- | --- | --- |
| Masa bazlı doluluk doğruluğu >= %90 | Değerlendirilemedi | Gerçek etiketli UTYM görüntüleri eksik |
| False empty oranı mümkün olduğunca düşük | Değerlendirilemedi | Gerçek dolu masa örnekleri eksik |
| Gerçek zamanlı kullanım için >= 5 FPS | Değerlendirilemedi | Gerçek model/kamera hattı çalıştırılamadı; sentetik CPU karar hattı 2619.27 FPS verdi |

## 7. Riskler ve öneriler

1. **Gerçek veri eksikliği:** Kabul testi için en az farklı yoğunluk, aydınlatma ve oturma düzenlerini içeren gerçek etiketli UTYM kareleri eklenmelidir.
2. **Dedektör performansı ölçülmedi:** Bu rapordaki duman testi, kişi algılama modelinin doğruluğunu ölçmez. ONNX/YOLO runtime ile uçtan uca test gereklidir.
3. **False empty kritik risk:** Kullanım senaryosunda dolu masayı boş göstermek operasyonel olarak daha riskli olduğundan kabul eşiğinde false empty ayrıca izlenmeli ve mümkünse false occupied değerinden daha sıkı takip edilmelidir.
4. **Kaynak ölçümü cihaz bağımlı:** CPU/RAM/GPU sonuçları hedef edge cihazda yeniden alınmalıdır.

## 8. Sonuç

Mevcut repository içeriğiyle gerçek etiketli UTYM görüntüleri üzerinde sistem başarısı ölçülemedi. Sentetik doğrulama seti üzerinde karar mantığı başarılı ve hızlı görünmektedir; ancak bu sonuçlar saha kabulü için yeterli değildir. Minimum kabul kriterlerine karar verebilmek için gerçek, etiketli UTYM görüntülerinin eklenmesi ve aynı metriklerin uçtan uca inference hattında tekrar ölçülmesi gerekir.
