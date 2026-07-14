# T.UTYM#2 Operatör Ana Çalışma Kitabı

Bu doküman, T.UTYM#2 için geliştirilen tüm güvenli saha akışını **tek sıraya** koyar.

Hedef okuyucu:

```text
VS Code, GitHub, Python veya terminal konusunda uzman olmayan operatör / saha sorumlusu.
```

Bu doküman kod yazdırmaz. Sadece hangi adımın hangi amaçla yapıldığını, hangi dosyanın ne işe yaradığını ve hangi sırayla ilerlenmesi gerektiğini anlatır.

## 0. En Önemli Kural

Aşağıdaki veriler hiçbir zaman GitHub'a, PR'a, chat ortamına veya repo içine eklenmemelidir:

```text
Gerçek RTSP URL
Kamera IP adresi
Kamera kullanıcı adı/parolası
Gerçek fotoğraf
Gerçek video
Tam lokal Windows path bilgisi
Katılımcı/yüz/kimlik bilgisi
```

Sistemde üretilen güvenli raporlar bile önce validator veya checklist ile kontrol edilmelidir.

## 1. Büyük Resim

T.UTYM#2 akışı şu sırayla düşünülmelidir:

```text
1. Kodları VS Code'a çek.
2. Gerekli dosyalar geldi mi kontrol et.
3. Offline paket manifestini kontrol et.
4. Lokal saha klasörünü hazırla.
5. Model ve lokal config dosyalarını repo dışında hazırla.
6. Offline readiness check yap.
7. Config validator çalıştır.
8. RTSP bağlantı testini güvenli raporla.
9. Lokal fotoğraf/video demosu veya RTSP demosu çalıştır.
10. Table accuracy raporu hazırla/validate et.
11. Dashboard state üret ve validate et.
12. Statik dashboard ile sonucu gör.
13. Saha teslim özetini üret.
14. Sadece güvenli özeti paylaş.
```

## 2. PR Geldikten Sonra VS Code'da Kontrol

Her PR merge edildikten sonra VS Code'da dosyaların gelip gelmediği kontrol edilir.

Öncelikli kontrol dosyaları:

```text
app/field_demo.py
app/rtsp_field_demo.py
app/offline_readiness.py
app/dashboard_state.py
app/dashboard_state_validator.py
app/field_handoff_summary.py
app/offline_package_manifest.py
app/ui/static/tutym2_dashboard.html
```

Öncelikli scriptler:

```text
scripts/check_tutym2_offline_readiness.py
scripts/run_tutym2_local_demo.py
scripts/run_tutym2_rtsp_demo.py
scripts/build_tutym2_dashboard_state.py
scripts/validate_tutym2_dashboard_state.py
scripts/build_tutym2_field_handoff_summary.py
scripts/validate_tutym2_offline_package_manifest.py
```

Eğer bu dosyalar görünüyorsa ana operatör araçları gelmiş demektir.



## 2.1. Komut Kataloğu

Scriptlerin tek tek ne işe yaradığını, hangi girdileri istediğini, hangi çıktıları ürettiğini ve hangi durumda durulması gerektiğini görmek için şu katalog kullanılmalıdır:

```text
docs/deployment/tutym2_operator_command_catalog.md
```



## 2.2. Hata ve Çözüm Rehberi

Komutlardan veya validatorlardan hata alındığında şu rehber kullanılmalıdır:

```text
docs/deployment/tutym2_operator_troubleshooting_guide.md
```

Bu rehber hata mesajını nasıl yorumlayacağını, ne zaman duracağını ve teknik kişiye hassas veri paylaşmadan ne söyleyeceğini açıklar.



## 2.3. Release Readiness Checklist

Sistemin sunuma, operatör demosuna veya kontrollü saha paketine hazır olup olmadığını değerlendirmek için şu checklist kullanılmalıdır:

```text
docs/deployment/tutym2_release_readiness_checklist.md
```

Bu checklist R3 dashboard demo ve R4 saha kabul adayı ayrımını netleştirir.

## 3. Offline Paket Kontrolü

Saha bilgisayarına dosya taşımadan önce şu doküman okunur:

```text
docs/deployment/tutym2_offline_package_manifest.md
```

Güvenli manifest template'i:

```text
configs/templates/tutym2_offline_package_manifest.template.json
```

Amaç:

```text
Offline pakette gerekli dosyalar var mı?
Hassas veri yanlışlıkla pakete girmiş mi?
```

## 4. Lokal Saha Klasörleri

Gerçek saha dosyaları repo dışında tutulur.

Önerilen kök klasör:

```text
C:\FTMC_FIELD_DATA\
```

Önerilen alt klasörler:

```text
C:\FTMC_FIELD_DATA\configs\
C:\FTMC_FIELD_DATA\inputs\
C:\FTMC_FIELD_DATA\models\
C:\FTMC_FIELD_DATA\reports\
```

Bu klasörler GitHub'a gönderilmez.

## 5. Lokal Config Hazırlığı

Başlangıç template'i:

```text
configs/templates/tutym2_cam_001.template.json
```

Lokal kopya adı:

```text
tutym2_cam_001.local.json
```

Bu lokal dosya gerçek kalibrasyon veya RTSP bilgisi içerebileceği için repo'ya geri kopyalanmaz.

Detaylı kalibrasyon akışı:

```text
docs/deployment/tutym2_calibration_operator_guide.md
```

## 6. Model Hazırlığı

Model dosyası varsayılan olarak lokal saha klasöründe tutulur:

```text
C:\FTMC_FIELD_DATA\models\person_detector.onnx
```

Repo içindeki açıklama dosyası:

```text
models/README.md
```

Model dosyasının kendisi kurum politikası izin vermedikçe PR'a eklenmemelidir.

## 7. Offline Readiness Check

Amaç:

```text
Saha bilgisayarı temel olarak hazır mı?
Python, klasörler, config ve model görünüyor mu?
```

İlgili script:

```text
scripts/check_tutym2_offline_readiness.py
```

İlgili detay dokümanı:

```text
docs/deployment/tutym2_offline_installation_plan.md
```

Bu adım kamera açmaz, RTSP bağlantısı kurmaz, görüntü okumaz.

## 8. Config Validation

Amaç:

```text
14 masa var mı?
Çözünürlük 1920x1080 mi?
Polygon değerleri beklenen sınırlar içinde mi?
Placeholder/RTSP güvenlik kuralları uygun mu?
```

İlgili script:

```text
scripts/validate_tutym2_config.py
```

Bu adım canlı kamera açmadan config dosyasının mantığını kontrol eder.

## 9. RTSP Bağlantı Testi

Amaç:

```text
Canlı kameraya bağlanılabiliyor mu?
Frame okunabiliyor mu?
Bu bilgi güvenli rapora dökülebiliyor mu?
```

İlgili script:

```text
scripts/run_tutym2_rtsp_demo.py
```

İlgili dokümanlar:

```text
docs/deployment/tutym2_rtsp_operator_guide.md
docs/deployment/tutym2_rtsp_connection_report_guide.md
```

RTSP URL veya kamera IP rapora yazılmamalıdır.

## 10. Lokal Fotoğraf/Video veya RTSP Demo

İlk denemede canlı kamera yerine lokal geçmiş fotoğraf/video ile ilerlemek daha güvenlidir.

Lokal demo scripti:

```text
scripts/run_tutym2_local_demo.py
```

RTSP demo scripti:

```text
scripts/run_tutym2_rtsp_demo.py
```

Windows hızlı başlangıç dokümanı:

```text
docs/deployment/windows_quick_start_for_operator.md
```

Bu adımın amacı masaların dolu/boş tahmin akışını sahada doğrulamaktır.

## 11. Table Accuracy Raporu

Amaç:

```text
14 masanın hangilerinde doğru/yanlış tahmin var?
False positive / false negative var mı?
Masa bazlı doğruluk görülebiliyor mu?
```

Rapor format dokümanı:

```text
docs/validation/tutym2_table_accuracy_report_format.md
```

Validator script:

```text
scripts/validate_tutym2_table_accuracy_report.py
```

Bu rapor gerçek görüntü içermez; sadece güvenli metrik içermelidir.

## 12. Dashboard State Üretimi

Amaç:

```text
Çeşitli güvenli raporları tek dashboard_state.json dosyasında toplamak.
```

Builder script:

```text
scripts/build_tutym2_dashboard_state.py
```

Validator script:

```text
scripts/validate_tutym2_dashboard_state.py
```

Dashboard state format dokümanı:

```text
docs/roadmap/tutym2_dashboard_state_format.md
```

Dashboard state doğrulanmadan statik dashboard üzerinden karar verilmemelidir.

## 13. Statik Dashboard Görüntüleme

Dashboard dosyası:

```text
app/ui/static/tutym2_dashboard.html
```

Dashboard kullanım dokümanları:

```text
docs/deployment/tutym2_static_dashboard_operator_guide.md
docs/deployment/tutym2_dashboard_operator_workflow.md
```

Dashboard operatöre şu bilgileri sade gösterir:

```text
Genel durum
14 masa kartı
Güvenlik bayrakları
Rapor durumu
Dashboard state özeti
```

Dashboard içinde gerçek görüntü veya canlı stream gösterilmesi bu aşamanın hedefi değildir.

## 14. Saha Günü Tek Sayfa Checklist

Saha günü hızlı takip için şu dosya kullanılır:

```text
docs/deployment/tutym2_field_day_one_page_checklist.md
```

Bu dosya uzun dokümanların kısa operasyon özetidir.

## 15. Saha Teslim Özeti

Saha sonunda güvenli paylaşım için tek özet üretilir:

```text
field_handoff_summary.json
```

İlgili script:

```text
scripts/build_tutym2_field_handoff_summary.py
```

İlgili doküman:

```text
docs/deployment/tutym2_field_handoff_summary.md
```

Bu çıktı sadece güvenli özet alanları içermelidir.

## 16. Operatörün Paylaşabileceği Bilgiler

Paylaşılabilir güvenli özet örnekleri:

```text
site = T.UTYM#2
overall_status = normal / warning / critical
report_count = sayı
masa sayısı = 14
doğruluk yüzdesi = metrik
false positive / false negative sayıları = metrik
safe_to_share = true / false
```

Paylaşılmayacaklar:

```text
RTSP URL
Kamera IP
Kamera kullanıcı adı/parolası
Gerçek fotoğraf/video
Tam lokal path
Kişi adı/yüz görüntüsü
```

## 17. Hata Durumunda Ne Yapılır?

| Durum | Anlam | Aksiyon |
| --- | --- | --- |
| Eksik dosya | PR veya sync eksik olabilir | VS Code dosya ağacı kontrol edilir |
| Validator fail | Config/rapor formatı hatalı veya hassas veri riski var | Saha testi durdurulur, teknik kişi bakar |
| Dashboard critical | Sistem sonucu güvenilir değil | Canlı karar için kullanılmaz |
| RTSP bağlantı yok | Kamera/network erişimi yok | RTSP bilgisi ve yerel ağ yetkisi kontrol edilir |
| Model yok | Algılama çalışmaz | Model lokal klasöre konur |

## 18. Öncelik Sırası

Her karar şu sırayla verilir:

```text
Güvenlik > Doğruluk > Kararlılık > Hız > Görsellik
```

Yani sistem hızlı veya güzel görünse bile hassas veri sızdırıyorsa kabul edilmez.

## 19. Çoklu UTYM'ye Yayılım Notu

Bu çalışma T.UTYM#2 ile başlar. Ürünleşme aşamasında aynı yapı diğer UTYM'lere şu mantıkla çoğaltılır:

```text
Her UTYM için ayrı site kodu
Her kamera için ayrı config
Her saha için ayrı lokal-only klasör
Her UTYM için ayrı dashboard_state
Her UTYM için ayrı field_handoff_summary
```

Bu yüzden bu ana runbook, ileride çoklu UTYM standardının başlangıç dokümanı olarak düşünülmelidir.
