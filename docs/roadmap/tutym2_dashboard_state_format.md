# T.UTYM#2 Dashboard State JSON Formatı

Bu doküman, `app/dashboard_state.py` tarafından üretilen güvenli `dashboard_state.json` çıktısının formatını açıklar.

Amaç:

```text
Dashboard UI'ın okuyacağı tek birleşik JSON formatını sabitlemek.
Operatör ekranı için genel durum, bağlantı, masa özeti, masa kartları ve uyarıları standartlaştırmak.
RTSP URL, görüntü, credential veya tam lokal path içermeyen güvenli bir ara katman oluşturmak.
```

## 1. Önerilen Dosya Adı

Saha bilgisayarında önerilen lokal çıktı:

```text
C:\FTMC_FIELD_DATA\reports\dashboard_state.json
```

Bu dosya güvenli özet içerir. Yine de kurum politikasına göre kontrollü paylaşılmalıdır.

## 2. Üst Seviye Alanlar

Dashboard state şu alanlardan oluşur:

```json
{
  "report_type": "dashboard_state",
  "site": "T.UTYM#2",
  "camera_id": "TUTYM2-CAM-001",
  "overall_status": "warning",
  "connection_status": "connected",
  "average_fps": 8.3,
  "table_summary": {},
  "tables": [],
  "warnings": [],
  "criticals": [],
  "sources": {},
  "safety": {}
}
```

## 3. `overall_status` Alanı

| Değer | Anlamı | UI rengi |
| --- | --- | --- |
| `normal` | Temel kontroller iyi | Yeşil |
| `warning` | Devam edilebilir ama kontrol gerekiyor | Sarı |
| `critical` | Canlı teste/demoya devam edilmemeli | Kırmızı |
| `not_ready` | Henüz rapor/veri yok | Gri |

## 4. `connection_status` Alanı

| Değer | Anlamı |
| --- | --- |
| `connected` | RTSP bağlantı testi başarılı veya frame okunabiliyor |
| `disconnected` | RTSP bağlantı/frame okuma başarısız |
| `not_tested` | RTSP bağlantı raporu yok veya test edilmedi |

## 5. `table_summary` Alanı

Örnek:

```json
"table_summary": {
  "total": 14,
  "occupied": 6,
  "empty": 7,
  "unknown": 1,
  "no_data": 0
}
```

Alanlar:

| Alan | Anlamı |
| --- | --- |
| `total` | Toplam masa sayısı; T.UTYM#2 için 14 |
| `occupied` | Dolu görünen masa sayısı |
| `empty` | Boş görünen masa sayısı |
| `unknown` | Belirsiz karar sayısı |
| `no_data` | Veri olmayan masa sayısı |

## 6. `tables` Alanı

Her masa kartı şu formatta olmalıdır:

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

| Alan | Açıklama |
| --- | --- |
| `table_id` | `table_01` - `table_14` |
| `display_name` | Operatöre gösterilecek masa adı |
| `state` | `occupied`, `empty`, `unknown`, `no_data` |
| `confidence` | 0.0 - 1.0 arası sayı veya null |
| `label` | TP/TN/FP/FN/UNK veya null |
| `color` | UI renk anahtarı |
| `warning` | Güvenli operatör uyarısı veya null |

## 7. Renk Anahtarları

| `color` | UI karşılığı |
| --- | --- |
| `red_or_orange` | Dolu masa |
| `green` | Boş masa |
| `yellow` | Belirsiz veya uyarı |
| `gray` | Veri yok |

## 8. `warnings` ve `criticals`

`warnings` devam edilebilir ama kontrol gerektiren durumları içerir.

Örnek:

```json
"warnings": [
  "FPS düşük. Ağ, stream profili veya GPU kontrol edilmeli."
]
```

`criticals` canlı teste/demoya devam edilmemesi gereken durumları içerir.

Örnek:

```json
"criticals": [
  "RTSP bağlantısında frame okunamadı."
]
```

## 9. `sources` Alanı

Dashboard state'in hangi rapor dosyalarından üretildiğini gösterir.

```json
"sources": {
  "offline_readiness": {
    "name": "offline_readiness.json",
    "status": "loaded"
  },
  "config_validation": {
    "name": "config_validation_summary.json",
    "status": "missing"
  }
}
```

İzinli `status` değerleri:

| Değer | Anlamı |
| --- | --- |
| `loaded` | Dosya okundu |
| `missing` | Dosya yok |
| `invalid_json` | Dosya var ama JSON bozuk |

## 10. `safety` Alanı

Dashboard state güvenli özet olduğu için şu alanların tamamı `false` olmalıdır:

```json
"safety": {
  "contains_rtsp_url": false,
  "contains_credentials": false,
  "contains_image_or_video": false,
  "contains_full_local_path": false
}
```

Bunlardan biri `true` olursa state güvenli sayılmamalıdır.

## 11. Tam Güvenli Örnek

Repo içinde güvenli örnek template olarak `configs/templates/tutym2_dashboard_state.example.json` dosyası bulunur.

Bu örnek gerçek RTSP URL, IP, credential, görüntü veya tam lokal path içermez.

## 12. UI İçin Kullanım Notu

İlk UI kodu sadece bu state dosyasını okumalıdır.

Önerilen akış:

```text
1. Güvenli raporlar üretilir.
2. app/dashboard_state.py bu raporları dashboard_state.json dosyasına dönüştürür.
3. UI sadece dashboard_state.json okur.
4. UI gerçek RTSP URL veya görüntü dosyasıyla doğrudan çalışmaz.
```

Bu yaklaşım ürünleşme sürecinde güvenliği ve test edilebilirliği artırır.
