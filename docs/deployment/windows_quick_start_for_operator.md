# Windows Operatör Hızlı Başlangıç Kılavuzu

Bu kılavuz, T.UTYM#2 lokal saha demosunu gerçek görüntü, video, RTSP URL veya model dosyasını repository'ye eklemeden Windows üzerinde hazırlamak için yazılmıştır. Terminal erişimi kurum politikasıyla kısıtlıysa bu adımları yetkili BT veya geliştirme sorumlusu uygulamalıdır.

## 1. Amaç

İlk hedef, canlı RTSP kameraya geçmeden önce lokal geçmiş fotoğraf veya video ile masa doluluk demosunu doğrulamaktır.

Bu akışta kullanılacak güvenli girişler:

- Lokal config dosyası: `C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json`
- Lokal fotoğraf/video: `C:\FTMC_FIELD_DATA\input\photos\` veya `C:\FTMC_FIELD_DATA\input\videos\`
- ONNX model: `C:\FTMC_FIELD_DATA\models\person_detector.onnx`

## 2. Güvenlik Kuralları

Aşağıdaki veriler repository'ye, GitHub'a, PR'a veya chat ortamına eklenmemelidir:

- Gerçek T.UTYM#2 fotoğrafları.
- Gerçek T.UTYM#2 videoları.
- Gerçek RTSP URL.
- Kamera IP adresi.
- Kamera kullanıcı adı/parolası.
- Katılımcıları veya ekranları tanımlayabilecek görüntüler.
- Gerçek model dosyası kurum politikası izin vermiyorsa.

Repository'de yalnızca kod, dokümantasyon, sentetik örnekler ve güvenli template dosyaları tutulmalıdır.

## 3. VS Code'da Dosyaların Geldiğini Kontrol Etme

Terminal kullanamıyorsanız VS Code sol dosya ağacında şu dosyaları kontrol edin:

```text
app/field_demo.py
scripts/run_tutym2_local_demo.py
configs/templates/tutym2_cam_001.template.json
docs/deployment/windows_field_demo.md
docs/requirements/non_shareable_real_data_workflow.md
models/README.md
```

Bu dosyalar görünüyorsa lokal demo hazırlık dosyaları gelmiş demektir.

## 4. Lokal Saha Klasörünü Hazırlama

Windows makinede repository dışında aşağıdaki klasör yapısı oluşturulmalıdır:

```text
C:\FTMC_FIELD_DATA\
├── input\
│   ├── photos\
│   └── videos\
├── models\
├── configs\
└── reports\
```

Bu klasör repository'nin içinde olmamalıdır. Amaç gerçek saha dosyalarını Git takibinden uzak tutmaktır.

## 5. Config Template'i Lokal Config'e Kopyalama

Repository içindeki template dosyası:

```text
configs/templates/tutym2_cam_001.template.json
```

lokal saha klasörüne şu adla kopyalanmalıdır:

```text
C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json
```

Kopyalanan lokal dosyada gerçek RTSP URL yazılacaksa bu dosya kesinlikle repository'ye geri kopyalanmamalıdır.

## 6. Model Dosyasını Yerleştirme

ONNX person detector modeli lokal saha klasörüne şu adla konmalıdır:

```text
C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

Model dosyasının nasıl doğrulanacağı için `models/README.md` dosyasına bakın.

Kalibrasyon ekranının adım adım kullanımı için `docs/deployment/tutym2_calibration_operator_guide.md` dosyasına bakın.

## 7. Lokal Fotoğraf veya Video Yerleştirme

İlk test için gerçek görüntü paylaşmadan lokal dosya kullanılmalıdır.

Fotoğraf örneği:

```text
C:\FTMC_FIELD_DATA\input\photos\sample.jpg
```

Video örneği:

```text
C:\FTMC_FIELD_DATA\input\videos\sample.mp4
```

Dosya adları örnektir; kurum içi dosya adlarını paylaşmayın.

## 8. Demo Komutu

Terminal erişimi varsa yetkili kullanıcı aşağıdaki komutu çalıştırabilir.

Fotoğraf testi:

```powershell
python scripts/run_tutym2_local_demo.py `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --source C:\FTMC_FIELD_DATA\input\photos\sample.jpg `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx `
  --report-output C:\FTMC_FIELD_DATA\reports\demo_result.json
```

İsteğe bağlı `--report-output` parametresi güvenli bir JSON çalışma raporu üretir. Bu rapor gerçek görüntü, RTSP URL veya tam lokal path içermez.

Video testi:

```powershell
python scripts/run_tutym2_local_demo.py `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --source C:\FTMC_FIELD_DATA\input\videos\sample.mp4 `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

Terminal erişiminiz yoksa bu komutları yetkili BT/geliştirme sorumlusunun çalıştırması gerekir.

## 9. Beklenen Sonuç

Demo açıldığında beklenen davranış:

1. Config dosyası okunur.
2. Lokal fotoğraf veya video dosyası okunur.
3. ONNX model dosyası yüklenir.
4. Masa poligonları görüntü üzerine çizilir.
5. İnsan tespiti yapılır.
6. Masa doluluk durumları overlay olarak gösterilir.

## 10. Sık Karşılaşılan Hatalar

| Hata | Anlamı | Çözüm |
| --- | --- | --- |
| `Missing config JSON` | Lokal config dosyası bulunamadı | `C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json` var mı kontrol edin |
| `Missing local photo/video source` | Fotoğraf/video dosyası bulunamadı | `--source` path'i doğru mu kontrol edin |
| `Missing ONNX person detector model` | Model dosyası bulunamadı | `C:\FTMC_FIELD_DATA\models\person_detector.onnx` var mı kontrol edin |
| `Unsupported source extension` | Desteklenmeyen dosya tipi | `.jpg`, `.jpeg`, `.png`, `.avi`, `.m4v`, `.mkv`, `.mov`, `.mp4` kullanın |
| `confidence-threshold must be between 0 and 1` | Hatalı eşik değeri | 0 ile 1 arasında değer girin |

## 11. İlk Saha Doğrulama Notları

İlk denemede görüntü paylaşmadan şu bilgileri not almak yeterlidir:

- Test tipi: fotoğraf mı video mu?
- Kaç görüntü/video denendi?
- Masa poligonları doğru yerde mi?
- Model insanları bulabildi mi?
- Dolu masalar dolu göründü mü?
- Boş masalar boş göründü mü?
- Belirsiz veya hatalı masa örnekleri kaç tane?
- Ortalama FPS veya akıcılık durumu nasıl?

Gerçek görüntü, video, RTSP URL veya kişi bilgisi rapora eklenmemelidir.

Lokal saha doğrulama sonuçlarını görüntü paylaşmadan yazmak için `docs/validation/tutym2_local_field_validation_template.md` şablonunu kullanın.

RTSP canlı kameraya geçmeden önce `docs/deployment/tutym2_rtsp_operator_guide.md` kılavuzunu okuyun.

RTSP lokal config hazırlığında `configs/templates/tutym2_cam_001.rtsp.template.json` dosyasını yalnızca şablon olarak kullanın; gerçek RTSP URL sadece lokal kopyaya yazılmalıdır.
