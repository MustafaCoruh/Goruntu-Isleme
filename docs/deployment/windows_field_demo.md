# T.UTYM#2 Windows Lokal Saha Demo Akışı

Bu doküman, gerçek T.UTYM#2 görüntüleri paylaşılmadan Windows üzerinde lokal geçmiş video, fotoğraf veya RTSP destekli IP kamera ile masa doluluk demosu çalıştırma akışını tanımlar.

## 1. Hedef Ortam

| Konu | Değer |
| --- | --- |
| UTYM | T.UTYM#2 |
| İşletim sistemi | Windows |
| Kamera tipi | RTSP destekli IP video kamera |
| Çözünürlük | 1920x1080 (1080P) |
| Masa sayısı | 14 |
| Sandalye | Masa başına 1 sandalye |
| Geliştirme bilgisayarı | Intel Xeon Gold 6284R CPU, GPU yok, kontrollü internet erişimi var |
| Operasyon bilgisayarı | GPU bulunan Windows bilgisayarlar, internet erişimi yok |
| İlk test kaynağı | Lokal geçmiş video veya fotoğraf |

## 2. Güvenlik Kuralları

- Gerçek fotoğraf, video, RTSP URL, kullanıcı adı, parola ve kamera IP adresi repository'ye eklenmez.
- Gerçek görüntü dosyaları yalnızca lokal saha makinesinde tutulur.
- Komut örneklerinde gerçek dosya yolları yerine temsili path kullanılır.
- T.UTYM#2 config dosyası kamera görüntüsü içermese bile tesis yerleşimi bilgisi taşıyabileceği için kontrollü paylaşılmalıdır.

## 3. Önerilen Lokal Klasör Yapısı

Windows saha makinesinde repo dışında aşağıdaki klasör yapısı kullanılabilir:

```text
C:\FTMC_FIELD_DATA\
├── input\
│   ├── photos\
│   └── videos\
├── models\
│   └── person_detector.onnx
├── configs\
│   └── tutym2_cam_001.local.json
└── reports\
```

Bu klasör repository dışında kalmalıdır.

## 4. İlk Lokal Fotoğraf/Video Testi

Gerçek görüntü paylaşılmadan, saha makinesindeki lokal dosya ile demo çalıştırılır.

Fotoğraf örneği:

```powershell
python -m app.main `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --source C:\FTMC_FIELD_DATA\input\photos\sample.jpg `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

Video örneği:

```powershell
python -m app.main `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --source C:\FTMC_FIELD_DATA\input\videos\sample.mp4 `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

## 5. RTSP Canlı Kamera Testi

Gerçek RTSP URL repository'ye yazılmamalıdır. Canlı kamera testi için URL yalnızca lokal saha config dosyasında veya kurumun secret yönetim mekanizmasında tutulmalıdır.

Temsili config alanı:

```json
{
  "camera_id": "TUTYM2-CAM-001",
  "source_type": "rtsp",
  "stream_url": "rtsp://<USER>:<PASSWORD>@<CAMERA_IP>/<STREAM_PATH>"
}
```

Canlı RTSP testi için mevcut `RtspCameraSource` altyapısı kullanılmalıdır. Komut satırı demo akışı şu an dosya kaynaklarını doğrudan desteklediği için RTSP canlı demo gerekiyorsa ayrı bir RTSP runner veya `app.main` içinde RTSP kaynak seçimi eklenmelidir.

## 6. Kalibrasyon Beklentisi

T.UTYM#2 için 14 masa lokal görüntü üzerinden kalibre edilecektir. Her masa için şu alanlar doldurulmalıdır:

- `table_id`
- `name`
- `capacity`
- `polygon`

Kalibrasyon tamamlandığında lokal config dosyası şu isimle saklanabilir:

```text
C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json
```

## 7. Saha Sonuçlarını Görüntü Paylaşmadan Raporlama

Görüntü paylaşmadan aşağıdaki sonuçlar raporlanabilir:

| Metrik | Örnek |
| --- | --- |
| Test tipi | Lokal video / lokal fotoğraf / RTSP canlı |
| Test dosyası adedi | 10 fotoğraf veya 1 video gibi |
| Ortalama FPS | 8.5 FPS |
| Masa bazlı doğruluk | %92 |
| False empty | %3 |
| False occupied | %5 |
| Belirsiz karar oranı | %4 |
| Donanım | CPU/GPU modeli, RAM |

## 8. Operatör Dostu Lokal Demo Runner

Lokal fotoğraf veya video testleri için daha anlaşılır preflight hataları veren T.UTYM#2 runner eklenmiştir. Bu runner gerçek görüntü, video, model ve lokal config dosyalarının repository dışında tutulduğunu varsayar.

Örnek kullanım:

```powershell
python scripts/run_tutym2_local_demo.py `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --source C:\FTMC_FIELD_DATA\input\photos\sample.jpg `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx `
  --report-output C:\FTMC_FIELD_DATA\reports\demo_result.json
```

Bu rapor dosyası gerçek görüntü veya RTSP bilgisi içermez; yalnızca güvenli özet metadata ve çalışma durumunu içerir.

Alternatif modül kullanımı:

```powershell
python -m app.field_demo `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --source C:\FTMC_FIELD_DATA\input\videos\sample.mp4 `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

Runner şu kontrolleri demo başlamadan yapar:

1. Lokal config dosyası var mı?
2. Lokal fotoğraf/video kaynağı var mı?
3. ONNX model dosyası var mı?
4. Kaynak uzantısı destekleniyor mu?
5. Confidence ve IoU eşikleri 0 ile 1 arasında mı?

## 9. Sıradaki Kod İhtiyacı

Aşağıdaki geliştirmeler önerilir:

1. RTSP kaynaklarını komut satırı demosuna güvenli şekilde bağlamak.
2. Windows için `.env` veya lokal config secret stratejisi eklemek.
3. Lokal saha raporu üretim komutu eklemek.
4. CPU ve GPU performansını ayrı ayrı raporlamak.
