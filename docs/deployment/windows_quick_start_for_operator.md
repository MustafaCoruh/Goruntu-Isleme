# Windows Operatör Hızlı Başlangıç Kılavuzu

Bu kılavuz, GitHub, VS Code veya Python'a yeni başlayan bir kullanıcının Windows bilgisayarda lokal demo hazırlığı yapabilmesi için yazılmıştır. Adımları sırayla uygulayın; gerçek fotoğraf, video, model, lokal config ve RTSP bilgilerini repository içine koymayın.

## 0. Başlamadan Önce

İhtiyaç listesi:

- Windows bilgisayar.
- Kurulu Visual Studio Code.
- Kurulu Python 3.11.9.
- Bu proje klasörü: `Goruntu-Isleme`.
- ONNX model dosyası: örnek ad `person_detector.onnx`.
- Lokal test için en az bir fotoğraf veya video.

Bu dokümanda gerçek saha dosyaları için repository dışındaki şu klasör kullanılacaktır:

```text
C:\FTMC_FIELD_DATA
```

> Önemli: `C:\FTMC_FIELD_DATA` içindeki dosyalar lokal bilgisayarda kalır. Bu dosyaları GitHub'a, repository'ye veya VS Code içinde commit alanına eklemeyin.

## 1. VS Code ile Projeyi Açma

1. Windows Başlat menüsünden **Visual Studio Code** uygulamasını açın.
2. Üst menüden **File > Open Folder...** seçeneğine tıklayın.
3. Proje klasörünü seçin. Örnek:

   ```text
   C:\Users\<KULLANICI_ADI>\Desktop\Goruntu-Isleme
   ```

4. VS Code güven sorarsa **Yes, I trust the authors** seçeneğini seçin.
5. VS Code içinde üst menüden **Terminal > New Terminal** seçeneğine tıklayın.
6. Terminal satırında proje klasöründe olduğunuzu kontrol edin. Terminalde şu komutu yazın:

   ```powershell
   pwd
   ```

   Çıktı `Goruntu-Isleme` klasörünü göstermelidir.

## 2. Python 3.11.9 Kontrolü

VS Code terminalinde şu komutu çalıştırın:

```powershell
python --version
```

Beklenen çıktı şuna benzer olmalıdır:

```text
Python 3.11.9
```

Eğer `python` komutu çalışmazsa şu komutu deneyin:

```powershell
py -3.11 --version
```

Bu komut `Python 3.11.9` gösteriyorsa sonraki adımlarda `python` yerine `py -3.11` kullanabilirsiniz.

## 3. `.venv` Sanal Ortamını Oluşturma

Sanal ortam, bu proje için gerekli Python paketlerini ayrı bir klasörde tutar. Proje klasöründeyken şu komutu çalıştırın:

```powershell
python -m venv .venv
```

Eğer bilgisayarınızda `python` komutu çalışmıyorsa:

```powershell
py -3.11 -m venv .venv
```

Sanal ortamı etkinleştirin:

```powershell
.\.venv\Scripts\Activate.ps1
```

Başarılı olursa terminal satırının başında `(.venv)` yazısı görünür.

## 4. Paket Kurulumu

Önce pip'i güncelleyin:

```powershell
python -m pip install --upgrade pip
```

Sonra proje paketlerini kurun:

```powershell
python -m pip install -r requirements.txt
```

Kurulum tamamlandıktan sonra hızlı kontrol için şu komutu çalıştırın:

```powershell
python -m app.main --help
```

Yardım metni görünüyorsa paket kurulumu temel olarak hazırdır.

## 5. `C:\FTMC_FIELD_DATA` Klasörünü Oluşturma

Gerçek saha dosyalarını proje klasörünün dışında tutmak için Windows PowerShell'de şu komutu çalıştırın:

```powershell
New-Item -ItemType Directory -Force C:\FTMC_FIELD_DATA\input\photos, C:\FTMC_FIELD_DATA\input\videos, C:\FTMC_FIELD_DATA\models, C:\FTMC_FIELD_DATA\configs, C:\FTMC_FIELD_DATA\reports
```

Beklenen klasör yapısı:

```text
C:\FTMC_FIELD_DATA\
├── input\
│   ├── photos\
│   └── videos\
├── models\
├── configs\
└── reports\
```

## 6. Model Dosyasını Yerleştirme

Model dosyanızı şu klasöre kopyalayın:

```text
C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

PowerShell ile kopyalama örneği:

```powershell
Copy-Item "C:\Users\<KULLANICI_ADI>\Downloads\person_detector.onnx" "C:\FTMC_FIELD_DATA\models\person_detector.onnx"
```

Dosyanın yerinde olduğunu kontrol edin:

```powershell
Test-Path C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

Çıktı `True` olmalıdır.

## 7. Lokal Fotoğraf veya Video Yerleştirme

Fotoğraf kullanacaksanız dosyayı şu klasöre koyun:

```text
C:\FTMC_FIELD_DATA\input\photos\sample.jpg
```

Video kullanacaksanız dosyayı şu klasöre koyun:

```text
C:\FTMC_FIELD_DATA\input\videos\sample.mp4
```

Örnek kopyalama komutları:

```powershell
Copy-Item "C:\Users\<KULLANICI_ADI>\Desktop\sample.jpg" "C:\FTMC_FIELD_DATA\input\photos\sample.jpg"
Copy-Item "C:\Users\<KULLANICI_ADI>\Desktop\sample.mp4" "C:\FTMC_FIELD_DATA\input\videos\sample.mp4"
```

Desteklenen yaygın dosya tipleri:

- Fotoğraf: `.jpg`, `.jpeg`, `.png`, `.bmp`.
- Video: `.mp4`, `.avi`, `.mkv`, `.mov`, `.m4v`.

## 8. Template Config'i Lokal Config'e Kopyalama

Repository içindeki template config dosyası örnek/başlangıç dosyasıdır. Bunu lokal klasöre kopyalayın ve lokal kopya üzerinden çalışın:

```powershell
Copy-Item "configs\templates\tutym2_cam_001.template.json" "C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json"
```

Kontrol edin:

```powershell
Test-Path C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json
```

Çıktı `True` olmalıdır.

> Not: Template dosyadaki masa koordinatları placeholder olabilir. Gerçek saha kalibrasyonu yapılınca masa `polygon` değerleri sadece lokal config dosyasında güncellenmelidir.

## 9. Demo Çalıştırma

Önce sanal ortamın aktif olduğundan emin olun. Terminal satırı `(.venv)` ile başlamalıdır. Başlamıyorsa:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Fotoğraf ile demo

```powershell
python -m app.main `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --source C:\FTMC_FIELD_DATA\input\photos\sample.jpg `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

### Fotoğraf ile çıktı dosyası üretme

Pencere açmadan overlay sonucu üretmek için:

```powershell
python -m app.main `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --source C:\FTMC_FIELD_DATA\input\photos\sample.jpg `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx `
  --output C:\FTMC_FIELD_DATA\reports\sample_overlay.jpg `
  --no-display
```

### Video ile demo

```powershell
python -m app.main `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --source C:\FTMC_FIELD_DATA\input\videos\sample.mp4 `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

Demo penceresi açılırsa kapatmak için klavyeden `q` tuşuna basabilirsiniz.

## 10. Sık Karşılaşılan Hatalar

### 10.1. Python bulunamadı

Belirti:

```text
python is not recognized
```

Çözüm:

1. Python 3.11.9'un kurulu olduğundan emin olun.
2. Şu komutu deneyin:

   ```powershell
   py -3.11 --version
   ```

3. Çalışıyorsa komutlarda `python` yerine `py -3.11` kullanın.
4. Hiçbiri çalışmıyorsa Python kurulumu veya Windows PATH ayarı eksiktir.

### 10.2. pip kurulumu başarısız

Belirti:

```text
ERROR: Could not install packages
```

Çözüm:

1. Sanal ortamın aktif olduğunu kontrol edin: terminalde `(.venv)` görünmelidir.
2. pip'i güncelleyin:

   ```powershell
   python -m pip install --upgrade pip
   ```

3. Paket kurulumunu tekrar deneyin:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Kurumsal bilgisayarda internet/proxy kısıtı varsa offline kurulum paketi veya kurum içi paket kaynağı gerekebilir.

### 10.3. Model bulunamadı

Belirti:

```text
Model path was not found
```

Çözüm:

1. Dosyanın burada olduğunu kontrol edin:

   ```powershell
   Test-Path C:\FTMC_FIELD_DATA\models\person_detector.onnx
   ```

2. Çıktı `False` ise model dosyasını `C:\FTMC_FIELD_DATA\models` klasörüne kopyalayın.
3. Demo komutundaki `--model` yolunun aynı olduğundan emin olun.

### 10.4. Config bulunamadı

Belirti:

```text
Config path was not found
```

Çözüm:

1. Lokal config'i yeniden kopyalayın:

   ```powershell
   Copy-Item "configs\templates\tutym2_cam_001.template.json" "C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json"
   ```

2. Kontrol edin:

   ```powershell
   Test-Path C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json
   ```

3. Demo komutundaki `--config` yolunu kontrol edin.

### 10.5. Video/foto okunamadı

Belirti:

```text
Source path was not found
```

veya

```text
Unsupported source file type
```

Çözüm:

1. Dosya yolunu kontrol edin:

   ```powershell
   Test-Path C:\FTMC_FIELD_DATA\input\photos\sample.jpg
   Test-Path C:\FTMC_FIELD_DATA\input\videos\sample.mp4
   ```

2. Dosya adında boşluk veya Türkçe karakter varsa önce sade bir ad deneyin: `sample.jpg` veya `sample.mp4`.
3. Dosya uzantısının desteklendiğinden emin olun.
4. Video başka bir programda açılmıyorsa dosya bozuk olabilir; farklı bir video ile deneyin.

### 10.6. RTSP URL yanlışlıkla repo'ya kondu

Belirti:

- Gerçek kamera IP adresi, kullanıcı adı, parola veya RTSP URL'si VS Code içinde proje dosyalarına yazıldı.
- VS Code Source Control ekranında gerçek RTSP bilgisi içeren dosya görünüyor.

Çözüm:

1. Hemen ilgili dosyadan gerçek RTSP bilgisini silin.
2. Gerçek URL yerine şu gibi temsili bir değer bırakın:

   ```text
   rtsp://<USER>:<PASSWORD>@<CAMERA_IP>/<STREAM_PATH>
   ```

3. Gerçek RTSP bilgisini sadece `C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json` gibi lokal ve repo dışı dosyada tutun.
4. VS Code Source Control ekranında `C:\FTMC_FIELD_DATA` içinden hiçbir dosyanın görünmediğini kontrol edin.
5. Eğer gerçek bilgi commit edildiyse veya GitHub'a gönderildiyse teknik sorumluya haber verin; parola/erişim bilgileri değiştirilmelidir.

## 11. Hızlı Kontrol Listesi

Demo öncesi son kontrol:

- [ ] VS Code proje klasörü olarak `Goruntu-Isleme` açıldı.
- [ ] Python sürümü `Python 3.11.9` olarak kontrol edildi.
- [ ] `.venv` oluşturuldu ve aktif edildi.
- [ ] `python -m pip install -r requirements.txt` tamamlandı.
- [ ] `C:\FTMC_FIELD_DATA` klasör yapısı oluşturuldu.
- [ ] Model dosyası `C:\FTMC_FIELD_DATA\models\person_detector.onnx` yolunda.
- [ ] Fotoğraf veya video `C:\FTMC_FIELD_DATA\input` altında.
- [ ] Config dosyası `C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json` yolunda.
- [ ] Gerçek RTSP URL, kullanıcı adı, parola, fotoğraf ve video repository içine konmadı.
