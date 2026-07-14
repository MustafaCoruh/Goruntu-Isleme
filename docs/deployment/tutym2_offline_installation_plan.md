# T.UTYM#2 Offline Kurulum ve Hazırlık Planı

Bu plan, programın internet olmayan saha bilgisayarında güvenli şekilde kurulup çalıştırılabilmesi için hazırlanmıştır.

Amaç:

```text
Geliştirme bilgisayarında paket hazırlanır.
Saha bilgisayarında internet olmadan kurulum yapılır.
Model, config ve rapor klasörleri lokal tutulur.
Gerçek RTSP URL, görüntü ve credential repo'ya girmez.
Kurulumdan sonra güvenli readiness check çalıştırılır.
```

## 1. Klasör Yapısı

Saha bilgisayarında önerilen lokal kök klasör:

```text
C:\FTMC_FIELD_DATA\
```

Alt klasörler:

```text
C:\FTMC_FIELD_DATA\configs\
C:\FTMC_FIELD_DATA\inputs\
C:\FTMC_FIELD_DATA\models\
C:\FTMC_FIELD_DATA\reports\
```

Bu klasörler repo dışında kalmalıdır.

## 2. Offline Pakette Olması Gerekenler

| İçerik | Açıklama |
| --- | --- |
| Uygulama kodu | GitHub'dan gelen repo içeriği |
| Python 3.11.x kurulumu veya kurum onaylı Python | Kullanıcıda 3.11.9 olduğu biliniyor |
| Python wheel/dependency paketi | İnternetsiz kurulum için önceden hazırlanır |
| Model dosyası | Lokal `models` klasöründe tutulur, repo'ya eklenmez |
| Config template dosyaları | Repo'dan gelir |
| Lokal config dosyaları | Sahada üretilir, repo'ya eklenmez |
| Operatör kılavuzları | Repo'dan gelir |

## 3. Offline Pakette Olmaması Gerekenler

```text
Gerçek RTSP URL
Kamera IP adresi
Kamera kullanıcı adı/parolası
Gerçek kamera görüntüsü
Gerçek video kaydı
Yetkisiz kişisel veri
```

## 4. Kurulum Sonrası Güvenli Kontrol

Bu PR ile güvenli readiness check scripti eklenmiştir:

```text
scripts/check_tutym2_offline_readiness.py
```

Bu script kamera açmaz, RTSP bağlantısı kurmaz, görüntü okumaz. Sadece temel ortam hazırlığını kontrol eder.

Kontrol ettiği şeyler:

```text
Python sürümü uygun mu?
Temel Python modülleri var mı?
Opsiyonel runtime modülleri görünüyor mu?
C:\FTMC_FIELD_DATA alt klasörleri var mı?
Config dosyası var mı?
Model dosyası var mı?
Güvenli readiness raporu yazılabiliyor mu?
```

## 5. Örnek Komut

Yetkili teknik kişi saha bilgisayarında şu mantıkta çalıştırabilir:

```powershell
python scripts/check_tutym2_offline_readiness.py `
  --field-root C:\FTMC_FIELD_DATA `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx `
  --report-output C:\FTMC_FIELD_DATA\reports\offline_readiness.json
```

Rapor güvenli özet içerir; RTSP URL, görüntü, credential veya tam lokal path yazmaz.

## 6. Sonraki Karar

Readiness sonucu:

```text
pass -> İlk lokal/RTSP testlere geçilebilir.
warn -> Eksik opsiyonel modül veya klasör olabilir; teknik kişi kontrol etmeli.
fail -> Kurulum tamamlanmadan saha demosuna geçilmemeli.
```

## 7. Offline Paket Manifesti

Saha bilgisayarına dosya taşımadan önce paket içeriği ayrıca manifest ile kontrol edilmelidir.

İlgili doküman:

```text
docs/deployment/tutym2_offline_package_manifest.md
```

İlgili güvenli template:

```text
configs/templates/tutym2_offline_package_manifest.template.json
```

İlgili validator:

```text
scripts/validate_tutym2_offline_package_manifest.py
```

Bu kontrol, offline pakette gerekli repo dosyalarının bulunduğunu ve manifest içinde gerçek RTSP URL, kamera IP, credential, gerçek medya veya tam lokal path yazılmadığını doğrulamak için kullanılır.
