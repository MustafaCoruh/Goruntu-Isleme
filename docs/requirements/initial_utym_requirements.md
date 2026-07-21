# İlk UTYM Prototipi Gereksinim Dokümanı

Bu doküman, ilk prototipin çalışacağı UTYM ortamı ve görüntü işleme kapsamı için temel gereksinimleri tek yerde toplar.

## 1. UTYM Bilgileri

| No | Gereksinim | Değer / Açıklama |
| --- | --- | --- |
| 1 | İlk prototipin çalışacağı UTYM adı veya kodu | T.UTYM#2 |
| 2 | UTYM’deki kamera sayısı | Karar bekliyor — ilk prototip için en az 1 RTSP destekli IP kamera kullanılacak |

## 2. Kamera Bilgileri

| No | Gereksinim | Değer / Açıklama |
| --- | --- | --- |
| 3 | İlk prototipte kullanılacak kamera | T.UTYM#2 ortamındaki ilk RTSP destekli IP video kamera; gerçek RTSP URL repo’ya yazılmayacak |
| 4 | Kameranın tipi | IP video kamera |
| 5 | Görüntü çözünürlüğü ve yaklaşık FPS | 1920x1080 (1080P); FPS karar bekliyor |

## 3. Masa ve Sandalye Bilgileri

| No | Gereksinim | Değer / Açıklama |
| --- | --- | --- |
| 6 | Masaların sayısı | 14 |
| 7 | Her masadaki sandalye sayısı | 1 |
| 8 | Masaların sabit olup olmadığı | Karar bekliyor — ilk MVP yaklaşımı sabit masa/kamera kalibrasyonu varsayar |

## 4. Çalışma Ortamı ve Kayıt Gereksinimleri

| No | Gereksinim | Değer / Açıklama |
| --- | --- | --- |
| 9 | Uygulamanın çalışacağı işletim sistemi | Windows |
| 10 | İnternetsiz çalışma zorunluluğu | Geliştirme bilgisayarı kontrollü internete açık; operasyon bilgisayarı tamamen internetsiz çalışacaktır |
| 11 | Görüntü kaydı tutulup tutulmayacağı | Hayır — gerçek görüntü/video repo’ya konmayacak ve paylaşılmayacak |

## 5. İlk Hedef Kapsamı

| No | Gereksinim | Değer / Açıklama |
| --- | --- | --- |
| 12 | İlk hedefin masa bazlı mı sandalye bazlı mı olduğu | Masa bazlı doluluk; her masada 1 sandalye olduğu için masa sonucu pratikte tek koltuk doluluk sonucuna karşılık gelir |

## 6. Gerçek Veri Kullanım Kısıtı

- Gerçek T.UTYM#2 görüntüleri ve videoları repo’ya eklenmeyecektir.
- Gerçek görüntü/video asistanla veya dış ortamla paylaşılmayacaktır.
- Geliştirme reposunda yalnızca sentetik/anonim örnek veri, kalibrasyon şablonu ve test fixture'ları tutulacaktır.
- Doğrulama, önce kurum içi Windows makinede T.UTYM#2'den alınmış lokal geçmiş video ile; ürün aşamasında canlı kamera akışı veya eski kamera kaydı ile çalıştırılacaktır.
- Kalibrasyon noktaları gerçek görüntü paylaşılmadan; kullanıcı tarafından lokal kalibrasyon ekranında veya koordinat dosyası üzerinden girilecektir.

## 7. Açık Kararlar

| Konu | Durum | Etki |
| --- | --- | --- |
| Toplam kamera sayısı | Karar bekliyor | Çoklu kamera birleştirme kapsamını etkiler |
| İlk kamera ID / RTSP URL | RTSP var; gerçek URL ürün bilgisayarında lokal secret/config olarak girilecek | Canlı IP video bağlantı testini etkiler |
| FPS | Karar bekliyor | Performans kabul kriterini etkiler |
| İlk test kaynağı | Lokal geçmiş video | Gerçek görüntü paylaşılmadan ilk saha denemesini mümkün kılar |
| Geliştirme donanımı | Intel Xeon Gold 6284R CPU; GPU yok | CPU baseline performansını belirler |
| Operasyon donanımı | GPU bulunan Windows bilgisayarlar | Son saha performansı GPU ile ayrıca ölçülmelidir |
| Masaların sabitliği | Karar bekliyor | Kalibrasyon yenileme sıklığını etkiler |

## Notlar

- İlk prototipte T.UTYM#2 için 14 masa ve masa başına 1 sandalye üzerinden masa doluluk tespiti yapılacaktır.
- Bir sonraki geliştirme aşaması, kullanıcı tarafından seçilen lokal geçmiş videoyu işleyip 14 masa için dolu/boş sonucu üretmeye odaklanmalıdır.
- Kamera tipi RTSP destekli IP video olduğundan ilk canlı bağlantı testi gerçek RTSP URL repo’ya yazılmadan lokal ortamda yapılmalıdır.
- İlk algoritma denemesi canlı kamera yerine lokal geçmiş video üzerinden yapılabilir; gerçek dosya repo’ya eklenmemelidir.
