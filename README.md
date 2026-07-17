# FTMC Occupancy

FTMC/UTYM ortamlarında kamera görüntüsünden masa doluluk durumunu tespit eden offline çalışabilir görüntü işleme uygulaması.

## T.UTYM#2 için terminalsiz hızlı yol

Bu repo artık T.UTYM#2 saha demo ve R4 kabul akışı için terminal kullanmadan izlenebilecek statik ekranlar da içerir. Operatör tarafında öncelik şu sıradır:

1. `app/ui/static/tutym2_r4_acceptance_center.html` dosyasını tarayıcıda aç.
2. Önce **Güvenli Örnekle Dene** veya **Güvenli Örnek JSON Dosyalarını İndir** ile ekranın nasıl çalıştığını kontrol et.
3. Gerçek R4 kapanışı için yalnızca sahadan gelen üç güvenli JSON dosyasını seç:
   - Dashboard Durum Raporu
   - Saha Teslim Özeti
   - R4 Final Karar Raporu
4. Ekranda **Toplu R4 Görsel Sonuç: KONTROLLÜ SAHA KABULÜNE HAZIR** görünmeden projeyi saha kabul açısından bitmiş sayma.

**Ne kadar kaldı?** Yazılım/UI/doküman tarafı yaklaşık %90+ hazır kabul edilebilir. Kalan ana iş, gerçek saha makinesinden üretilecek üç güvenli R4 JSON dosyasının gelmesi ve R4 ekranında PASS vermesidir. Bu dosyalar hazırsa kontrol aynı gün içinde kapanabilir; dosyalar yoksa süre saha ekibinin üretimine bağlıdır.

> Güvenli örnek dosyalar resmi kapanış değildir. Gerçek video dosyası, RTSP URL, kamera IP, parola veya tam lokal path bu repoya eklenmemeli ve R4 ekranına not olarak yazılmamalıdır.

## Operatörün kontrol edeceği ana ekranlar

- R4 kabul merkezi: `app/ui/static/tutym2_r4_acceptance_center.html`
- T.UTYM#2 dashboard: `app/ui/static/tutym2_dashboard.html`
- R3 başlatıcı: `app/ui/static/tutym2_r3_demo_launcher.html`
- R3 sunum ekranı: `app/ui/static/tutym2_r3_presentation.html`

## Teknik kullanıcılar için güvenli CLI girişleri

Terminal kullanabilen ekip üyeleri için script girişleri `scripts/` altındadır. Üretilen raporlar RTSP URL, credential, görüntü/video ve tam lokal path içermeyecek şekilde tasarlanmıştır. Operatör terminal kullanamıyorsa bu scriptleri çalıştırması beklenmez; ona yalnızca güvenli JSON çıktıları verilmelidir.
