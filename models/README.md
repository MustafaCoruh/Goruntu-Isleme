# Person Detector Model Artifact Guide

Bu klasör, FTMC/UTYM masa doluluk demosunda kullanılacak kişi tespit modelinin beklenen konumunu ve güvenli taşıma kurallarını açıklar.

## 1. Beklenen Model Dosyası

Uygulama varsayılan olarak aşağıdaki ONNX model dosyasını bekler:

```text
models/person_detector.onnx
```

Kod, COCO sınıf sıralamasında kişi sınıfı `0` olan, YOLOX-stili tek görüntü girdili ve kutu/güven/sınıf değerleri üreten bir ONNX nesne tespit modeli bekler. Bu proje için önerilen başlangıç dosyası, model üreticisinin resmî kaynağından temin edilen `yolox_nano.onnx` dosyasıdır. Rastgele dosya indirme sitelerini kullanmayın.

## 2. Modeli Adım Adım Kurma

> Şirket ağı GitHub veya haricî model indirmeyi engelliyorsa bu adımı atlayabilirsiniz. Uygulama otomatik olarak OpenCV HOG kişi dedektörüyle; OpenCV paketinde HOG yoksa hareket tabanlı dedektörle **geliştirme modu**nda çalışır. Ayrı dosya veya internet gerekmez; ancak doğruluğu YOLOX'tan düşüktür ve üretim kabulü için kullanılmamalıdır.

1. Kurumunuzun onaylı model deposundan veya [Megvii YOLOX projesinin resmî GitHub Releases sayfasından](https://github.com/Megvii-BaseDetection/YOLOX/releases) `yolox_nano.onnx` dosyasını indirin.
2. Dosyayı örneğin Windows `Downloads` klasöründe tutun; adını elle `person_detector.onnx` yapmanız gerekmez.
3. En kolay yöntem: indirdiğiniz `yolox_nano.onnx` dosyasını repository kökündeki `TUTYM2_MODEL_KUR.bat` dosyasının üzerine sürükleyip bırakın. Araç doğrulama ve kopyalama işlemini otomatik yapar.
4. Komut satırı kullanmak isterseniz repository kökünde Komut İstemi veya PowerShell açıp aşağıdaki komutu indirdiğiniz gerçek yola göre çalıştırın:

```powershell
py -3 scripts/install_tutym2_person_model.py "$env:USERPROFILE\Downloads\yolox_nano.onnx"
```

Repository içinde `.venv` kullanıyorsanız:

```powershell
.\.venv\Scripts\python.exe scripts\install_tutym2_person_model.py "$env:USERPROFILE\Downloads\yolox_nano.onnx"
```

Araç modeli önce ONNX Runtime ile açar, giriş/çıkış yapısını kontrol eder ve yalnızca doğrulama geçerse atomik olarak `models/person_detector.onnx` konumuna kopyalar. Başarılı sonuçta `MODEL KURULDU` mesajı görünür.

5. `MODEL KURULDU` mesajını gördükten sonra `TUTYM2_KONTROL.bat` dosyasını yeniden çalıştırın.
6. Doluluk panelinde **Yenile** düğmesine basın ve **Kişi tespit modeli** kontrolünün yeşil olduğunu doğrulayın.

T.UTYM#2 Windows kurulumu için alternatif lokal model yolu şudur:

```text
C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

## 3. Model Repository'ye Eklenmeli mi?

Varsayılan kural:

```text
Model dosyası büyükse, lisanslıysa veya kurum politikası gereği kontrollü dağıtılıyorsa repository'ye eklenmemelidir.
```

Bu durumda model yalnızca saha makinesinde veya kurum içi güvenli dosya paylaşım alanında tutulmalıdır.

## 4. Modelin Bütünlüğünü Kontrol Etme

Windows PowerShell ile SHA256 hash alınabilir:

```powershell
Get-FileHash C:\FTMC_FIELD_DATA\models\person_detector.onnx -Algorithm SHA256
```

Elde edilen hash kurum içi onaylı hash değeriyle karşılaştırılmalıdır.

## 5. CPU ve GPU Notları

- Geliştirme bilgisayarı CPU-only olabilir.
- T.UTYM#2 operasyon bilgisayarlarında GPU varsa performans ayrıca ölçülmelidir.
- ONNX Runtime CPU provider baseline olarak kullanılabilir.
- GPU kullanımı istenirse ONNX Runtime GPU kurulumu, CUDA/cuDNN sürümleri ve kurum BT politikaları ayrıca değerlendirilmelidir.

## 6. Model Yoksa Beklenen Hata

T.UTYM#2 lokal demo runner model yoksa demo başlamadan önce şu tip hata verir:

```text
Missing ONNX person detector model
```

Çözüm:

1. Model dosyasını lokal saha klasörüne koyun.
2. Dosya adının `person_detector.onnx` olduğundan emin olun.
3. Komutta `--model` path'inin doğru olduğundan emin olun.

## 7. Güvenlik Notları

- Model dosyasının kaynağı kurum tarafından onaylanmalıdır.
- Model hash değeri kayıt altına alınmalıdır.
- Model dosyası değiştirilirse saha doğrulama metrikleri yeniden alınmalıdır.
- Model dosyasıyla birlikte gerçek görüntü, video veya RTSP credential taşınmamalıdır.
