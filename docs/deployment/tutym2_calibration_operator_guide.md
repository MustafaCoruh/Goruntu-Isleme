# T.UTYM#2 Kalibrasyon Operatör Kılavuzu

Bu kılavuz, T.UTYM#2 için gerçek görüntüleri paylaşmadan 14 masanın görüntü üzerindeki konumlarını işaretleyip lokal config dosyası üretmeyi anlatır. Kodlama, GitHub veya Python bilmeyen operatörler için hazırlanmıştır.

## 1. Kalibrasyon Ne Demektir?

Kamera görüntüsü bilgisayar için yalnızca piksellerden oluşur. Bilgisayar, hangi piksel alanının hangi masaya ait olduğunu kendiliğinden bilemez.

Kalibrasyon şu bilgiyi üretir:

```text
Masa 1 görüntüde şu dörtgen alan.
Masa 2 görüntüde şu dörtgen alan.
...
Masa 14 görüntüde şu dörtgen alan.
```

Bu bilgi JSON config dosyası olarak kaydedilir. İlk T.UTYM#2 hedef dosyası:

```text
C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json
```

## 2. Güvenlik Kuralları

Kalibrasyon sırasında aşağıdaki verileri GitHub'a, PR'a veya chat ortamına eklemeyin:

- Gerçek T.UTYM#2 fotoğrafı.
- Gerçek T.UTYM#2 videosu.
- Gerçek RTSP URL.
- Kamera IP adresi.
- Kamera kullanıcı adı/parolası.
- Katılımcı veya ekran bilgisi içeren görüntüler.
- Lokal üretilen `tutym2_cam_001.local.json` dosyası kurum politikası hassas kabul ediyorsa.

Kalibrasyon gerçek görüntü üzerinde lokal Windows makinede yapılmalıdır.

## 3. Gerekli Dosyalar ve Klasörler

Lokal Windows makinede şu klasör yapısı olmalıdır:

```text
C:\FTMC_FIELD_DATA\
├── input\
│   ├── photos\
│   └── videos\
├── models\
├── configs\
└── reports\
```

Kalibrasyon için en pratik başlangıç, gerçek kamera görüntüsünden alınmış tek bir fotoğraftır:

```text
C:\FTMC_FIELD_DATA\input\photos\calibration_reference.jpg
```

Dosya adı örnektir. Gerçek dosya adını paylaşmayın.

## 4. Kalibrasyon Ekranını Açma

Kalibrasyon ekranı web arayüzünün bir parçasıdır. Yetkili BT/geliştirme sorumlusu uygulamayı başlattıktan sonra tarayıcıdan şu adres açılır:

```text
http://127.0.0.1:8000/ui/calibration.html
```

Terminal erişiminiz yoksa bu adresi açma ve uygulamayı başlatma işlemini yetkili kişi yapmalıdır.

## 5. Ekranda Görmeniz Gereken Varsayılanlar

Kalibrasyon ekranında şu değerler görünmelidir:

```text
Başlık: T.UTYM#2 Masa Kalibrasyonu
Kapasite: 1
UTYM ID: T.UTYM#2
Kamera ID: TUTYM2-CAM-001
Hedef masa sayısı: 0 / 14
```

Bu değerler farklıysa yanlış branch veya eski sürüm açılmış olabilir.

## 6. Fotoğraf Yükleme

1. `Örnek fotoğraf yükle` alanına tıklayın.
2. Lokal Windows klasöründen kalibrasyon fotoğrafını seçin.
3. Fotoğraf ekranda görünmelidir.
4. Fotoğrafta masalar net görünmüyorsa daha uygun bir kare seçin.

Gerçek fotoğraf yalnızca lokal makinede kalmalıdır.

## 7. Masa İşaretleme Mantığı

Her masa için görüntü üzerinde en az 3 nokta seçilir. Pratikte dörtgen masa alanı için 4 nokta önerilir.

Önerilen nokta sırası:

```text
1. Sol üst köşe
2. Sağ üst köşe
3. Sağ alt köşe
4. Sol alt köşe
```

Masa alanı tam dikdörtgen görünmüyorsa kameradaki perspektife göre masayı çevreleyen poligon noktalarını seçin.

## 8. Masa Ekleme Adımları

Her masa için şu adımları uygulayın:

1. `Masa adı` alanına masa adını yazın.
   - Örnek: `Masa 1`
2. `Kapasite` alanının `1` olduğundan emin olun.
3. Görsel üzerinde masa köşelerine tıklayın.
4. En az 3 nokta eklendikten sonra `Masayı Ekle` butonuna basın.
5. Sağ panelde masanın eklendiğini kontrol edin.
6. Üst/alt durum yazısında sayaç ilerlemelidir:

```text
T.UTYM#2 hedef masa sayısı: 1 / 14
```

Bu adımları `Masa 14` eklenene kadar tekrarlayın.

## 9. Hata Yaparsanız Ne Yapmalısınız?

| Durum | Ne yapmalısınız? |
| --- | --- |
| Yanlış noktaya tıkladım | `Son Noktayı Sil` butonuna basın |
| Poligonu tamamen yanlış çizdim | `Poligonu Temizle` butonuna basın |
| Yanlış masayı ekledim | Sağ panelde ilgili masanın `Sil` butonuna basın |
| 14 masadan fazla ekleyemiyorum | Bu beklenen davranış; T.UTYM#2 hedefi 14 masadır |
| Masa adı girmeyi unuttum | Sistem uyarı verir; masa adı girip tekrar deneyin |

## 10. 14 Masa Tamamlanınca

Sayaç şu hale gelmelidir:

```text
T.UTYM#2 hedef masa sayısı: 14 / 14
```

Bu noktada yeni masa ekleme butonu devre dışı kalabilir. Bu beklenen davranıştır.

## 11. JSON İndirme

14 masa tamamlandıktan sonra `tutym2_cam_001.local.json İndir` butonuna basın.

İndirilen dosyanın adı şu olmalıdır:

```text
tutym2_cam_001.local.json
```

Bu dosyayı şu klasöre koyun:

```text
C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json
```

## 12. Config İçinde Ne Olmalı?

JSON dosyasının içinde genel olarak şu bilgiler bulunmalıdır:

```json
{
  "utym_id": "T.UTYM#2",
  "camera_id": "TUTYM2-CAM-001",
  "resolution": {
    "width": 1920,
    "height": 1080
  },
  "tables": [
    {
      "table_id": "T-001",
      "name": "Masa 1",
      "capacity": 1,
      "polygon": [[...], [...], [...], [...]]
    }
  ]
}
```

`tables` listesinde 14 masa olmalıdır.

## 13. Kalibrasyon Sonrası İlk Kontrol

Config üretildikten sonra gerçek görüntü paylaşmadan şu kontrol listesini doldurun:

```text
UTYM ID doğru mu? Evet/Hayır
Kamera ID doğru mu? Evet/Hayır
Masa sayısı 14 mü? Evet/Hayır
Tüm kapasiteler 1 mi? Evet/Hayır
Masa poligonları görüntüde doğru yerde mi? Evet/Hayır
Dosya C:\FTMC_FIELD_DATA\configs\ altında mı? Evet/Hayır
Gerçek görüntü veya RTSP URL paylaşılmadı mı? Evet/Hayır
```

## 14. Sonraki Adım

Kalibrasyon config dosyası hazırlandıktan sonra lokal fotoğraf veya video demosu çalıştırılır:

```text
scripts/run_tutym2_local_demo.py
```

Bu komutu terminal erişimi olan yetkili BT/geliştirme sorumlusu çalıştırmalıdır.
