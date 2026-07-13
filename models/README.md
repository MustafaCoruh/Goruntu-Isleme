# Person Detector ONNX Model Placement

Bu dizin, saha makinesinde çalışacak person detector ONNX modelinin beklenen konumunu dokümante eder. Gerçek model dosyası büyük boyutlu olabileceği veya lisans/dağıtım kısıtları içerebileceği için repo'ya eklenmeyebilir.

## Beklenen repo içi model yolu

Uygulamanın varsayılan olarak arayacağı model dosyası aşağıdaki konumdadır:

```text
models/person_detector.onnx
```

Saha kurulumunda model repo ile birlikte dağıtılıyorsa, `person_detector.onnx` dosyasını bu README ile aynı dizine kopyalayın.

## Alternatif saha yolu

Saha operasyon bilgisayarında modelin uygulama dizininden bağımsız ve kalıcı bir veri alanında tutulması istenirse aşağıdaki yol kullanılabilir:

```text
C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

Bu yol özellikle uygulama klasörünün güncelleme sırasında silinebileceği veya yeniden oluşturulabileceği kurulumlarda tercih edilmelidir. Operatör, uygulama yapılandırmasında model yolu seçeneği varsa bu mutlak Windows yolunu kullanmalıdır.

## Model repo'ya eklenmiyorsa taşıma adımları

1. Model dosyasını güvenilir dağıtım kaynağından saha makinesine indirin veya harici disk/kurumsal dosya paylaşımı ile taşıyın.
2. Dosya adının tam olarak `person_detector.onnx` olduğundan emin olun.
3. Aşağıdaki hedeflerden yalnızca birine kopyalayın:
   - Repo içi varsayılan yol: `models/person_detector.onnx`
   - Alternatif saha yolu: `C:\FTMC_FIELD_DATA\models\person_detector.onnx`
4. Alternatif saha yolunu kullanıyorsanız klasör yoksa oluşturun:

   ```powershell
   New-Item -ItemType Directory -Force C:\FTMC_FIELD_DATA\models
   ```

5. Kopyalama sonrası bütünlük kontrolünü SHA256 checksum ile doğrulayın.

## SHA256 bütünlük kontrolü

Model dosyası için beklenen SHA256 değeri model dağıtım notunda, sürüm manifest dosyasında veya teslimat e-postasında ayrıca paylaşılmalıdır. Kurulum operatörü, kopyalanan dosyanın checksum değerini bu beklenen değerle karşılaştırmalıdır.

Windows PowerShell ile repo içi yol için:

```powershell
Get-FileHash .\models\person_detector.onnx -Algorithm SHA256
```

Windows PowerShell ile alternatif saha yolu için:

```powershell
Get-FileHash C:\FTMC_FIELD_DATA\models\person_detector.onnx -Algorithm SHA256
```

Linux/macOS geliştirme ortamında repo içi yol için:

```bash
sha256sum models/person_detector.onnx
```

Çıktıdaki hash değeri beklenen SHA256 değeriyle birebir aynı olmalıdır. Farklıysa model dosyasını kullanmayın; dosyayı yeniden indirin veya tekrar kopyalayın.

## CPU-only geliştirme bilgisayarı ve GPU'lu operasyon bilgisayarı

- CPU-only geliştirme bilgisayarı: Geliştirici, gerçek model dosyası olmadan kodu düzenleyebilir, dokümantasyonu güncelleyebilir ve model yüklemeyen testleri çalıştırabilir. Model gerektiren entegrasyon testleri veya gerçek zamanlı çıkarım performans kontrolleri bu ortamda beklenen performansı vermeyebilir.
- GPU'lu operasyon bilgisayarı: Saha çalıştırması için `person_detector.onnx` dosyası yukarıdaki beklenen yollardan birinde bulunmalıdır. GPU sürücüleri, CUDA/cuDNN veya kullanılan çıkarım sağlayıcısının gerektirdiği runtime bileşenleri ayrıca kurulu olmalıdır.

Model dosyasının konumu CPU ve GPU ayrımından bağımsızdır; fark, çıkarımın hangi donanım ve runtime sağlayıcısıyla çalıştırılacağıdır.

## Model bulunamazsa hata ve çözüm

Model dosyası beklenen konumlarda yoksa uygulama başlatılırken veya person detector bileşeni etkinleştirilirken aşağıdakine benzer bir hata alınır:

```text
FileNotFoundError: person detector model not found: models/person_detector.onnx
```

Alternatif saha yolu yapılandırılmışsa hata mesajı şu yolu da içerebilir:

```text
FileNotFoundError: person detector model not found: C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

Çözüm:

1. `person_detector.onnx` dosyasının gerçekten hedef klasörde olduğunu kontrol edin.
2. Dosya adında yazım hatası, ek uzantı veya büyük/küçük harf farkı olmadığını doğrulayın.
3. Alternatif saha yolu kullanılıyorsa uygulama yapılandırmasının `C:\FTMC_FIELD_DATA\models\person_detector.onnx` yolunu gösterdiğinden emin olun.
4. SHA256 checksum değerini tekrar kontrol edin.
5. Dosya eksik veya checksum hatalıysa modeli güvenilir kaynaktan yeniden taşıyın.
