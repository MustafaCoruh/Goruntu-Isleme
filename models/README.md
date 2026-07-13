# Person Detector Model Artifact Guide

Bu klasör, FTMC/UTYM masa doluluk demosunda kullanılacak kişi tespit modelinin beklenen konumunu ve güvenli taşıma kurallarını açıklar.

## 1. Beklenen Model Dosyası

Uygulama varsayılan olarak aşağıdaki ONNX model dosyasını bekler:

```text
models/person_detector.onnx
```

T.UTYM#2 Windows saha demosunda önerilen lokal model yolu şudur:

```text
C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

## 2. Model Repository'ye Eklenmeli mi?

Varsayılan kural:

```text
Model dosyası büyükse, lisanslıysa veya kurum politikası gereği kontrollü dağıtılıyorsa repository'ye eklenmemelidir.
```

Bu durumda model yalnızca saha makinesinde veya kurum içi güvenli dosya paylaşım alanında tutulmalıdır.

## 3. Modelin Bütünlüğünü Kontrol Etme

Windows PowerShell ile SHA256 hash alınabilir:

```powershell
Get-FileHash C:\FTMC_FIELD_DATA\models\person_detector.onnx -Algorithm SHA256
```

Elde edilen hash kurum içi onaylı hash değeriyle karşılaştırılmalıdır.

## 4. CPU ve GPU Notları

- Geliştirme bilgisayarı CPU-only olabilir.
- T.UTYM#2 operasyon bilgisayarlarında GPU varsa performans ayrıca ölçülmelidir.
- ONNX Runtime CPU provider baseline olarak kullanılabilir.
- GPU kullanımı istenirse ONNX Runtime GPU kurulumu, CUDA/cuDNN sürümleri ve kurum BT politikaları ayrıca değerlendirilmelidir.

## 5. Model Yoksa Beklenen Hata

T.UTYM#2 lokal demo runner model yoksa demo başlamadan önce şu tip hata verir:

```text
Missing ONNX person detector model
```

Çözüm:

1. Model dosyasını lokal saha klasörüne koyun.
2. Dosya adının `person_detector.onnx` olduğundan emin olun.
3. Komutta `--model` path'inin doğru olduğundan emin olun.

## 6. Güvenlik Notları

- Model dosyasının kaynağı kurum tarafından onaylanmalıdır.
- Model hash değeri kayıt altına alınmalıdır.
- Model dosyası değiştirilirse saha doğrulama metrikleri yeniden alınmalıdır.
- Model dosyasıyla birlikte gerçek görüntü, video veya RTSP credential taşınmamalıdır.
