# FTMC Occupancy

FTMC/UTYM ortamlarında **video görüntüsünden** masaların dolu veya boş olduğunu belirleyen, çevrimdışı çalışabilen görüntü işleme uygulaması.

## T.UTYM#2 için gerçek çalışma akışı

Bu sistemin kullanıcıdan beklediği ana girdi JSON raporu veya fotoğraf değil, **videodur**:

1. **Geliştirme aşaması:** T.UTYM#2 kamerasından daha önce alınmış bir video dosyası bilgisayardan seçilir.
2. Sistem videonun karelerini işler ve 14 masanın her biri için **dolu/boş** sonucu üretir.
3. Sonuçlar masa doluluk panelinde izlenir; hatalı masalar için kalibrasyon veya model ayarı yapılır.
4. **Ürün hazır olduğunda:** aynı işlem canlı kamera akışıyla veya kameradan alınmış eski bir video kaydıyla çalışır.

Desteklenen lokal video uzantıları: `.avi`, `.m4v`, `.mkv`, `.mov`, `.mp4`.

> Fotoğraf girişi bu akışın parçası değildir. `dashboard_state.json`, `field_handoff_summary.json` ve `r4_acceptance_gate.json` kullanıcıdan temin edilmesi gereken kaynak dosyalar değildir; bunlar yalnızca sistemin gerektiğinde üretebildiği teknik özetlerdir.

## Kullanılacak ana ekranlar

- Masa doluluk paneli: `app/ui/static/index.html`
- T.UTYM#2 doluluk görünümü: `app/ui/static/tutym2_dashboard.html`
- Masa bölgelerini tanımlama/düzeltme: `app/ui/static/calibration.html`
- Teknik hata ayıklama: `app/ui/static/debug.html`

## Geliştirme videosunu çalıştırma

Terminal kullanabilen geliştirici, video dosyasını repo dışında tutarak aşağıdaki giriş noktasını kullanır:

```bash
python scripts/run_tutym2_local_demo.py \
  --source "C:\\TUTYM2_DATA\\videos\\ornek.mp4" \
  --config "configs\\local\\tutym2_cam_001.json" \
  --output-dir "C:\\TUTYM2_DATA\\output"
```

Canlı kamera veya eski kamera kaydı aşamasında RTSP akışı için `scripts/run_tutym2_rtsp_demo.py` kullanılır. Gerçek video, RTSP adresi, kullanıcı adı, parola ve IP bilgileri repoya eklenmez.

## Projenin tamamlanma ölçütü

Proje üç JSON dosyasının seçilmesiyle değil, aşağıdaki iki video doğrulamasının başarıyla tamamlanmasıyla hazır sayılır:

- Lokal geçmiş videoda 14 masanın dolu/boş sonuçlarının doğrulanması.
- Canlı kamera akışında veya eski kamera kaydında aynı sonuçların doğrulanması.

Teknik durum özeti gerekirse `scripts/build_tutym2_project_status.py` bu iki doğrulama sonucuna göre bir JSON üretir; bu JSON bir video girdisinin yerine geçmez.
