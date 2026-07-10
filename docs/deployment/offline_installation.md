# Offline Kurulum Kılavuzu

Bu doküman, uygulamanın internet erişimi olmayan bir makinede çalıştırılabilmesi için geliştirme ortamında hazırlanacak paketleri, model dosyalarını ve offline makinede uygulanacak kurulum adımlarını açıklar. Komutlar depo kök dizininden çalıştırılmalıdır.

## 1. Geliştirme ortamında paketlerin hazırlanması

İnternet erişimi olan geliştirme makinesinde uygulama klasörünün güncel ve test edilmiş bir kopyasını hazırlayın.

1. Depoyu veya uygulama klasörünü geliştirme makinesine alın.
2. `requirements.txt` dosyasının hedef sürümle uyumlu olduğundan emin olun.
3. Hedef offline makinenin işletim sistemi, Python sürümü ve işlemci mimarisiyle aynı veya uyumlu bir geliştirme ortamı kullanın. Wheel dosyaları platforma göre değişebildiği için bu adım özellikle `opencv-python` ve `onnxruntime` gibi paketlerde önemlidir.
4. Paketleri ve model dosyalarını uygulama klasörünün içine yerleştireceğiniz standart dizinleri oluşturun:

   ```bash
   mkdir -p wheels models data logs
   ```

## 2. Python wheel dosyalarının indirilmesi

Geliştirme makinesinde tüm bağımlılıkları `wheels/` klasörüne indirin. Bu klasör daha sonra offline makineye uygulama ile birlikte taşınacaktır.

```bash
python -m pip install --upgrade pip
python -m pip download --dest ./wheels -r requirements.txt
```

İsteğe bağlı olarak, paketlerin offline ortamda kurulabildiğini geliştirme makinesinde temiz bir sanal ortamla doğrulayın:

```bash
python -m venv .venv-offline-test
. .venv-offline-test/bin/activate
pip install --no-index --find-links ./wheels -r requirements.txt
python -m app.main --help
deactivate
```

Windows PowerShell kullanılıyorsa aktivasyon komutu aşağıdaki gibidir:

```powershell
.venv-offline-test\Scripts\Activate.ps1
```

## 3. Model dosyalarının `models/` klasörüne eklenmesi

Uygulama varsayılan olarak kişi tespit modeli için `models/person_detector.onnx` yolunu kullanır. Offline paket hazırlığı sırasında ONNX model dosyasını bu klasöre ekleyin.

```bash
mkdir -p models
cp /path/to/person_detector.onnx models/person_detector.onnx
```

Dikkat edilmesi gerekenler:

- Model dosyası internet erişimi olmayan ortamda indirilemeyeceği için transferden önce mutlaka uygulama klasörüne eklenmelidir.
- Model adı veya yolu değiştirilecekse uygulama başlatılırken `--model` parametresiyle yeni yol verilmelidir.
- Kurumsal dağıtım öncesinde model lisansı, bütünlük kontrolü ve kurum içi onay süreci tamamlanmalıdır.

## 4. Uygulama klasörünün USB veya kurum içi transfer yöntemiyle taşınması

Aşağıdaki içerikler aynı uygulama klasörü içinde olacak şekilde offline makineye aktarılmalıdır:

- Uygulama kaynak kodu (`app/` ve ilgili proje dosyaları)
- `requirements.txt`
- `wheels/` klasörü
- `models/` klasörü
- Gerekli kamera/UTYM kalibrasyon JSON dosyaları
- Varsa kuruma özel yapılandırma dosyaları

Örnek arşivleme komutu:

```bash
tar -czf goruntu-isleme-offline.tar.gz app docs requirements.txt wheels models data logs
```

Offline makinede arşivi açmak için:

```bash
tar -xzf goruntu-isleme-offline.tar.gz
cd Goruntu-Isleme
```

USB bellek kullanılıyorsa kurumun zararlı yazılım taraması, varlık kayıt ve veri transfer prosedürleri uygulanmalıdır. Kurum içi dosya transfer sistemi kullanılıyorsa aktarımın tamamlandığı ve dosya bütünlüğünün korunduğu ayrıca doğrulanmalıdır.

## 5. Offline makinede sanal ortam oluşturulması

Offline makinede internet bağlantısı gerekmeden kullanılacak Python sanal ortamını oluşturun ve etkinleştirin.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip --version
```

Windows PowerShell için:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip --version
```

## 6. Paketlerin internet olmadan kurulması

Bağımlılıkları yalnızca yerel `wheels/` klasöründen kurun. `--no-index` parametresi pip'in internet paket indekslerine bağlanmasını engeller; `--find-links ./wheels` parametresi paket kaynağı olarak yerel wheel klasörünü gösterir.

```bash
pip install --no-index --find-links ./wheels -r requirements.txt
```

Kurulumdan sonra temel import kontrolü yapılabilir:

```bash
python -c "import cv2, fastapi, onnxruntime, sqlalchemy; print('offline dependencies ok')"
```

Eksik paket hatası alınırsa geliştirme makinesinde `pip download --dest ./wheels -r requirements.txt` adımı tekrar çalıştırılmalı ve güncel `wheels/` klasörü offline makineye yeniden taşınmalıdır.

## 7. Uygulamanın başlatılması

Komut satırı demo akışı için kamera/UTYM kalibrasyon dosyası, görüntü veya video kaynağı ve model dosyası hazır olmalıdır. Yardım çıktısını görmek için:

```bash
python -m app.main --help
```

Örnek başlatma komutu:

```bash
python -m app.main --config configs/camera.json --source samples/input.mp4 --model models/person_detector.onnx
```

Model dosyası varsayılan konumdaysa `--model` parametresi verilmeden de çalıştırılabilir:

```bash
python -m app.main --config configs/camera.json --source samples/input.mp4
```

API uygulaması kullanılacaksa ASGI uygulaması `app.api.app:app` üzerinden başlatılabilir:

```bash
uvicorn app.api.app:app --host 0.0.0.0 --port 8000
```

## 8. Log ve veritabanı dosyalarının konumu

Varsayılan SQLite veritabanı dosyası aşağıdaki konumda oluşturulur:

```text
data/ftmc.sqlite
```

`data/` klasörü yoksa uygulama veritabanı başlatma sırasında bu klasörü oluşturur. Kurulum öncesinde klasörü manuel oluşturmak isterseniz:

```bash
mkdir -p data
```

Log dosyaları için önerilen uygulama dizini:

```text
logs/
```

Bu depoda varsayılan kalıcı log dosyası yolu kod içinde zorunlu olarak tanımlı değildir. Kurumsal çalıştırma betiği veya servis yöneticisi kullanılıyorsa stdout/stderr çıktısını `logs/` altına yönlendirin:

```bash
mkdir -p logs
python -m app.main --config configs/camera.json --source samples/input.mp4 > logs/app.log 2>&1
```

Servis olarak çalıştırılan kurulumlarda sistem servis yöneticisinin log konumu ayrıca belgelenmelidir. Veritabanı ve log dosyalarına erişim yalnızca yetkili sistem yöneticileri ve proje teknik personeliyle sınırlandırılmalıdır.
