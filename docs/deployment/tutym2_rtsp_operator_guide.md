# T.UTYM#2 RTSP Canlı Kamera Operatör Kılavuzu

Bu kılavuz, lokal fotoğraf/video ve kalibrasyon adımları tamamlandıktan sonra T.UTYM#2 için RTSP canlı kamera testine güvenli şekilde hazırlanmayı anlatır. Gerçek RTSP URL, kamera IP adresi, kullanıcı adı veya parola bu repository'ye yazılmamalıdır.

## 1. RTSP Nedir?

RTSP, IP kameradan canlı video akışı almak için kullanılan bir bağlantı yöntemidir. Basitçe kamera görüntüsünü uygulamaya canlı olarak taşır.

RTSP adresi genellikle şuna benzer:

```text
rtsp://kullanici:sifre@kamera-ip-adresi/stream-yolu
```

Bu adres hassas bilgidir. Bu yüzden gerçek RTSP adresi GitHub'a, PR'a, dokümana veya chat ortamına yazılmamalıdır.

## 2. RTSP'ye Ne Zaman Geçilmeli?

RTSP canlı kameraya geçmeden önce şu adımlar tamamlanmış olmalıdır:

```text
[ ] T.UTYM#2 kalibrasyon ekranı açıldı.
[ ] 14 masa lokal fotoğraf üzerinde işaretlendi.
[ ] tutym2_cam_001.local.json üretildi.
[ ] Config dosyası C:\FTMC_FIELD_DATA\configs\ altında duruyor.
[ ] ONNX model dosyası C:\FTMC_FIELD_DATA\models\ altında duruyor.
[ ] Lokal fotoğraf veya video demo testi yapıldı.
[ ] Görüntü paylaşmadan doğrulama raporu dolduruldu.
```

Bu adımlar tamamlanmadan RTSP canlı teste geçmek önerilmez.

## 3. Gerçek RTSP Bilgisi Nereye Yazılmalı?

Gerçek RTSP URL yalnızca lokal Windows saha makinesinde tutulmalıdır.

Önerilen lokal dosya:

```text
C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.rtsp.local.json
```

Bu dosya repository içinde olmamalıdır.

## 4. RTSP Lokal Config Örneği

Repository içinde güvenli bir RTSP template dosyası vardır:

```text
configs/templates/tutym2_cam_001.rtsp.template.json
```

Bu template lokal Windows makinede şu dosyaya kopyalanmalıdır:

```text
C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.rtsp.local.json
```

Aşağıdaki örnek gerçek değer içermez. Gerçek kullanıcı adı, parola, IP ve stream yolu yalnızca lokal dosyada doldurulmalıdır.

```json
{
  "utym_id": "T.UTYM#2",
  "camera_id": "TUTYM2-CAM-001",
  "source_type": "rtsp",
  "stream_url": "rtsp://<USER>:<PASSWORD>@<CAMERA_IP>/<STREAM_PATH>",
  "resolution": {
    "width": 1920,
    "height": 1080
  },
  "tables": []
}
```

`tables` alanı, kalibrasyon sonucunda üretilen 14 masa poligonuyla doldurulmalıdır.

## 5. Güvenli RTSP Hazırlık Kontrolü

| Kontrol | Sonuç |
| --- | --- |
| RTSP URL yalnızca lokal dosyada mı? | Evet / Hayır |
| RTSP URL GitHub'a yazılmadı mı? | Evet / Hayır |
| Kamera IP adresi GitHub'a yazılmadı mı? | Evet / Hayır |
| Kullanıcı adı/parola GitHub'a yazılmadı mı? | Evet / Hayır |
| Config içinde 14 masa poligonu var mı? | Evet / Hayır |
| Lokal foto/video demo daha önce denendi mi? | Evet / Hayır |

Her cevap `Evet` değilse canlı RTSP teste geçilmemelidir.

## 6. İlk RTSP Testinde Ne Ölçülmeli?

İlk canlı kamera testinde görüntü paylaşmadan şu bilgiler not alınmalıdır:

- Kamera bağlantısı kurulabildi mi?
- Görüntü çözünürlüğü 1920x1080 mi?
- FPS kabul edilebilir mi?
- Masa poligonları canlı görüntüde doğru yerde mi?
- Kişi tespiti canlı görüntüde çalışıyor mu?
- Dolu/boş kararları lokal foto/video testine benzer mi?
- Gecikme veya donma var mı?
- Ağ kopması yaşandı mı?

## 7. RTSP Hata Türleri

| Hata | Olası Sebep | İlk Kontrol |
| --- | --- | --- |
| Kamera bağlanmıyor | URL, kullanıcı adı, parola veya ağ erişimi yanlış | RTSP URL lokal olarak doğru mu? |
| Görüntü donuyor | Ağ gecikmesi veya kamera FPS/codec sorunu | Aynı kamera başka yazılımda akıcı mı? |
| FPS düşük | CPU/GPU yetersiz veya model ağır | Lokal video FPS ile karşılaştırın |
| Poligonlar kaymış | Canlı kamera açısı kalibrasyon fotoğrafından farklı | Kalibrasyon yeniden yapılmalı |
| Dolu masa boş görünüyor | Model kişiyi kaçırıyor veya poligon yanlış | False Empty olarak raporlayın |

## 8. Paylaşılabilir RTSP Test Raporu

RTSP testinden sonra gerçek görüntü veya URL paylaşmadan şu formatta rapor verilebilir:

```text
Test tipi: RTSP canlı
Kamera: TUTYM2-CAM-001
Çözünürlük: 1920x1080
Bağlantı kuruldu mu: Evet/Hayır
Ortalama FPS: ...
Gecikme/donma: Var/Yok
Masa bazlı doğruluk: ...
False Empty sayısı: ...
False Occupied sayısı: ...
Belirsiz karar sayısı: ...
RTSP URL paylaşılmadı: Evet
```

## 9. Sonraki Kod Adımı

Güvenli RTSP runner eklenmiştir. Yetkili BT/geliştirme sorumlusu canlı test için şu komutu kullanabilir:

```powershell
python scripts/run_tutym2_rtsp_demo.py `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.rtsp.local.json `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx `
  --report-output C:\FTMC_FIELD_DATA\reports\rtsp_demo_result.json
```

İlk bağlantı testi için dedektör çalıştırmadan birkaç frame okumak istenirse şu ek parametre kullanılabilir:

```powershell
python scripts/run_tutym2_rtsp_demo.py `
  --config C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.rtsp.local.json `
  --model C:\FTMC_FIELD_DATA\models\person_detector.onnx `
  --report-output C:\FTMC_FIELD_DATA\reports\rtsp_connection_test.json `
  --connection-test-frames 10
```

Runner gerçek RTSP URL'yi yalnızca lokal config dosyasından okur, rapora URL veya tam lokal path yazmaz, görüntü kaydetmez ve bağlantı durumunu güvenli rapora işler.

Bağlantı testi raporunu yorumlamak için `docs/deployment/tutym2_rtsp_connection_report_guide.md` kılavuzunu kullanın.
