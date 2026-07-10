# İlk UTYM Prototipi Gereksinim Dokümanı

Bu doküman, ilk prototipin çalışacağı UTYM ortamı ve görüntü işleme kapsamı için temel gereksinimleri tek yerde toplar.

## 1. UTYM Bilgileri

| No | Gereksinim | Değer / Açıklama |
| --- | --- | --- |
| 1 | İlk prototipin çalışacağı UTYM adı veya kodu | T.UTYM#2 |
| 2 | UTYM’deki kamera sayısı | Karar bekliyor — ilk prototip için en az 1 IP kamera kullanılacak |

## 2. Kamera Bilgileri

| No | Gereksinim | Değer / Açıklama |
| --- | --- | --- |
| 3 | İlk prototipte kullanılacak kamera | T.UTYM#2 ortamındaki ilk IP video kamera; kamera ID ve RTSP/yerel video erişim bilgisi saha kurulumunda belirlenecek |
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
| 10 | İnternetsiz çalışma zorunluluğu | Evet — uygulama offline/lokal ortamda çalışacak şekilde tasarlanmalıdır |
| 11 | Görüntü kaydı tutulup tutulmayacağı | Hayır — gerçek görüntü/video repo’ya konmayacak ve paylaşılmayacak |

## 5. İlk Hedef Kapsamı

| No | Gereksinim | Değer / Açıklama |
| --- | --- | --- |
| 12 | İlk hedefin masa bazlı mı sandalye bazlı mı olduğu | Masa bazlı doluluk; her masada 1 sandalye olduğu için masa sonucu pratikte tek koltuk doluluk sonucuna karşılık gelir |

## 6. Gerçek Veri Kullanım Kısıtı

- Gerçek T.UTYM#2 görüntüleri ve videoları repo’ya eklenmeyecektir.
- Gerçek görüntü/video asistanla veya dış ortamla paylaşılmayacaktır.
- Geliştirme reposunda yalnızca sentetik/anonim örnek veri, kalibrasyon şablonu ve test fixture'ları tutulacaktır.
- Saha doğrulaması, kurum içi Windows makinede ve gerçek IP video kaynağına erişimi olan operatör tarafından çalıştırılacaktır.
- Kalibrasyon noktaları gerçek görüntü paylaşılmadan; kullanıcı tarafından lokal kalibrasyon ekranında veya koordinat dosyası üzerinden girilecektir.

## 7. Açık Kararlar

| Konu | Durum | Etki |
| --- | --- | --- |
| Toplam kamera sayısı | Karar bekliyor | Çoklu kamera birleştirme kapsamını etkiler |
| İlk kamera ID / RTSP URL | Saha kurulumunda belirlenecek | Canlı IP video bağlantı testini etkiler |
| FPS | Karar bekliyor | Performans kabul kriterini etkiler |
| Masaların sabitliği | Karar bekliyor | Kalibrasyon yenileme sıklığını etkiler |

## Notlar

- İlk prototipte T.UTYM#2 için 14 masa ve masa başına 1 sandalye üzerinden masa doluluk tespiti yapılacaktır.
- Gerçek veri paylaşılmayacağı için bir sonraki geliştirme aşaması, gerçek görüntü gerektirmeyen Windows offline kurulum, kalibrasyon ve saha doğrulama prosedürlerine odaklanmalıdır.
- Kamera tipi IP video olduğundan RTSP/ONVIF veya kurum içi kamera yazılımından alınacak yerel stream/file erişimi ayrıca netleştirilmelidir.
