# Yüz Tanıma Ön Değerlendirmesi

Bu doküman, UTYM görüntü işleme prototipinde yüz tanıma veya yüz embedding tabanlı kimliklendirme düşünülmeden önce tamamlanması gereken hukuki, kurumsal, teknik ve operasyonel değerlendirmeyi özetler. Bu çalışma tamamlanmadan ve gerekli onaylar alınmadan yüz tanıma implementasyonuna başlanmamalıdır.

## Karar Özeti

| No | Başlık | Ön Değerlendirme | Karar / Aksiyon |
| --- | --- | --- | --- |
| 1 | Yüz tanımanın hukuki uygunluğu | Yüz tanıma, kişiyi benzersiz biçimde tanımlamaya yönelik biyometrik veri işleme riski taşır. Bu nedenle mevcut doluluk tespiti kapsamından daha yüksek hukuki risk doğurur. | Hukuk birimi tarafından yazılı uygunluk değerlendirmesi yapılmadan kapsam dışı tutulmalıdır. |
| 2 | Açık rıza veya kurumsal onay gereksinimi | Yüz tanıma kullanımı, ilgili kişilerden açık rıza alınmasını veya uygulanabilir mevzuata göre geçerli başka bir işleme şartının açıkça belgelenmesini gerektirebilir. Kurum içi onay tek başına yeterli kabul edilmemelidir. | Açık rıza gereksinimi, aydınlatma metni, itiraz/geri çekme süreci ve kurumsal onay akışı netleşmeden geliştirme başlatılmamalıdır. |
| 3 | Yüz verisinin saklanıp saklanmayacağı | Ham yüz görüntüsü, yüz kesiti, video karesi veya yüz embedding verisi saklanması veri minimizasyonu ilkesine aykırı riskler oluşturabilir. Mevcut veri politikası, görüntü ve biyometrik veri saklamamayı esas alır. | Varsayılan karar: yüz verisi saklanmayacaktır. Saklama talebi doğarsa amaç, süre, erişim yetkileri, silme yöntemi ve hukuki dayanak ayrıca onaylanmalıdır. |
| 4 | Yüz embedding verilerinin şifrelenmesi | Embedding değerleri ham görüntü olmasa bile kişiyi ayırt etmeye yarayan biyometrik nitelikli veri olarak değerlendirilmelidir. Yetkisiz erişim, veri sızıntısı ve yeniden kimliklendirme riski vardır. | Embedding saklama onaylanırsa veri aktarımda ve depoda güçlü şifreleme, anahtar yönetimi, erişim loglama, rotasyon ve silme kontrolleri zorunlu olmalıdır. |
| 5 | Yanlış eşleşme riski | Yanlış pozitif eşleşme bir kişinin başka biriyle ilişkilendirilmesine; yanlış negatif eşleşme ise yetkili kişinin tanınmamasına yol açabilir. Işık, açı, maske, gözlük, yaş değişimi ve kamera kalitesi riski artırır. | Yüz tanıma zorunlu görülürse eşik değerleri, manuel doğrulama, itiraz mekanizması, hata metrikleri ve düzenli performans testi tasarlanmalıdır. |
| 6 | Kamera açılarının yüz tanıma için uygunluğu | Doluluk tespiti için konumlandırılmış kameralar çoğu zaman tepeden, geniş açıdan veya uzak mesafeden görüntü alır. Bu açılar yüz tanıma için yeterli yüz çözünürlüğü ve frontal açı sağlamayabilir. | Mevcut kameralar yüz tanıma amacıyla uygun varsayılmamalıdır. Her kamera için yüz piksel boyutu, açı, ışık ve kör nokta analizi yapılmalıdır. |
| 7 | Alternatif yöntemler | Manuel atama, RFID, badge ve login check-in yöntemleri kimliklendirme ihtiyacını biyometrik veri işlemeden karşılayabilir. Bu yöntemler daha düşük mahremiyet riski ve daha açık denetlenebilirlik sağlar. | Öncelik biyometrik olmayan alternatiflere verilmelidir. Yüz tanıma ancak alternatiflerin hedefleri karşılamadığı yazılı olarak gösterilirse yeniden değerlendirilebilir. |
| 8 | Yüz tanıma olmadan hedeflerin karşılanması | Mevcut prototip hedefleri masa/sandalye doluluğu, oturum takibi ve raporlama odaklıdır. Bu hedeflerin büyük bölümü kişiyi tanımadan, anonim doluluk olayları ve manuel/harici atama ile karşılanabilir. | İlk prototip yüz tanıma olmadan ilerlemelidir. Kimlik bazlı raporlama gerekiyorsa önce manuel atama, RFID, badge veya login check-in entegrasyonu denenmelidir. |

## Ayrıntılı Değerlendirme

### 1. Yüz tanımanın hukuki uygunluğu

Yüz tanıma, yalnızca görüntü işleme özelliği değil, kişiyi belirleme veya doğrulama amacı taşıdığında biyometrik veri işleme faaliyeti olarak ele alınmalıdır. Bu durum, mevcut sistemin anonim doluluk tespitinden farklı bir risk sınıfına geçmesine neden olur.

Uygulamaya geçmeden önce aşağıdaki konular yazılı olarak cevaplanmalıdır:

- İşleme amacı açık, belirli ve meşru mu?
- Aynı amaç daha az müdahaleci bir yöntemle karşılanabiliyor mu?
- İlgili kişiler kimlerdir ve hangi bilgilendirme yapılacaktır?
- Verinin işlenmesi, saklanması, aktarılması ve silinmesi hangi kurallara bağlıdır?
- Denetim, itiraz ve hata düzeltme süreçleri nasıl işletilecektir?

### 2. Açık rıza veya kurumsal onay gereksinimi

Kurumsal onay, proje yönetimi açısından gerekli olsa da yüz tanıma için tek başına yeterli bir güvence değildir. İlgili kişilerin açık rızası gerekip gerekmediği, rızanın özgür iradeyle verilip verilemeyeceği ve rızanın geri çekilmesi durumunda sistemin nasıl çalışacağı ayrıca değerlendirilmelidir.

Minimum gereksinimler:

- Hukuk birimi veya veri koruma sorumlusu tarafından onaylanmış aydınlatma metni.
- Açık rıza gerekiyorsa, rızanın kayıt altına alınması ve geri çekilebilmesi.
- Rıza vermeyen kişiler için eşdeğer alternatif süreç.
- Kurumsal risk kabulü ve yazılı proje onayı.

### 3. Yüz verisinin saklanıp saklanmayacağı

Mevcut yaklaşımda kamera görüntüleri kalıcı olarak saklanmamalı, sistem yalnızca operasyonel doluluk sonuçlarını tutmalıdır. Yüz verisi saklama kararı bu politikadan sapma anlamına gelir ve ayrı bir güvenlik mimarisi gerektirir.

Varsayılan saklama kararı şu şekilde olmalıdır:

- Ham video veya yüz görüntüsü saklanmaz.
- Yüz kesiti veya ekran görüntüsü saklanmaz.
- Yüz embedding verisi saklanmaz.
- Geçici bellek dışına biyometrik veri yazılmaz.

Bu varsayılanın değişmesi ancak yazılı hukuki değerlendirme, kurumsal onay ve teknik güvenlik tasarımı ile mümkün olmalıdır.

### 4. Yüz embedding verilerinin şifrelenmesi

Embedding verileri geri doğrudan fotoğrafa çevrilemese bile kişileri ayırt etmek ve veri kümeleri arasında eşleştirmek için kullanılabilir. Bu nedenle düşük riskli anonim veri gibi ele alınmamalıdır.

Embedding saklanması onaylanırsa en az şu kontroller gerekir:

- Depoda şifreleme.
- Aktarım sırasında şifreleme.
- Ayrı anahtar yönetimi ve anahtar rotasyonu.
- En az yetki prensibine göre erişim kontrolü.
- Erişim ve silme işlemleri için denetim logları.
- Belirli saklama süresi sonunda güvenli silme.
- Test ve geliştirme ortamlarında gerçek embedding kullanılmaması.

### 5. Yanlış eşleşme riski

Yüz tanıma sonuçları kesin kimlik kanıtı olarak görülmemelidir. Kamera koşullarına, model performansına ve eşik değerlerine bağlı olarak yanlış pozitif ve yanlış negatif sonuçlar oluşabilir.

Risk azaltma gereksinimleri:

- Model performansı UTYM ortamındaki gerçek kamera koşullarıyla ölçülmelidir.
- Eşik değerleri kullanım senaryosuna göre belgelenmelidir.
- Kritik kararlar otomatik eşleşmeye tek başına bağlanmamalıdır.
- Kullanıcıların hatalı eşleşmeye itiraz edebileceği süreç tanımlanmalıdır.
- Hata oranları düzenli olarak izlenmeli ve raporlanmalıdır.

### 6. Kamera açılarının yüz tanıma için uygunluğu

Doluluk tespiti için ideal kamera açısı ile yüz tanıma için ideal kamera açısı aynı değildir. Masa veya sandalye doluluğunu izleyen kameralar genellikle geniş alanı görecek şekilde yerleştirilir; bu da yüzlerin küçük, eğik, kısmen kapalı veya yetersiz aydınlatılmış görünmesine neden olabilir.

Her kamera için değerlendirilmesi gereken başlıklar:

- Yüzün görüntüdeki yaklaşık piksel boyutu.
- Frontal veya profile yakın açı oranı.
- Aydınlatma değişimi ve gölge etkisi.
- Hareket bulanıklığı.
- Kamera yüksekliği ve mesafesi.
- Oturma düzeni nedeniyle oluşan kapanmalar.

### 7. Alternatif yöntemler

Yüz tanıma yerine değerlendirilecek seçenekler:

| Yöntem | Avantaj | Sınırlama |
| --- | --- | --- |
| Manuel atama | Basit, düşük teknik riskli, biyometrik veri gerektirmez. | Operatör yükü ve insan hatası olabilir. |
| RFID | Hızlı ve otomasyon dostudur. | Kart unutma, başkasına kullandırma veya donanım maliyeti riski vardır. |
| Badge | Kurumsal kimlik kartlarıyla uyumludur. | Okuyucu entegrasyonu ve kart kullanım disiplini gerekir. |
| Login check-in | Yazılım tabanlıdır ve mevcut hesaplarla entegre olabilir. | Kullanıcının aktif işlem yapmasını gerektirir. |

Bu alternatifler, kişiyi otomatik olarak yüzünden tanımadan kimlik/oturum bilgisi sağlayabildiği için ilk değerlendirme kapsamına alınmalıdır.

### 8. Yüz tanıma olmadan hedeflerin karşılanması

İlk prototip hedefleri için yüz tanıma zorunlu görünmemektedir. Aşağıdaki hedefler biyometrik veri işlemeden karşılanabilir:

- Masa bazlı doluluk tespiti.
- Sandalye bazlı doluluk tespiti.
- Zaman bazlı doluluk raporu.
- Oturum başlangıç/bitiş tahmini.
- Operatör tarafından manuel oturum atama.
- Harici RFID, badge veya login check-in verisiyle oturum eşleştirme.

Bu nedenle yüz tanıma, ilk prototip için ön koşul veya varsayılan özellik olmamalıdır. Sistem mimarisi, doluluk tespiti ve anonim raporlama hedeflerini yüz tanıma olmadan tamamlayacak şekilde ilerlemelidir.

## Uygulamaya Başlama Ön Koşulları

Yüz tanıma implementasyonuna başlanabilmesi için aşağıdaki maddelerin tamamı tamamlanmış olmalıdır:

1. Hukuki uygunluk değerlendirmesi yazılı olarak onaylanmış olmalıdır.
2. Açık rıza veya alternatif hukuki dayanak gereksinimi netleştirilmiş olmalıdır.
3. Kurumsal risk kabulü ve proje onayı alınmış olmalıdır.
4. Yüz verisi ve embedding saklama kararı yazılı hale getirilmiş olmalıdır.
5. Saklama varsa şifreleme, anahtar yönetimi, erişim ve silme kontrolleri tasarlanmış olmalıdır.
6. Yanlış eşleşme için test, izleme, manuel doğrulama ve itiraz süreçleri belirlenmiş olmalıdır.
7. Kamera uygunluk analizi tamamlanmış olmalıdır.
8. Biyometrik olmayan alternatiflerin neden yeterli olmadığı belgelenmiş olmalıdır.

## Sonuç

Mevcut kapsamda yüz tanıma implementasyonuna başlanmamalıdır. Prototip, yüz tanıma olmadan doluluk tespiti ve anonim/alternatif kimlik eşleştirme yöntemleriyle ilerlemelidir. Yüz tanıma ancak yukarıdaki hukuki, kurumsal ve teknik ön koşullar tamamlandıktan sonra ayrı bir kapsam değişikliği olarak değerlendirilmelidir.
