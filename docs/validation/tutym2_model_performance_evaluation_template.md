# T.UTYM#2 Model Performans Değerlendirme Şablonu

Bu şablon, T.UTYM#2 için modelin masa dolu/boş kararlarını gerçek görüntü, video, RTSP URL, IP adresi veya kişisel veri paylaşmadan değerlendirmek için hazırlanmıştır.

Amaç:

```text
Model masaları doğru dolu/boş sınıflandırıyor mu?
Hangi masalarda hata yapıyor?
Yanlış dolu mu daha fazla, yanlış boş mu daha fazla?
Belirsiz karar var mı?
Işık, açı veya oturma pozisyonu sonucu etkiliyor mu?
```

Bu dosya bir rapor şablonudur. Gerçek görüntü veya video eklenmemelidir.

## 1. Değerlendirme Bilgileri

| Alan | Değer |
| --- | --- |
| UTYM | `T.UTYM#2` |
| Kamera | `TUTYM2-CAM-001` |
| Masa sayısı | `14` |
| Değerlendirme tarihi | `YYYY-MM-DD` |
| Değerlendiren rol | `Operatör / Test sorumlusu / Geliştirici` |
| Kullanılan config dosya adı | `tutym2_cam_001.local.json` veya `tutym2_cam_001.rtsp.local.json` |
| Kullanılan model dosya adı | `person_detector.onnx` |
| Model versiyonu | `...` |
| Test tipi | `Lokal fotoğraf / Lokal video / RTSP canlı` |
| Görüntü paylaşımı yapıldı mı? | `Hayır` |
| RTSP URL paylaşıldı mı? | `Hayır` |

## 2. Test Koşulları

| Koşul | Seçenek / Açıklama |
| --- | --- |
| Işık durumu | `Normal / Loş / Parlak / Karışık` |
| Katılımcı yoğunluğu | `Boş / Az / Orta / Yoğun` |
| Sandalyeler görünür mü? | `Evet / Hayır / Kısmen` |
| Masalar net görünür mü? | `Evet / Hayır / Kısmen` |
| Kamera açısı değişti mi? | `Hayır / Evet` |
| Kalibrasyon yeni mi? | `Evet / Hayır` |
| Test süresi | `... dakika` |
| Ortalama FPS | `...` |

Bu bilgiler model sonucunu yorumlamak için kullanılır; gerçek görüntü paylaşımı yerine bağlam sağlar.

## 3. Karar Etiketleri

Değerlendirmede şu etiketler kullanılmalıdır:

| Etiket | Anlamı |
| --- | --- |
| `TP` | True Positive: Gerçekte dolu, sistem dolu dedi |
| `TN` | True Negative: Gerçekte boş, sistem boş dedi |
| `FP` | False Positive: Gerçekte boş, sistem dolu dedi |
| `FN` | False Negative: Gerçekte dolu, sistem boş dedi |
| `UNK` | Belirsiz: Sistem karar veremedi veya operatör emin değil |

Kritik fark:

```text
FP = Yanlış dolu kararı
FN = Yanlış boş kararı
```

UTYM kullanımında `FN` yani dolu masayı boş sanmak bazı senaryolarda daha kritik olabilir.

## 4. Masa Bazlı Değerlendirme Tablosu

Her masa için gerçek durum ve sistem kararı işaretlenmelidir.

| Masa ID | Gerçek durum | Sistem kararı | Sonuç etiketi | Güven skoru | Not |
| --- | --- | --- | --- | --- | --- |
| `table_01` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |
| `table_02` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |
| `table_03` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |
| `table_04` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |
| `table_05` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |
| `table_06` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |
| `table_07` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |
| `table_08` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |
| `table_09` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |
| `table_10` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |
| `table_11` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |
| `table_12` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |
| `table_13` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |
| `table_14` | `Dolu/Boş` | `Dolu/Boş/Belirsiz` | `TP/TN/FP/FN/UNK` | `0.00-1.00` | `...` |

Not alanına görüntü veya kişi bilgisi yazılmamalıdır. Yalnızca güvenli teknik açıklama yazılmalıdır.

Örnek güvenli notlar:

```text
Masa kısmen kapalı.
Sandalye masadan uzak.
Işık yansıması var.
Kişi masanın kenarında oturuyor.
Kalibrasyon polygonu dar olabilir.
```

## 5. Toplam Sonuç Özeti

Aşağıdaki sayılar doldurulmalıdır:

| Metrik | Değer |
| --- | ---: |
| Toplam masa sayısı | `14` |
| TP sayısı | `...` |
| TN sayısı | `...` |
| FP sayısı | `...` |
| FN sayısı | `...` |
| UNK sayısı | `...` |
| Doğru karar sayısı (`TP + TN`) | `...` |
| Yanlış karar sayısı (`FP + FN`) | `...` |
| Değerlendirilebilir masa sayısı (`14 - UNK`) | `...` |

## 6. Basit Doğruluk Hesabı

İlk değerlendirme için basit doğruluk şöyle hesaplanır:

```text
Doğruluk = (TP + TN) / (TP + TN + FP + FN)
```

`UNK` kararları doğruluk hesabına dahil edilmez; ayrıca raporlanır.

Örnek:

```text
TP = 7
TN = 5
FP = 1
FN = 1
UNK = 0

Doğruluk = (7 + 5) / (7 + 5 + 1 + 1)
Doğruluk = 12 / 14
Doğruluk = %85.7
```

## 7. Hata Türü Yorumu

| Hata türü | Anlamı | Olası sebep | İlk aksiyon |
| --- | --- | --- | --- |
| FP yüksek | Boş masalar dolu sanılıyor | Sandalye/çanta/gölge kişi gibi algılanıyor olabilir | Model eşiği ve masa polygonu kontrol edilmeli |
| FN yüksek | Dolu masalar boş sanılıyor | Kişi kısmen görünmüyor veya polygon yanlış olabilir | Kalibrasyon ve kamera açısı kontrol edilmeli |
| UNK yüksek | Sistem çok kararsız | Görüntü kalitesi, ışık, FPS veya model zayıf olabilir | Test koşulları ve model performansı incelenmeli |

## 8. Masa Bazlı Sorun Listesi

Hata yapan veya kararsız olan masalar ayrıca yazılmalıdır.

| Masa ID | Sorun tipi | Kısa güvenli açıklama | Önerilen aksiyon |
| --- | --- | --- | --- |
| `table_..` | `FP/FN/UNK` | `...` | `Kalibrasyon / model / kamera açısı / ışık` |

Örnek:

```text
table_05 | FN | Kişi masa polygonunun dışında kalıyor olabilir | Polygon genişletilmeli
table_09 | FP | Sandalye/masa kenarı kişi gibi algılanıyor olabilir | Model eşiği kontrol edilmeli
```

## 9. Kabul Eşiği

İlk saha prototipi için önerilen başlangıç eşiği:

```text
Doğruluk >= %80
FN sayısı <= 2
FP sayısı <= 2
UNK sayısı <= 2
```

Bu değerler ilk saha testinden sonra revize edilebilir.

Ürünleşmeye yaklaşırken hedef daha yüksek olmalıdır:

```text
Doğruluk >= %90
FN sayısı mümkün olduğunca düşük
FP sayısı operasyonu yanıltmayacak seviyede
UNK kararları açıklanabilir ve yönetilebilir
```

## 10. Son Karar

Değerlendirme sonunda aşağıdaki kararlardan biri seçilir:

```text
[ ] Model ilk saha prototipi için yeterli.
[ ] Kalibrasyon düzeltilip tekrar test edilmeli.
[ ] Kamera açısı/çözünürlük/ışık koşulu düzeltilmeli.
[ ] Model eşiği veya model dosyası değiştirilmeli.
[ ] Daha fazla test örneği gerekiyor.
[ ] Ürünleşme aşamasına geçmek için henüz erken.
```

## 11. Paylaşılabilir Güvenli Özet

Gerçek görüntü paylaşmadan şu formatta özet verilebilir:

```text
UTYM: T.UTYM#2
Kamera: TUTYM2-CAM-001
Test tipi: Lokal video / RTSP canlı
Toplam masa: 14
TP: ...
TN: ...
FP: ...
FN: ...
UNK: ...
Doğruluk: ...%
Ortalama FPS: ...
En sorunlu masalar: table_.., table_..
Görüntü paylaşılmadı: Evet
RTSP URL paylaşılmadı: Evet
Son karar: ...
```

## 12. Dikkat Edilecek Güvenlik Kuralları

Bu değerlendirme sırasında şunlar yapılmamalıdır:

```text
Gerçek görüntü eklemek
Gerçek video eklemek
RTSP URL yazmak
Kamera IP adresi yazmak
Kullanıcı adı/parola yazmak
Kişi adı yazmak
Yüz görüntüsü paylaşmak
Tam lokal dosya path'i paylaşmak
```

Bu kurallara uyulursa model performansı güvenli şekilde tartışılabilir.
