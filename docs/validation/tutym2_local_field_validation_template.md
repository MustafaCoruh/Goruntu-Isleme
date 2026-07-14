# T.UTYM#2 Lokal Saha Doğrulama Raporu Şablonu

Bu şablon, T.UTYM#2 lokal fotoğraf/video demosu çalıştırıldıktan sonra gerçek görüntü veya video paylaşmadan sonuçları raporlamak için kullanılır. Rapor, teknik olmayan operatörün doldurabileceği şekilde hazırlanmıştır.

## 1. Raporun Amacı

Bu raporun amacı, T.UTYM#2 masa doluluk sisteminin gerçek görüntü paylaşmadan ilk saha başarımını ölçmektir.

Cevaplanacak ana sorular:

```text
Masa poligonları doğru yerde mi?
Model insanları bulabiliyor mu?
Dolu masalar dolu görünüyor mu?
Boş masalar boş görünüyor mu?
Hangi masalarda hata var?
Sistem yeterince hızlı mı?
```

## 2. Paylaşılmaması Gerekenler

Bu rapora şu bilgiler eklenmemelidir:

- Gerçek fotoğraf.
- Gerçek video.
- RTSP URL.
- Kamera IP adresi.
- Kamera kullanıcı adı/parolası.
- Katılımcı adı veya kişi bilgisi.
- Ekran görüntüsü içinde hassas veri varsa ekran görüntüsü.

Sadece sayısal sonuçlar, genel gözlemler ve masa numarası bazlı hata türleri yazılmalıdır.

## 3. Test Bilgileri

| Alan | Değer |
| --- | --- |
| Rapor tarihi | YYYY-AA-GG |
| Testi yapan kişi/ekip | Kurum içi ekip adı; kişi adı gerekiyorsa kurum politikasına göre yazın |
| UTYM | T.UTYM#2 |
| Kamera | TUTYM2-CAM-001 |
| Test tipi | Lokal fotoğraf / Lokal video / RTSP canlı |
| Görüntü çözünürlüğü | 1920x1080 |
| Masa sayısı | 14 |
| Masa başına sandalye | 1 |
| Kullanılan config dosyası | `C:\FTMC_FIELD_DATA\configs\tutym2_cam_001.local.json` |
| Kullanılan model dosyası | `C:\FTMC_FIELD_DATA\models\person_detector.onnx` |
| Güvenli otomatik rapor | `C:\FTMC_FIELD_DATA\reports\demo_result.json` |
| Test bilgisayarı | CPU/GPU/RAM bilgisi |
| İnternet durumu | Offline / Kontrollü internet / Bilinmiyor |

## 4. Kalibrasyon Kontrolü

| Kontrol | Sonuç | Not |
| --- | --- | --- |
| UTYM ID `T.UTYM#2` mi? | Evet / Hayır |  |
| Kamera ID `TUTYM2-CAM-001` mi? | Evet / Hayır |  |
| Config içinde 14 masa var mı? | Evet / Hayır |  |
| Tüm masalarda kapasite 1 mi? | Evet / Hayır |  |
| Masa poligonları görselde doğru yerde mi? | Evet / Hayır / Kısmen |  |
| Gerçek görüntü/video paylaşılmadı mı? | Evet / Hayır |  |

## 5. Test Kapsamı

Aşağıdaki tablodan yalnızca kullanılan test tiplerini doldurun.

| Test tipi | Adet / Süre | Açıklama |
| --- | ---: | --- |
| Lokal fotoğraf |  | Örn. 10 fotoğraf |
| Lokal video |  | Örn. 2 dakika |
| RTSP canlı |  | Örn. 5 dakika |

## 6. Masa Bazlı Sonuç Tablosu

Her masa için gözlenen sonucu doldurun. Görüntü paylaşmadan yalnızca masa numarası ve karar sonucu yazılır.

| Masa | Beklenen durum | Sistem sonucu | Doğru mu? | Hata türü | Not |
| --- | --- | --- | --- | --- | --- |
| Masa 1 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |
| Masa 2 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |
| Masa 3 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |
| Masa 4 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |
| Masa 5 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |
| Masa 6 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |
| Masa 7 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |
| Masa 8 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |
| Masa 9 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |
| Masa 10 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |
| Masa 11 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |
| Masa 12 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |
| Masa 13 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |
| Masa 14 | Dolu / Boş | Dolu / Boş / Belirsiz | Evet / Hayır | Yok / False Empty / False Occupied / Belirsiz |  |

## 7. Metrik Özeti

Aşağıdaki değerleri testten sonra doldurun.

| Metrik | Değer | Nasıl hesaplanır? |
| --- | ---: | --- |
| Toplam masa kararı |  | Test edilen görüntü sayısı × 14 masa |
| Doğru karar sayısı |  | Sistem sonucu beklenenle aynı olan kararlar |
| Masa bazlı doğruluk |  | Doğru karar / toplam karar |
| False Empty sayısı |  | Dolu masayı boş gösterme |
| False Occupied sayısı |  | Boş masayı dolu gösterme |
| Belirsiz karar sayısı |  | Sistem sonucu `Belirsiz` olan kararlar |
| Ortalama FPS |  | Operatör veya logdan alınır |
| En düşük FPS |  | Operatör veya logdan alınır |
| CPU kullanımı |  | Yaklaşık yüzde veya gözlem |
| GPU kullanımı |  | Varsa yaklaşık yüzde veya gözlem |
| RAM kullanımı |  | Yaklaşık değer |

## 8. Hata Türleri Nasıl Yorumlanır?

| Hata türü | Anlamı | Öncelik |
| --- | --- | --- |
| False Empty | Dolu masayı boş gösterdi | Kritik |
| False Occupied | Boş masayı dolu gösterdi | Orta |
| Belirsiz | Sistem kararsız kaldı | İncelenmeli |
| Poligon hatası | Masa alanı yanlış çizilmiş olabilir | Kalibrasyon düzeltmesi gerekir |
| Model hatası | Kişi hiç bulunmamış veya yanlış bulunmuş olabilir | Model/ışık/açı incelenmeli |

## 9. Genel Gözlemler

Aşağıdaki sorulara kısa cevap yazın:

```text
Kamera açısı masaları yeterince görüyor mu?
Masaların üstü veya sandalyeler başka nesnelerle kapanıyor mu?
Işık değişimi tespiti bozuyor mu?
Monitörler veya koltuklar insan tespitini yanıltıyor mu?
Hangi masalarda hata daha sık?
Kalibrasyon noktaları doğru mu?
```

## 10. Karar

Test sonunda bir karar seçin:

```text
[ ] Devam edilebilir: Lokal foto/video test sonucu yeterli.
[ ] Kalibrasyon düzeltilmeli: Masa poligonlarında hata var.
[ ] Model iyileştirilmeli: İnsan tespiti zayıf.
[ ] Kamera açısı/ışık iyileştirilmeli.
[ ] RTSP canlı teste geçilebilir.
[ ] Henüz RTSP canlı teste geçilmemeli.
```

## 11. Sonraki Aksiyonlar

| Aksiyon | Sorumlu | Hedef tarih | Durum |
| --- | --- | --- | --- |
|  |  |  | Bekliyor |
|  |  |  | Bekliyor |
|  |  |  | Bekliyor |

## 12. Rapor Paylaşım Notu

Bu rapor yalnızca görüntü içermeyen sonuçlar, sayısal metrikler ve genel gözlemler içeriyorsa paylaşılabilir. Gerçek görüntü, video, RTSP URL, IP adresi veya kişi bilgisi içeriyorsa paylaşılmamalıdır.
