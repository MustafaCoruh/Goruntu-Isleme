# T.UTYM#2 Dashboard State Validator Operatör Kılavuzu

Bu kılavuz, `dashboard_state.json` dosyasının UI tarafından okunmadan önce nasıl kontrol edileceğini anlatır.

Amaç:

```text
dashboard_state.json gerçekten var mı?
JSON formatı doğru mu?
14 masa kartı var mı?
overall_status ve connection_status izinli değerlerden mi?
table_summary değerleri masa kartlarıyla tutarlı mı?
safety alanlarının tamamı false mu?
```

Bu kılavuz gerçek görüntü, RTSP URL, IP adresi, kullanıcı adı/parola veya kişisel veri içermez.

## 1. Bu Validator Hangi Dosyaları Ekler?

Bu adımda VS Code içinde özellikle şu dosyalar görülmelidir:

```text
app/dashboard_state_validator.py
scripts/validate_tutym2_dashboard_state.py
tests/test_dashboard_state_validator.py
```

Bu üç dosya yoksa PR merge/pull işlemi eksik kalmış olabilir.

## 2. Validator Ne İşe Yarar?

`app/dashboard_state_validator.py`, dashboard ekranının okuyacağı `dashboard_state.json` dosyasını kontrol eder.

Kontrol ettiği temel konular:

```text
report_type = dashboard_state mi?
site = T.UTYM#2 mi?
camera_id = TUTYM2-CAM-001 mi?
overall_status izinli değerlerden biri mi?
connection_status izinli değerlerden biri mi?
14 masa kartı var mı?
table_summary toplamları doğru mu?
sources alanları var mı?
safety alanlarının tamamı false mu?
```

## 3. Neden Gerekli?

Dashboard UI yanlış veya güvensiz JSON okursa operatöre yanlış bilgi gösterebilir.

Örnek riskler:

```text
UI 13 masa gösterir ama sahada 14 masa vardır.
JSON overall_status için geçersiz değer içerir.
Safety alanında contains_rtsp_url = true olur.
Table summary 14 etmeyen toplamlar içerir.
Source raporlarından biri eksik veya bozuk olabilir.
```

Validator bu hataları UI aşamasından önce yakalamak için vardır.

## 4. Örnek Kullanım

Yetkili teknik kişi saha bilgisayarında şu mantıkta çalıştırabilir:

```powershell
python scripts/validate_tutym2_dashboard_state.py `
  --state C:\FTMC_FIELD_DATA\reports\dashboard_state.json
```

Başarılıysa güvenli kısa çıktı beklenir:

```json
{
  "status": "valid",
  "site": "T.UTYM#2",
  "camera_id": "TUTYM2-CAM-001"
}
```

## 5. Hata Örnekleri

| Hata | Anlamı | İlk aksiyon |
| --- | --- | --- |
| `overall_status` hatalı | Dashboard genel durumu izinli değer değil | `dashboard_state.py` çıktısı kontrol edilmeli |
| `tables must contain 14 records` | 14 masa kartı yok | Table accuracy raporu ve state builder kontrol edilmeli |
| `table_summary counts must add up to 14` | Masa özet sayıları tutarsız | Table summary yeniden üretilmeli |
| `safety.contains_rtsp_url must be false` | State güvenli değil | Rapor paylaşılmamalı |
| `sources missing keys` | Beklenen rapor kaynağı eksik | Rapor üretim zinciri kontrol edilmeli |

## 6. Merge Sonrası Kontrol

VS Code içinde şu aramaları yapabilirsiniz:

```text
DashboardStateValidationError
EXPECTED_TABLE_COUNT = 14
validate_dashboard_state
_validate_safety
MERGE-CHECK: dashboard-state-validator
```

Bu ifadeler görünüyorsa validator dosyası gelmiş demektir.
