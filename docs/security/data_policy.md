# Veri Saklama ve Erişim Politikası

Bu doküman, kamera videolarının işlenmesi, anonim doluluk sonuçlarının saklanması, log kayıtları, veritabanı erişimi ve offline ortamdan veri aktarımı konularındaki kararları yazılı hale getirir.

## Kararlar

| No | Konu | Karar |
| --- | --- | --- |
| 1 | Kamera görüntüleri kaydedilecek mi? | Hayır. Kamera görüntüleri kalıcı olarak kaydedilmeyecektir. Görüntüler yalnızca anlık işleme amacıyla kullanılacaktır. |
| 2 | Sadece doluluk sonuçları mı saklanacak? | Evet. Sistemde yalnızca doluluk tespit sonuçları ve bu sonuçlara ait zaman bilgisi gibi operasyonel veriler saklanacaktır. |
| 3 | Kişi bilgisi saklanacak mı? | Hayır. Ad, soyad, kimlik numarası, personel numarası, biyometrik veri veya kişiyi doğrudan/ dolaylı tanımlayabilecek bilgi saklanmayacaktır. |
| 4 | Log kayıtlarının kaç gün tutulacağı | Log kayıtları en fazla 30 gün tutulacaktır. Bu sürenin sonunda loglar otomatik olarak silinecek veya geri döndürülemeyecek şekilde anonimleştirilecektir. |
| 5 | Veritabanı dosyasına kimlerin erişebileceği | Veritabanı dosyasına yalnızca sistem yöneticileri ve proje kapsamında yetkilendirilmiş teknik personel erişebilecektir. Erişimler görev gerekliliği ve en az yetki prensibine göre sınırlandırılacaktır. |
| 6 | Offline ortamdan dışarı veri aktarımı yapılıp yapılmayacağı | Hayır. Offline ortamdan dışarı veri aktarımı yapılmayacaktır. Zorunlu bakım veya denetim ihtiyacı doğarsa aktarım ancak yazılı kurumsal onay, kayıt altına alma ve yetkili personel gözetimi ile gerçekleştirilebilir. |

## Uygulama İlkeleri

- Kamera görüntüleri geçici işlem belleği dışında tutulmamalı ve dosya sistemine kalıcı kayıt olarak yazılmamalıdır.
- Saklanan doluluk sonuçları kişi tespitine veya kimliklendirmeye imkân vermeyecek şekilde tasarlanmalıdır.
- Veritabanı ve log dosyaları yetkisiz erişime karşı dosya sistemi izinleriyle korunmalıdır.
- Log içerikleri kişisel veri, görüntü karesi veya biyometrik veri içermemelidir.
- Bu politika kapsamındaki kararların değiştirilmesi durumunda değişiklik gerekçesi, onaylayan kişiler ve yürürlük tarihi ayrıca kayıt altına alınmalıdır.
