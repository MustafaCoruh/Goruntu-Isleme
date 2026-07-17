# T.UTYM#2 Masa Bazlı Doğruluk Raporu JSON Formatı

Bu doküman, T.UTYM#2 model performans değerlendirmesinin makine tarafından okunabilir güvenli JSON formatını tanımlar.

Amaç:

```text
Model performans sonucunu standart JSON olarak tutmak.
Dashboard veya raporlama modülünün bu sonucu okuyabilmesini sağlamak.
Gerçek görüntü, video, RTSP URL, IP adresi, kullanıcı adı/parola veya kişisel veri eklenmesini engellemek.
```

Bu format, `docs/validation/tutym2_model_performance_evaluation_template.md` dosyasındaki insan tarafından doldurulan şablonun JSON karşılığıdır.

## 1. Rapor Dosya Adı Önerisi

Önerilen lokal rapor dosyası:

```text
C:\FTMC_FIELD_DATA\reports\tutym2_table_accuracy_report.json
```

Bu dosya repo'ya eklenmemelidir. Gerçek saha sonucu lokal ve kontrollü ortamda kalmalıdır.

Repo içinde yalnızca güvenli örnek/template formatı tutulabilir.

## 2. Güvenlik Kuralları

Bu JSON raporda şunlar kesinlikle olmamalıdır:

```text
RTSP URL
Kamera IP adresi
Kullanıcı adı/parola
Gerçek görüntü veya video
Tam lokal dosya path'i
Kişi adı
Yüz görüntüsü veya yüz tanımlayıcı bilgi
Hava aracı veya uçuş testine ait yetkisiz hassas bilgi
```

Raporda sadece aşağıdaki güvenli bilgiler yer almalıdır:

```text
UTYM/site kodu
Kamera ID
Dosya adları
Model versiyonu
Masa ID'leri
Dolu/boş karar özetleri
TP/TN/FP/FN/UNK sayıları
Doğruluk metrikleri
Güvenli teknik notlar
```

## 3. Üst Seviye JSON Yapısı

Raporun önerilen üst seviye alanları:

```json
{
  "report_type": "table_accuracy_evaluation",
  "schema_version": "1.0",
  "site": "T.UTYM#2",
  "camera_id": "TUTYM2-CAM-001",
  "created_at": "YYYY-MM-DDTHH:MM:SS",
  "evaluation_context": {},
  "inputs": {},
  "summary": {},
  "tables": [],
  "decision": {},
  "safety": {}
}
```

## 4. `evaluation_context` Alanı

Bu alan test koşullarını açıklar.

```json
"evaluation_context": {
  "test_type": "local_video",
  "lighting": "normal",
  "occupancy_level": "medium",
  "camera_angle_changed": false,
  "calibration_recent": true,
  "duration_minutes": 5,
  "average_fps": 8.3
}
```

Önerilen değerler:

| Alan | Açıklama |
| --- | --- |
| `test_type` | `local_video` veya `rtsp_live` |
| `lighting` | `normal`, `dim`, `bright`, `mixed` |
| `occupancy_level` | `empty`, `low`, `medium`, `high` |
| `camera_angle_changed` | Kamera açısı değiştiyse `true` |
| `calibration_recent` | Kalibrasyon güncelse `true` |
| `duration_minutes` | Test süresi |
| `average_fps` | Ortalama FPS |

## 5. `inputs` Alanı

Bu alan yalnızca güvenli dosya adlarını içerir. Tam lokal path yazılmaz.

```json
"inputs": {
  "config_name": "tutym2_cam_001.local.json",
  "model_name": "person_detector.onnx",
  "model_version": "initial-field-test"
}
```

Yasak örnek:

```json
"config_path": "C:\\FTMC_FIELD_DATA\\configs\\tutym2_cam_001.local.json"
```

Tam path yerine sadece dosya adı kullanılmalıdır.

## 6. `summary` Alanı

Bu alan toplam metrikleri içerir.

```json
"summary": {
  "table_count": 14,
  "tp": 7,
  "tn": 5,
  "fp": 1,
  "fn": 1,
  "unk": 0,
  "correct": 12,
  "incorrect": 2,
  "evaluated": 14,
  "accuracy": 0.8571
}
```

Hesaplama kuralları:

```text
correct = tp + tn
incorrect = fp + fn
evaluated = table_count - unk
accuracy = correct / evaluated
```

Eğer `evaluated = 0` ise `accuracy` null olmalıdır.

## 7. `tables` Alanı

Her masa için ayrı kayıt tutulur.

```json
"tables": [
  {
    "table_id": "table_01",
    "ground_truth": "occupied",
    "prediction": "occupied",
    "label": "TP",
    "confidence": 0.91,
    "safe_note": "Normal görünüm."
  },
  {
    "table_id": "table_02",
    "ground_truth": "empty",
    "prediction": "occupied",
    "label": "FP",
    "confidence": 0.72,
    "safe_note": "Sandalye/masa kenarı etkisi olabilir."
  }
]
```

Alan kuralları:

| Alan | İzinli değerler |
| --- | --- |
| `table_id` | `table_01` ... `table_14` |
| `ground_truth` | `occupied`, `empty` |
| `prediction` | `occupied`, `empty`, `unknown` |
| `label` | `TP`, `TN`, `FP`, `FN`, `UNK` |
| `confidence` | `0.0` ile `1.0` arasında sayı veya `null` |
| `safe_note` | Görüntü/kişi/IP/RTSP içermeyen kısa teknik not |

## 8. `decision` Alanı

Değerlendirme sonunda alınan karar burada tutulur.

```json
"decision": {
  "prototype_ready": true,
  "recommended_next_action": "Proceed to longer RTSP live validation.",
  "requires_recalibration": false,
  "requires_model_change": false,
  "requires_camera_adjustment": false
}
```

## 9. `safety` Alanı

Bu alan raporun hassas veri içermediğini açıkça belirtir.

```json
"safety": {
  "contains_image_or_video": false,
  "contains_rtsp_url": false,
  "contains_ip_address": false,
  "contains_credentials": false,
  "contains_person_name": false,
  "contains_full_local_path": false
}
```

Bu alanlardan biri `true` ise rapor paylaşılmamalıdır.

## 10. Tam Güvenli Örnek JSON

Aşağıdaki örnek temsili ve güvenlidir.

```json
{
  "report_type": "table_accuracy_evaluation",
  "schema_version": "1.0",
  "site": "T.UTYM#2",
  "camera_id": "TUTYM2-CAM-001",
  "created_at": "YYYY-MM-DDTHH:MM:SS",
  "evaluation_context": {
    "test_type": "rtsp_live",
    "lighting": "normal",
    "occupancy_level": "medium",
    "camera_angle_changed": false,
    "calibration_recent": true,
    "duration_minutes": 5,
    "average_fps": 8.3
  },
  "inputs": {
    "config_name": "tutym2_cam_001.rtsp.local.json",
    "model_name": "person_detector.onnx",
    "model_version": "initial-field-test"
  },
  "summary": {
    "table_count": 14,
    "tp": 7,
    "tn": 5,
    "fp": 1,
    "fn": 1,
    "unk": 0,
    "correct": 12,
    "incorrect": 2,
    "evaluated": 14,
    "accuracy": 0.8571
  },
  "tables": [
    {
      "table_id": "table_01",
      "ground_truth": "occupied",
      "prediction": "occupied",
      "label": "TP",
      "confidence": 0.91,
      "safe_note": "Normal görünüm."
    },
    {
      "table_id": "table_02",
      "ground_truth": "empty",
      "prediction": "occupied",
      "label": "FP",
      "confidence": 0.72,
      "safe_note": "Sandalye/masa kenarı etkisi olabilir."
    }
  ],
  "decision": {
    "prototype_ready": false,
    "recommended_next_action": "Kalibrasyon ve model eşiği tekrar kontrol edilmeli.",
    "requires_recalibration": true,
    "requires_model_change": false,
    "requires_camera_adjustment": false
  },
  "safety": {
    "contains_image_or_video": false,
    "contains_rtsp_url": false,
    "contains_ip_address": false,
    "contains_credentials": false,
    "contains_person_name": false,
    "contains_full_local_path": false
  }
}
```

Gerçek saha raporunda `tables` listesi 14 masa içermelidir.

## 11. Kabul Kontrolü

Bir JSON rapor ilk kabul için şu kontrollerden geçmelidir:

```text
[ ] report_type = table_accuracy_evaluation
[ ] schema_version dolu
[ ] site = T.UTYM#2
[ ] camera_id dolu
[ ] summary.table_count = 14
[ ] tables listesinde 14 kayıt var
[ ] Her table_id benzersiz
[ ] Her label izinli değerlerden biri
[ ] safety alanlarının tamamı false
[ ] RTSP URL/IP/parola/tam path yok
```

## 12. Sonraki Kod Adımı

Bu format sabitlendikten sonra sonraki teknik adım, bu JSON'u doğrulayan küçük bir validator eklemektir.

Validator şunları kontrol etmelidir:

```text
JSON parse edilebiliyor mu?
Zorunlu alanlar var mı?
14 masa var mı?
TP/TN/FP/FN/UNK toplamları summary ile uyumlu mu?
Accuracy doğru hesaplanmış mı?
Safety alanları false mu?
Hassas string örüntüleri var mı?
```

Bu validator operatör hatalarını azaltmak için ürünleşme aşamasında önemlidir.
