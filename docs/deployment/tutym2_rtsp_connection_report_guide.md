# T.UTYM#2 RTSP Bağlantı Raporu Okuma Kılavuzu

Bu kılavuz, `rtsp_connection_test.json` dosyası üretildikten sonra raporu gerçek görüntü, RTSP URL veya kamera bilgisi paylaşmadan nasıl yorumlayacağınızı anlatır.

## 1. Bu Rapor Ne İşe Yarar?

RTSP bağlantı testi, model veya insan tespiti çalıştırmadan yalnızca canlı kamera bağlantısını kontrol eder.

Testin amacı şudur:

```text
Kameraya bağlanabiliyor muyuz?
Kameradan frame okuyabiliyor muyuz?
İlk frame çözünürlüğü beklenen gibi mi?
Ortalama FPS kabul edilebilir mi?
```

Bu rapor görüntü veya video içermez. Raporun amacı bağlantı sağlığını güvenli şekilde ölçmektir.

## 2. Rapor Dosyası Nerede Olmalı?

Önerilen lokal rapor dosyası:

```text
C:\FTMC_FIELD_DATA\reports\rtsp_connection_test.json
```

Bu dosya gerçek görüntü içermez. Yine de kurum politikasına göre kontrollü paylaşılmalıdır.

## 3. Rapor İçinde Ne Olur?

Başarılı bir bağlantı testi raporunda genel olarak şu alanlar beklenir:

```json
{
  "generated_at": "...",
  "site": "T.UTYM#2",
  "status": "connection_test_completed",
  "camera_id": "TUTYM2-CAM-001",
  "config": {
    "name": "tutym2_cam_001.rtsp.local.json",
    "extension": ".json"
  },
  "model": {
    "name": "person_detector.onnx",
    "extension": ".onnx"
  },
  "details": {
    "requested_frames": 10,
    "frames_read": 10,
    "first_frame_shape": {
      "height": 1080,
      "width": 1920
    },
    "elapsed_seconds": 1.2,
    "average_fps": 8.33
  }
}
```

Gerçek değerler kameraya, ağ durumuna ve bilgisayar performansına göre değişebilir.

## 4. Güvenlik Kontrolü

Raporu paylaşmadan önce şunları kontrol edin:

| Kontrol | Beklenen |
| --- | --- |
| RTSP URL var mı? | Hayır |
| Kamera IP adresi var mı? | Hayır |
| Kullanıcı adı/parola var mı? | Hayır |
| Gerçek görüntü veya video var mı? | Hayır |
| Tam lokal path var mı? | Hayır |
| Sadece dosya adı/uzantı ve sayısal metrik var mı? | Evet |

Rapor içinde `rtsp://`, gerçek IP adresi, kullanıcı adı veya parola görürseniz raporu paylaşmayın.

## 5. `status` Alanı Nasıl Yorumlanır?

| Status | Anlamı | Ne yapılmalı? |
| --- | --- | --- |
| `connection_test_started` | Test başladı | Son raporu bekleyin |
| `connection_test_completed` | Test başarıyla tamamlandı | `frames_read`, çözünürlük ve FPS değerlerini kontrol edin |
| `connection_test_failed` | Bağlantı veya frame okuma başarısız | RTSP URL, ağ, kamera ve yetki bilgileri lokal olarak kontrol edilmeli |
| `rtsp_preflight_failed` | Test başlamadan girişler hatalı | Config/model/report path veya placeholder kontrol edilmeli |

## 6. `requested_frames` ve `frames_read` Nasıl Yorumlanır?

| Alan | Anlamı |
| --- | --- |
| `requested_frames` | Testte okunmak istenen frame sayısı |
| `frames_read` | Gerçekte okunabilen frame sayısı |

Örnek yorum:

```text
requested_frames = 10
frames_read = 10
```

Bu iyi sonuçtur. Kamera 10 frame’in tamamını vermiştir.

```text
requested_frames = 10
frames_read = 0
```

Bu kötü sonuçtur. Kamera bağlantısı kurulmamış veya frame okunamamıştır.

```text
requested_frames = 10
frames_read = 3
```

Bu kısmi sonuçtur. Kamera bağlantısı kararsız olabilir.

## 7. `first_frame_shape` Nasıl Yorumlanır?

Bu alan ilk okunan frame’in çözünürlüğünü gösterir.

Beklenen değer T.UTYM#2 için şudur:

```json
"first_frame_shape": {
  "height": 1080,
  "width": 1920
}
```

| Durum | Yorum |
| --- | --- |
| `height=1080`, `width=1920` | Beklenen 1080P görüntü |
| Daha düşük çözünürlük | Kamera stream profili düşük olabilir |
| Boş `{}` | Frame şekli okunamamış olabilir |

Eğer çözünürlük beklenenden farklıysa kamera stream profili veya RTSP stream path lokal olarak kontrol edilmelidir.

## 8. `average_fps` Nasıl Yorumlanır?

`average_fps`, test sırasında yaklaşık saniye başına kaç frame okunduğunu gösterir.

İlk yorum için basit eşikler:

| Ortalama FPS | Yorum |
| ---: | --- |
| 10 FPS ve üzeri | İyi başlangıç |
| 5 - 10 FPS | Kabul edilebilir olabilir; model performansı ayrıca ölçülmeli |
| 1 - 5 FPS | Zayıf; ağ, kamera stream veya bilgisayar performansı incelenmeli |
| 0 FPS | Bağlantı/frame okuma başarısız |

Bu değer yalnızca bağlantı testidir. Model çalışınca FPS daha düşük olabilir.

## 9. Başarılı RTSP Bağlantı Testi İçin Minimum Beklenti

İlk başarılı bağlantı testi için minimum beklenti:

```text
status = connection_test_completed
frames_read = requested_frames
first_frame_shape.width = 1920
first_frame_shape.height = 1080
average_fps >= 5
```

Bu koşullar sağlanırsa canlı RTSP demo testine geçilebilir.

## 10. Sorun Giderme

| Belirti | Olası sebep | İlk aksiyon |
| --- | --- | --- |
| `rtsp_preflight_failed` | Config/model/report yolu hatalı veya placeholder kalmış | Lokal config dosyasını kontrol edin |
| `connection_test_failed` | Kamera bağlantısı kurulamadı veya frame okunamadı | RTSP URL, ağ erişimi, kullanıcı adı/parola lokal kontrol edilmeli |
| `frames_read = 0` | Kamera frame vermiyor | Aynı RTSP URL başka güvenli kamera yazılımında denenmeli |
| Çözünürlük düşük | Yanlış stream profili | Kamera stream path/profil ayarı kontrol edilmeli |
| FPS düşük | Ağ, codec, kamera veya bilgisayar performansı | Daha düşük çözünürlük veya farklı stream profili denenebilir |

## 11. Sonraki Karar

Rapor okunduktan sonra aşağıdaki kararlardan biri seçilir:

```text
[ ] RTSP canlı demo testine geçilebilir.
[ ] RTSP URL/ağ/yetki bilgileri lokal olarak düzeltilmeli.
[ ] Kamera stream profili değiştirilmeli.
[ ] Kalibrasyon yeniden yapılmalı.
[ ] Model performans testine geçilmeli.
```

## 12. Paylaşılabilir Özet Formatı

Gerçek raporu paylaşmak yerine şu özet kullanılabilir:

```text
RTSP bağlantı testi: Başarılı/Başarısız
requested_frames: 10
frames_read: 10
çözünürlük: 1920x1080
average_fps: 8.33
RTSP URL paylaşılmadı: Evet
Sonraki karar: RTSP canlı demo testine geçilebilir
```
