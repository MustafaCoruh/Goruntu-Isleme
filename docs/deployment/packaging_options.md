# Paketleme Seçenekleri

Bu doküman, FTMC Occupancy uygulamasının Windows ortamında tek çalıştırılabilir dosya veya taşınabilir klasör olarak dağıtılması için PyInstaller seçeneğini değerlendirir. Amaç, offline kurulum dokümanındaki `configs/`, `models/`, `data/` ve `logs/` ayrımını koruyarak sahada güncellenebilir ve yönetilebilir bir paket elde etmektir.

## Önerilen PyInstaller yaklaşımı

PyInstaller için önerilen dağıtım modeli `--onedir` çıktısıdır. `--onefile` tek `.exe` üretse de uygulamayı her başlatmada geçici dizine açar; büyük ONNX model dosyaları, antivirüs taraması ve yazılabilir veri/log dizinleri nedeniyle operasyonel risk oluşturur. Bu nedenle Windows hedef paketinde `.exe` dosyası uygulama kökünde, değiştirilebilir ve büyük dosyalar ise yanında ayrı klasörlerde tutulmalıdır.

Önerilen hedef çıktı:

```text
FTMC-Occupancy/
├── FTMC-Occupancy.exe
├── configs/
│   └── utym_001_cam_001.json
├── models/
│   └── person_detector.onnx
├── data/
│   └── ftmc.sqlite
└── logs/
    └── app.log
```

PyInstaller komutu başlangıç için aşağıdaki gibi tasarlanabilir:

```powershell
pyinstaller --onedir --name FTMC-Occupancy app/main.py
```

Üretim paketi hazırlanırken `dist/FTMC-Occupancy/` klasörüne `configs/`, `models/`, `data/` ve `logs/` dizinleri ayrıca kopyalanmalıdır. Dağıtım betiği bu klasörleri eksikse oluşturmalı, `configs/` ve `models/` içeriklerini kontrollü şekilde güncellemeli, `data/` ve `logs/` içeriğini ise varsayılan olarak korumalıdır.

## 1. Windows için `.exe` üretimi

PyInstaller Windows `.exe` üretimi için uygun bir seçenektir; ancak paket, hedef Windows mimarisiyle uyumlu bir Windows build makinesinde üretilmelidir. Linux veya macOS üzerinde doğrudan Windows `.exe` üretimi bu proje için önerilmez. `opencv-python`, `onnxruntime` ve benzeri native bağımlılıklar işletim sistemi ve mimariye duyarlı olduğundan build ortamı, hedef makinelerle aynı Python ve bağımlılık sürümlerini kullanmalıdır.

Öneriler:

- `--onedir` kullanılmalı; böylece bağımlılıklar, executable ve dış kaynak klasörleri denetlenebilir bir dizin yapısında kalır.
- Build çıktısı temiz bir Windows sanal makinesinde çalıştırılarak `--config`, `--source` ve `--model` parametreleriyle uçtan uca test edilmelidir.
- Paket adı ve sürümü dağıtım klasörü veya arşiv adına eklenmelidir: `FTMC-Occupancy-<surum>-win64.zip`.
- Kurumsal kurulum gerekiyorsa `.zip` yerine MSI veya kurum içi yazılım dağıtım aracı kullanılabilir; PyInstaller yine uygulama payload'ını üretir.

## 2. Model dosyalarının executable içine mi yoksa yanında mı taşınacağı

Model dosyaları executable içine gömülmemeli, `models/` klasöründe executable yanında taşınmalıdır. Mevcut komut satırı varsayılanı kişi tespit modeli için `models/person_detector.onnx` yolunu kullanır; bu düzen PyInstaller `--onedir` paketiyle uyumludur.

Dışarıda tutmanın avantajları:

- ONNX model dosyaları büyük olabilir; executable içine gömülürse build boyutu ve başlatma süresi artar.
- Model güncellemesi için tüm executable'ın yeniden paketlenmesi gerekmez.
- Model lisansı, bütünlük kontrolü ve kurum içi onay süreçleri ayrı yürütülebilir.
- Antivirüs taramasında tek büyük ve sık değişen `.exe` yerine sabit `.exe` + ayrı model dosyası daha yönetilebilir olur.

Dikkat edilmesi gerekenler:

- `models/person_detector.onnx` paketle birlikte gelmelidir.
- Güncelleme mekanizması model dosyasını değiştirirken hash veya imza kontrolü yapmalıdır.
- Model yolu değişirse uygulama `--model` parametresiyle başlatılmalıdır.

## 3. SQLite veritabanı konumu

SQLite veritabanı executable içine veya PyInstaller iç kaynaklarına konulmamalıdır. Yazılabilir ve yedeklenebilir bir dosya olarak `data/ftmc.sqlite` altında tutulmalıdır. Mevcut varsayılan veritabanı URL'si `sqlite:///data/ftmc.sqlite` olduğu için önerilen paket yapısı uygulamanın varsayılan davranışıyla uyumludur.

Operasyonel kararlar:

- Taşınabilir kurulumda veritabanı `FTMC-Occupancy/data/ftmc.sqlite` içinde kalabilir.
- Windows servis veya çok kullanıcılı kurulumda kurum politikası gerektirirse `C:\ProgramData\FTMC-Occupancy\data\ftmc.sqlite` gibi merkezi bir yazılabilir dizin tercih edilebilir.
- Uygulama güncellemeleri `data/` klasörünü silmemeli veya üzerine yazmamalıdır.
- Yedekleme, arşivleme ve erişim yetkileri `data/` klasörü üzerinden yönetilmelidir.

## 4. Config dosyalarının düzenlenebilir kalması

Kamera, UTYM ve ortam ayarlarını içeren JSON config dosyaları executable dışında `configs/` klasöründe kalmalıdır. Bu sayede saha ekipleri kamera kalibrasyonu, masa poligonları ve ortam bazlı parametreleri yeni build beklemeden düzenleyebilir.

Öneriler:

- `configs/` klasörü paketle birlikte örnek veya varsayılan JSON dosyalarıyla gelmelidir.
- Çalıştırma komutu config yolunu açıkça vermelidir: `FTMC-Occupancy.exe --config configs\utym_001_cam_001.json ...`.
- Güncelleme paketleri mevcut config dosyalarını otomatik olarak ezmemelidir.
- Yeni config şeması gerekiyorsa dağıtım notlarında migrasyon adımı veya örnek farklar verilmelidir.
- Config dosyaları üzerinde kurum içi değişiklik takibi gerekiyorsa `configs/` yedekleme kapsamına alınmalıdır.

## 5. Log dosyalarının konumu

Log dosyaları executable içine veya geçici PyInstaller dizinine yazılmamalıdır. Taşınabilir paket için önerilen konum `logs/` klasörüdür. Bu depoda zorunlu bir kalıcı log dosyası yolu tanımlı olmadığından, paketleme veya servis başlatma betiği stdout/stderr çıktısını `logs/app.log` dosyasına yönlendirmelidir.

Örnek PowerShell başlatma yaklaşımı:

```powershell
New-Item -ItemType Directory -Force -Path .\logs | Out-Null
.\FTMC-Occupancy.exe --config .\configs\utym_001_cam_001.json --source .\sample.mp4 --model .\models\person_detector.onnx *> .\logs\app.log
```

Servis olarak çalıştırılan dağıtımlarda loglar aşağıdaki seçeneklerden biriyle yönetilebilir:

- `FTMC-Occupancy/logs/` altında dosya bazlı log.
- `C:\ProgramData\FTMC-Occupancy\logs\` altında merkezi log.
- Kurumsal servis yöneticisinin veya SIEM ajanının topladığı standart servis logları.

Log rotasyonu ayrıca planlanmalıdır; aksi halde uzun süreli kamera izleme senaryolarında `logs/` dizini büyüyebilir.

## 6. Güncelleme mekanizması

PyInstaller paketinde güncelleme, executable ve bağımlılıkların değiştirildiği katman ile saha verilerinin korunduğu katmanı ayırmalıdır. `FTMC-Occupancy.exe` ve PyInstaller bağımlılık klasörleri değiştirilebilir; `configs/`, `models/`, `data/` ve `logs/` ise ayrı kurallarla ele alınmalıdır.

Önerilen güncelleme stratejisi:

1. Yeni sürüm `FTMC-Occupancy-<surum>-win64.zip` olarak hazırlanır.
2. Paket hash'i ve varsa dijital imzası doğrulanır.
3. Uygulama durdurulur.
4. Mevcut `data/`, `logs/` ve saha tarafından değiştirilmiş `configs/` yedeklenir.
5. Yeni executable ve bağımlılıklar kopyalanır.
6. Gerekirse `models/` içeriği hash kontrollü olarak güncellenir.
7. Config şeması değiştiyse migrasyon veya manuel doğrulama yapılır.
8. Uygulama başlatılır ve temel sağlık kontrolü yapılır.

Otomatik güncelleme gerekiyorsa, ana uygulamanın kendisini çalışırken değiştirmesi yerine ayrı bir updater betiği veya kurum içi yazılım dağıtım aracı tercih edilmelidir. Güncelleme hiçbir koşulda `data/ftmc.sqlite` dosyasını varsayılan olarak silmemelidir.

## 7. Antivirüs veya güvenlik politikası etkileri

PyInstaller ile üretilen executable'lar bazı antivirüs ürünlerinde ek incelemeye veya yanlış pozitif uyarılara neden olabilir. Bu risk özellikle `--onefile` paketlerde daha yüksektir; çünkü uygulama başlangıçta kendini geçici dizine açar ve dinamik dosya yükleme davranışı sergiler.

Risk azaltma önerileri:

- `--onedir` tercih edilmelidir.
- Üretim `.exe` dosyası kurum tarafından güvenilen bir sertifika ile imzalanmalıdır.
- Build süreci tekrarlanabilir olmalı; paket hash değerleri dağıtım notlarına eklenmelidir.
- `models/`, `configs/`, `data/` ve `logs/` için gerekli okuma/yazma izinleri en az yetki prensibiyle verilmelidir.
- Uygulama klasörü antivirüs istisnasına alınacaksa bu karar güvenlik ekibi onayıyla ve dosya bütünlüğü kontrolleriyle uygulanmalıdır.
- Offline ortama USB ile aktarımda zararlı yazılım taraması ve kurum içi veri transfer prosedürleri işletilmelidir.

## Sonuç

Bu proje için PyInstaller uygulanabilir bir Windows paketleme seçeneğidir; fakat en güvenli ve bakımı kolay model tek dosyalık `--onefile` yerine taşınabilir `--onedir` dağıtımdır. Hedef çıktı aşağıdaki ayrımı korumalıdır:

```text
FTMC-Occupancy.exe
configs/
models/
data/
logs/
```

Bu yapı model, config, veritabanı ve logların executable'dan bağımsız yönetilmesini sağlar; güncelleme, yedekleme ve güvenlik politikalarını daha öngörülebilir hale getirir.
