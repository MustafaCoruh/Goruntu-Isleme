# T.UTYM#2 Dashboard Veri Sözleşmesi

Bu doküman, ilk operatör dashboard'unun hangi güvenli JSON verilerini okuyacağını ve bu verilerden ekran durumlarını nasıl üreteceğini tanımlar.

Amaç:

```text
Dashboard UI koduna geçmeden önce veri alanlarını sabitlemek.
Eksik veya hatalı JSON durumunda dashboard'un ne yapacağını belirlemek.
Renk ve uyarı kurallarını standartlaştırmak.
Gerçek görüntü, RTSP URL, IP, credential veya tam lokal path kullanılmasını engellemek.
```

Bu sözleşme gerçek görüntü, video, RTSP URL, IP adresi, kullanıcı adı/parola veya kişisel veri içermez.

## 1. Dashboard'un Okuyacağı Güvenli JSON Kaynakları

İlk dashboard aşağıdaki güvenli JSON çıktılarından beslenecektir.

| Veri kaynağı | Örnek dosya adı | Üreten araç |
| --- | --- | --- |
| Offline readiness | `offline_readiness.json` | `app/offline_readiness.py` |
| Config doğrulama özeti | `config_validation_summary.json` | `app/tutym2_config_validator.py` |
| RTSP bağlantı raporu | `rtsp_connection_test.json` | `app/rtsp_field_demo.py` |
| Masa doğruluk raporu | `tutym2_table_accuracy_report.json` | `app/table_accuracy_report.py` |
| Canlı demo özeti | `rtsp_demo_result.json` | `app/rtsp_field_demo.py` |

Dashboard bu dosyaları lokal rapor klasöründen okuyabilir:

```text
C:\FTMC_FIELD_DATA\reports\
```

Bu path dashboard ekranında veya raporda tam path olarak paylaşılmamalıdır.

## 2. Ortak Güvenlik Kuralı

Dashboard'un okuduğu tüm JSON verilerinde şu bilgiler bulunmamalıdır:

```text
RTSP URL
Kamera IP adresi
Kullanıcı adı/parola
Gerçek görüntü
Gerçek video
Kişi adı
Yüz görüntüsü
Tam lokal path
```

Dashboard bir JSON içinde bu tür veri görürse:

```text
1. İlgili raporu güvensiz saymalı.
2. Operatöre kırmızı uyarı göstermeli.
3. Raporu dışa aktarmamalı.
4. Teknik sorumluya haber verilmesini önermeli.
```

## 3. Dashboard Üst Durum Modeli

Dashboard üst çubuğu için önerilen birleşik veri modeli:

```json
{
  "site": "T.UTYM#2",
  "camera_id": "TUTYM2-CAM-001",
  "mode": "rtsp_live",
  "connection_status": "connected",
  "overall_status": "normal",
  "average_fps": 8.3,
  "last_update": "YYYY-MM-DDTHH:MM:SS"
}
```

İzinli değerler:

| Alan | İzinli değerler |
| --- | --- |
| `mode` | `local_photo`, `local_video`, `rtsp_connection_test`, `rtsp_live`, `not_started` |
| `connection_status` | `connected`, `disconnected`, `not_tested`, `unknown` |
| `overall_status` | `normal`, `warning`, `critical`, `not_ready` |

## 4. Renk Kuralları

| Durum | Renk | Kullanım |
| --- | --- | --- |
| `normal` | Yeşil | Her şey beklenen seviyede |
| `warning` | Sarı | Teste devam edilebilir ama kontrol gerekir |
| `critical` | Kırmızı | Canlı teste/demoya devam edilmemeli |
| `not_ready` | Gri | Henüz test yapılmadı veya veri yok |

Masa kartları için:

| Masa durumu | Renk |
| --- | --- |
| `occupied` | Kırmızı / koyu turuncu |
| `empty` | Yeşil |
| `unknown` | Sarı |
| `no_data` | Gri |

## 5. Offline Readiness JSON Alanları

Dashboard için gereken minimum alanlar:

```json
{
  "report_type": "offline_readiness",
  "site": "T.UTYM#2",
  "overall_status": "pass",
  "checks": [],
  "safety": {
    "contains_rtsp_url": false,
    "contains_credentials": false,
    "contains_image_or_video": false,
    "contains_full_local_path": false
  }
}
```

Dashboard yorumu:

| `overall_status` | Dashboard durumu |
| --- | --- |
| `pass` | Normal |
| `warn` | Uyarı |
| `fail` | Kritik |
| Eksik dosya | Hazır değil |

## 6. Config Validation Summary JSON Alanları

Dashboard için gereken minimum alanlar:

```json
{
  "utym_id": "T.UTYM#2",
  "camera_id": "TUTYM2-CAM-001",
  "source_type": "rtsp",
  "resolution": {
    "width": 1920,
    "height": 1080
  },
  "table_count": 14,
  "stream_url_mode": "local_only_placeholder",
  "status": "valid"
}
```

Dashboard yorumu:

| Alan | Beklenen |
| --- | --- |
| `status` | `valid` |
| `table_count` | `14` |
| `resolution.width` | `1920` |
| `resolution.height` | `1080` |

Eğer `status != valid` veya masa sayısı 14 değilse config paneli kırmızı olmalıdır.

## 7. RTSP Connection Report JSON Alanları

Dashboard için gereken minimum alanlar:

```json
{
  "site": "T.UTYM#2",
  "status": "connection_test_completed",
  "camera_id": "TUTYM2-CAM-001",
  "details": {
    "requested_frames": 10,
    "frames_read": 10,
    "first_frame_shape": {
      "height": 1080,
      "width": 1920
    },
    "average_fps": 8.3
  }
}
```

Dashboard yorumu:

| Koşul | Dashboard sonucu |
| --- | --- |
| `status = connection_test_completed` ve `frames_read = requested_frames` | Bağlı |
| `frames_read = 0` | Kopuk / Kritik |
| `0 < frames_read < requested_frames` | Kararsız / Uyarı |
| Çözünürlük 1920x1080 değil | Uyarı |
| `average_fps < 5` | Uyarı |

## 8. Masa Doğruluk Raporu JSON Alanları

Dashboard için gereken minimum alanlar:

```json
{
  "report_type": "table_accuracy_evaluation",
  "site": "T.UTYM#2",
  "camera_id": "TUTYM2-CAM-001",
  "summary": {
    "table_count": 14,
    "tp": 7,
    "tn": 5,
    "fp": 1,
    "fn": 1,
    "unk": 0,
    "accuracy": 0.8571
  },
  "tables": []
}
```

Dashboard yorumu:

| Koşul | Dashboard sonucu |
| --- | --- |
| `accuracy >= 0.90` | Normal |
| `0.80 <= accuracy < 0.90` | Uyarı ama prototip için kabul edilebilir |
| `accuracy < 0.80` | Kritik / iyileştirme gerekli |
| `fn > 2` | Kritik |
| `fp > 2` | Uyarı veya kritik |
| `unk > 2` | Uyarı |

## 9. Masa Kartı Veri Modeli

Dashboard içinde her masa şu modele çevrilmelidir:

```json
{
  "table_id": "table_01",
  "display_name": "Masa 01",
  "state": "occupied",
  "confidence": 0.91,
  "label": "TP",
  "color": "red_or_orange",
  "warning": null
}
```

Alan açıklamaları:

| Alan | Açıklama |
| --- | --- |
| `table_id` | JSON'daki masa ID |
| `display_name` | Operatöre gösterilecek ad |
| `state` | `occupied`, `empty`, `unknown`, `no_data` |
| `confidence` | 0.0 - 1.0 arası değer veya null |
| `label` | TP/TN/FP/FN/UNK veya null |
| `color` | Dashboard renk eşlemesi |
| `warning` | Operatöre kısa güvenli uyarı |

## 10. Uyarı Üretme Kuralları

Dashboard aşağıdaki uyarıları üretmelidir:

| Kural | Uyarı |
| --- | --- |
| Offline readiness `fail` | Kurulum hazır değil. Saha demosuna geçmeyin. |
| Config geçersiz | Config doğrulanamadı. 14 masa ve çözünürlük kontrol edilmeli. |
| RTSP `frames_read = 0` | Kamera bağlantısı yok veya frame okunamıyor. |
| FPS `< 5` | FPS düşük. Ağ, stream profili veya GPU kontrol edilmeli. |
| Accuracy `< 0.80` | Model doğruluğu düşük. Kalibrasyon/model incelenmeli. |
| FN `> 2` | Dolu masalar boş sanılıyor olabilir. Kritik kontrol gerekli. |
| Safety alanında `true` var | Rapor güvenli değil. Paylaşmayın. |

## 11. Eksik Dosya Davranışı

Dashboard beklenen JSON dosyasını bulamazsa sistemi çökertmemelidir.

Önerilen davranış:

```text
Dosya yok -> ilgili panel gri / not_ready
Alan eksik -> ilgili panel sarı / warning
JSON parse edilemiyor -> ilgili panel kırmızı / critical
Safety ihlali -> ilgili panel kırmızı / critical
```

## 12. Dashboard Birleşik Durum Hesabı

Genel durum şu öncelikle hesaplanmalıdır:

```text
Herhangi critical varsa -> overall_status = critical
Critical yok ama warning varsa -> overall_status = warning
Tüm temel kontroller normal ise -> overall_status = normal
Hiç veri yoksa -> overall_status = not_ready
```

## 13. Güvenli Dashboard State Örneği

Dashboard'un kendi içinde kullanabileceği güvenli birleşik state örneği:

```json
{
  "site": "T.UTYM#2",
  "camera_id": "TUTYM2-CAM-001",
  "overall_status": "warning",
  "connection_status": "connected",
  "average_fps": 8.3,
  "table_summary": {
    "total": 14,
    "occupied": 6,
    "empty": 7,
    "unknown": 1,
    "no_data": 0
  },
  "warnings": [
    "Masa 03 belirsiz. Kalibrasyon veya görüş açısı kontrol edilebilir."
  ]
}
```

Bu state gerçek görüntü, RTSP URL, IP, credential veya tam lokal path içermez.

## 14. Sonraki Teknik Adım

Bu sözleşmeden sonra sıradaki teknik adım küçük bir dashboard state builder modülü eklemektir.

Bu modül:

```text
Güvenli JSON raporlarını okuyacak.
Eksik/hatalı dosyaları yakalayacak.
Masa durumlarını normalize edecek.
Renk ve uyarı kurallarını uygulayacak.
Tek bir güvenli dashboard state JSON'u üretecek.
```

Bu modül hazırlandıktan sonra gerçek UI kodu bu state'i okuyarak daha kolay geliştirilebilir.
