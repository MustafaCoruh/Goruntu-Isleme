# T.UTYM#2 R3 Dashboard Demo Smoke Plan

Bu plan, T.UTYM#2 için **R3 - Dashboard demo hazır** seviyesine hızlı geçiş yapmak için hazırlanmıştır.

R3 hedefi:

```text
Gerçek görüntü veya RTSP URL göstermeden,
güvenli dashboard_state.json ile statik dashboard'u açıp,
operatöre/yöneticiye ürün akışını göstermek.
```

R3 bir saha kabulü değildir. R3, güvenli ve kontrollü demo/sunum seviyesidir.

## 1. R3 Demo'da Ne Gösterilir?

Gösterilecekler:

```text
Statik T.UTYM#2 dashboard
14 masa kartı
Genel durum bilgisi
Güvenlik bayrakları
Örnek dashboard_state.json yükleme akışı
Operatör runbook / komut kataloğu / troubleshooting bağlantıları
```

Gösterilmeyecekler:

```text
Gerçek kamera görüntüsü
Gerçek RTSP URL
Kamera IP adresi
Kamera kullanıcı adı/parolası
Gerçek katılımcı bilgisi
Tam lokal Windows path
```

## 2. R3 Demo İçin Gereken Dosyalar

VS Code'da şu dosyalar görünmelidir:

| Dosya | Amaç |
| --- | --- |
| `app/ui/static/tutym2_dashboard.html` | Statik dashboard ekranı |
| `configs/templates/tutym2_dashboard_state.example.json` | Güvenli örnek dashboard verisi |
| `docs/deployment/tutym2_static_dashboard_operator_guide.md` | Dashboard açma kılavuzu |
| `docs/deployment/tutym2_dashboard_operator_workflow.md` | Dashboard kullanım akışı |
| `docs/deployment/tutym2_operator_master_runbook.md` | Tüm operatör akışı |
| `docs/deployment/tutym2_operator_command_catalog.md` | Script/komut açıklamaları |
| `docs/deployment/tutym2_operator_troubleshooting_guide.md` | Hata durumunda yapılacaklar |
| `docs/deployment/tutym2_release_readiness_checklist.md` | Release seviyesi kontrolü |

Bu dosyalardan biri yoksa R3 sunuma geçmeden önce PR/sync kontrolü yapılmalıdır.

## 3. R3 Demo Öncesi 5 Dakikalık Kontrol

| Kontrol | Beklenen |
| --- | --- |
| Son PR'lar merge edildi | Evet |
| VS Code sync/pull yapıldı | Evet |
| Dashboard HTML var | Evet |
| Örnek dashboard state JSON var | Evet |
| Dashboard guide var | Evet |
| Gerçek görüntü/video repo'da yok | Evet |
| Gerçek RTSP URL repo'da yok | Evet |
| Kamera IP/credential repo'da yok | Evet |

Bu kontrollerden biri “Hayır” ise demo durdurulur.



## 3.1. Otomatik R3 Smoke Check

R3 demo dosyalarının temel olarak hazır olup olmadığını kontrol etmek için şu script eklenmiştir:

```text
scripts/check_tutym2_r3_demo_smoke.py
```

Bu script kamera açmaz, RTSP bağlantısı kurmaz ve gerçek görüntü okumaz. Sadece statik dashboard HTML dosyasını ve güvenli örnek dashboard JSON dosyasını kontrol eder.

Kontrol ettiği ana şeyler:

```text
Dashboard HTML var mı?
Dashboard içinde beklenen güvenli demo metinleri var mı?
Örnek dashboard_state JSON var mı?
site = T.UTYM#2 mi?
camera_id = TUTYM2-CAM-001 mi?
14 masa var mı?
Safety flag değerleri false mu?
```

Örnek kullanım:

```powershell
python scripts/check_tutym2_r3_demo_smoke.py `
  --report-output C:\FTMC_FIELD_DATA\reports\r3_demo_smoke.json
```

`overall_status = pass` ise R3 dashboard demo dosyaları temel olarak sunuma hazırdır.



## 3.2. Terminal Kullanamayan Operatör İçin R3 Başlatıcı

Terminal kullanılamıyorsa R3 demo için şu statik HTML dosyası açılmalıdır:

```text
app/ui/static/tutym2_r3_demo_launcher.html
```

Bu sayfa tarayıcıda açılır, kamera/RTSP bağlantısı kurmaz ve güvenli örnek state değerleri üzerinden terminalsiz R3 kontrolü gösterir. Kontrol başarılıysa aynı sayfadan `tutym2_dashboard.html` dosyasına geçilebilir.



## 3.3. Buton Link Gibi Görünmüyorsa

`Terminalsiz R3 Kontrolü Gör` kontrolü normal bir link/anchor olarak tasarlanmıştır. Bazı VS Code önizleme modlarında buton gibi görünen öğeler sağ tık menüsünde `open link` göstermeyebilir. Bu durumda sorun değildir.

Sayfada şu statik yazıların görünmesi yeterlidir:

```text
R3 DEMO HAZIR
PASS Site T.UTYM#2
PASS Kamera TUTYM2-CAM-001
PASS 14 masa hedefi
PASS RTSP URL yok
PASS Credential yok
PASS Görüntü/video yok
PASS Tam lokal path yok
```

Bu yazılar görünüyorsa terminal gerekmeden R3 demo başlatıcı temel kontrolü okunabilir. Ardından `T.UTYM#2 Dashboard Aç` bağlantısı kullanılmalıdır.

## 4. R3 Demo Açılış Sırası

Terminal bilmeyen operatör için önerilen basit sıra:

```text
1. VS Code'da repo klasörünü aç.
2. app/ui/static/tutym2_dashboard.html dosyasını bul.
3. Dosyayı tarayıcıda aç.
4. configs/templates/tutym2_dashboard_state.example.json dosyasını bul.
5. Dashboard ekranındaki JSON yükleme alanından örnek JSON'u yükle.
6. 14 masa kartı, genel durum ve güvenlik bayrakları görünüyor mu kontrol et.
7. Gerçek görüntü/RTSP/kişisel veri görünmediğini teyit et.
```

Not: Eğer tarayıcıdan dosya yükleme kurum politikası nedeniyle engellenirse teknik kişi aynı akışı lokal web sunucusu üzerinden gösterebilir.

## 5. R3 Demo Konuşma Metni

Sunumda şu akışla anlatılabilir:

```text
Bu ekran T.UTYM#2 için güvenli operatör dashboard prototipidir.
Gerçek kamera görüntüsü veya RTSP bilgisi göstermiyoruz.
Sistem güvenli JSON özetleri üzerinden 14 masanın durumunu ve saha sağlığını gösterir.
Canlı sahaya geçmeden önce readiness, config validation, RTSP connection report ve dashboard state validation adımları vardır.
Hata olursa operatör troubleshooting guide'a göre ilerler.
Saha sonunda field handoff summary ile paylaşılabilir güvenli özet üretilir.
```



## 5.1. Terminalsiz R3 Sunum Akışı Sayfası

Sunum sırasında konuşma sırası, hangi ekranda ne gösterileceği ve beklenen sorulara kısa cevaplar için şu statik HTML sayfası kullanılabilir:

```text
app/ui/static/tutym2_r3_presentation.html
```

Bu sayfa terminal gerektirmez ve gerçek görüntü/RTSP/IP/credential göstermez. R3 demo başlatıcı sayfasından da açılabilir.

## 6. R3 Demo'da Beklenen Görsel Sonuç

Dashboard açıldığında beklenenler:

```text
Site: T.UTYM#2
Kamera: TUTYM2-CAM-001
14 masa kartı
Genel durum alanı
Safety / güvenlik alanı
Rapor özetleri
```

Beklenmeyenler:

```text
Gerçek görüntü görünmesi
RTSP URL görünmesi
Kamera IP görünmesi
Credential görünmesi
Tam lokal path görünmesi
Kişi/yüz bilgisi görünmesi
```

Beklenmeyen bir durum varsa R3 demo durdurulur.



## 6.1. Dashboard Üzerindeki R3 Demo Banner

`tutym2_dashboard.html` açıldığında üst bölümde `R3 Demo Modu` banner'ı görünmelidir. Bu banner şunu anlatır:

```text
Bu ekran güvenli örnek dashboard verisiyle açılır.
Gerçek kamera görüntüsü, RTSP URL, kamera IP veya credential göstermez.
```

Banner içinde `R3 Demo Başlatıcıya dön` bağlantısı da bulunur. Operatör yanlışlıkla dashboard'a doğrudan geldiyse bu bağlantıyla terminalsiz başlatıcı sayfasına dönebilir.

## 7. R3 Demo Sonrası Paylaşılabilir Özet

Demo sonrası paylaşılabilir güvenli özet:

```text
R3 dashboard demo açıldı.
Örnek güvenli dashboard_state yüklendi.
14 masa kartı görüntülendi.
Gerçek görüntü/RTSP/IP/credential paylaşılmadı.
Dashboard state güvenli örnek üzerinden gösterildi.
R4 saha kabul için gerçek saha doğruluk raporu gereklidir.
```

Paylaşılmaması gerekenler:

```text
Ekranda görünen gerçek saha görüntüsü varsa paylaşma.
Lokal path ekran görüntüsü varsa paylaşma.
RTSP veya IP içeren not varsa paylaşma.
```

## 8. R3 Başarı Kriterleri

R3 başarılı sayılırsa:

| Kriter | Başarılı mı? |
| --- | --- |
| Dashboard açıldı | `[ ]` |
| Örnek JSON yüklendi | `[ ]` |
| 14 masa kartı görüldü | `[ ]` |
| Genel durum görüldü | `[ ]` |
| Safety alanı görüldü | `[ ]` |
| Gerçek görüntü/RTSP/IP görünmedi | `[ ]` |
| Operatör ana dokümanlara erişebildi | `[ ]` |

Tüm kritik kriterler tamamlanırsa R3 demo sunulabilir.

## 9. R3'ten R4'e Geçiş

R3 tamamlandıktan sonra R4 için yapılacaklar:

```text
1. Lokal saha klasörü hazırlanır.
2. Model lokal models klasörüne konur.
3. Gerçek lokal config oluşturulur.
4. Offline readiness raporu alınır.
5. Config validation pass alınır.
6. RTSP connection report alınır.
7. Lokal/RTSP demo report alınır.
8. Table accuracy report hazırlanır.
9. Dashboard state gerçek güvenli raporlardan üretilir.
10. Field handoff summary ile kapanış yapılır.
```

R4 için gerçek saha verisi gerekir; bu veri repo'ya konmaz ve paylaşılmaz.

## 10. Zaman Tahmini

Pratik tahmin:

| Hedef | Kalan iş | Tahmin |
| --- | --- | --- |
| R3 demo | Son PR'ları çek, dashboard example ile smoke demo yap | Kısa |
| R4 saha kabul adayı | Lokal config/model/RTSP/readiness/doğruluk raporları | Orta |
| Çoklu UTYM yayılım | T.UTYM#2 standardını genelleştir | Daha sonra |

R3 için artık ana eksik kod değil, **ilk kontrollü demo koşusudur**.

## 11. R3 Demo Kararı

R3 demo için karar cümlesi:

```text
Eğer dashboard güvenli örnek JSON ile açılıyor, 14 masa kartını gösteriyor ve hassas veri göstermiyorsa R3 demo sunulabilir.
```

R4 için karar cümlesi:

```text
Eğer gerçek T.UTYM#2 saha raporları güvenli şekilde üretilmiş, doğruluk raporu kabul edilebilir ve dashboard state validation pass ise R4 saha kabul adayıdır.
```
