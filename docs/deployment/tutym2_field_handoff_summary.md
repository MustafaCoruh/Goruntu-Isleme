# T.UTYM#2 Saha Teslim Özeti

Bu doküman, saha çalışması bittikten sonra güvenli şekilde paylaşılabilecek **tek bir özet JSON** üretme mantığını açıklar.

Amaç şudur:

```text
Saha koşusu yapıldı.
Birden fazla güvenli rapor üretildi.
Bu raporların sonucunu tek özet halinde paylaşmak istiyoruz.
Ama gerçek RTSP URL, IP, görüntü, video, credential veya tam lokal path paylaşmak istemiyoruz.
```

## 1. Neden Saha Teslim Özeti Gerekli?

T.UTYM#2 akışında birçok güvenli rapor oluşabilir:

- Offline readiness raporu.
- Offline package manifest validation raporu.
- Config validation raporu.
- RTSP connection raporu.
- Local demo raporu.
- RTSP demo raporu.
- Table accuracy raporu.
- Dashboard state validation raporu.

Operatör veya yönetici her raporu tek tek okumak zorunda kalmamalıdır. Bunun yerine sistem güvenli bir üst özet üretir:

```text
field_handoff_summary.json
```

Bu özet sadece güvenli alanları içerir:

- Site adı.
- Genel durum.
- Kaç rapor okunduğu.
- Her raporun dosya adı.
- Her raporun tip bilgisi.
- Her raporun normalize edilmiş durumu.
- Paylaşılabilirlik bilgisi.

## 2. Eklenen Araç

Bu PR ile şu modül ve script eklenmiştir:

```text
app/field_handoff_summary.py
scripts/build_tutym2_field_handoff_summary.py
```

Script, lokal JSON raporlarını okur ve güvenli bir `field_handoff_summary.json` üretir.

## 3. Desteklenen Input Etiketleri

Komutta her rapor `LABEL=PATH` şeklinde verilir.

Desteklenen etiketler:

```text
offline_readiness
offline_package_manifest
config_validation
rtsp_connection
local_demo
rtsp_demo
table_accuracy
dashboard_state
dashboard_state_validation
```

Bu etiketler dışındaki değerler reddedilir. Böylece operatör yanlışlıkla belirsiz veya hassas bir dosyayı eklemeye çalışırsa hata alınır.

## 4. Güvenlik Kontrolleri

Özet oluşturucu input raporların metninde şunları arar ve bulursa işlemi durdurur:

```text
RTSP benzeri stream bilgisi
Credential/parola/token benzeri kelimeler
IP adresi
Tam lokal Windows/Linux path bilgisi
```

Ayrıca çıktı raporu tam path yazmaz; sadece dosya adını yazar.

## 5. Örnek Komut

Terminal erişimi olan yetkili kişi şu mantıkta çalıştırır:

```powershell
python scripts/build_tutym2_field_handoff_summary.py `
  --input offline_readiness=C:\FTMC_FIELD_DATA\reports\offline_readiness.json `
  --input dashboard_state_validation=C:\FTMC_FIELD_DATA\reports\dashboard_state_validation.json `
  --input table_accuracy=C:\FTMC_FIELD_DATA\reports\table_accuracy_report.json `
  --output C:\FTMC_FIELD_DATA\reports\field_handoff_summary.json
```

Üretilen çıktı güvenli özet mantığındadır.

## 6. Örnek Çıktı

Repo içinde güvenli örnek çıktı tutulur:

```text
configs/templates/tutym2_field_handoff_summary.example.json
```

Bu örnek gerçek saha verisi içermez.

## 7. Durum Mantığı

Input raporların durumları normalize edilir:

| Input durumu | Özet durumu |
| --- | --- |
| `pass`, `ok`, `normal`, `ready` | `normal` |
| `warn`, `warning`, `not_ready` | `warning` |
| `fail`, `failed`, `critical`, `error` | `critical` |
| Bilinmeyen değer | `warning` |

Genel sonuç önceliği:

```text
critical > warning > normal
```

Yani bir rapor bile kritikse saha teslim özeti kritik olur.

## 8. Paylaşım Kuralı

Paylaşılabilecek güvenli bilgiler:

```text
site
overall_status
report_count
report label
report file name
report type
normalized status
safe_to_share
```

Paylaşılmaması gereken bilgiler:

```text
Gerçek RTSP URL
Kamera IP
Kamera kullanıcı adı/parolası
Gerçek görüntü/video
Tam lokal path
Katılımcı kimliği
```

## 9. Operatör İçin Basit Karar

| Sonuç | Anlamı | Ne yapılır? |
| --- | --- | --- |
| `normal` | Okunan raporlar normal | Güvenli özet paylaşılabilir |
| `warning` | En az bir raporda uyarı var | Teknik sorumlu kontrol eder |
| `critical` | En az bir raporda kritik hata var | Saha sonucu kabul edilmeden önce düzeltilir |

## 10. Ürünleşme Notu

Bu özet, ürünleşme tarafında “günün sonunda tek güvenli çıktı” ihtiyacını karşılar.

İleride çoklu UTYM yapısında her UTYM için ayrı teslim özeti üretilebilir:

```text
tutym2_field_handoff_summary.json
tutym3_field_handoff_summary.json
tutym4_field_handoff_summary.json
```
