# T.UTYM#2 Statik Dashboard Operatör Kılavuzu

Bu kılavuz, ilk statik operatör dashboard dosyasının nasıl kontrol edileceğini anlatır.

## 1. Dosya

VS Code içinde şu dosya bulunmalıdır:

```text
app/ui/static/tutym2_dashboard.html
```

Bu dosya kamera açmaz, RTSP bağlantısı kurmaz ve gerçek görüntü okumaz. Sadece güvenli `dashboard_state.json` dosyasını veya gömülü örnek state'i ekranda gösterir.

## 2. Dashboard Ne Gösterir?

```text
Genel durum
UTYM ve kamera ID
Bağlantı durumu
Ortalama FPS
14 masa özeti
14 masa kartı
Uyarılar
Kritikler
Kaynak rapor durumları
Safety özeti
```

## 3. Güvenlik

Dashboard gerçek RTSP URL, IP, credential, görüntü veya tam lokal path göstermemelidir.

İlk sürüm statiktir ve sadece operatör ekran taslağını göstermek içindir.

## 4. VS Code Kontrolü

Dosya içinde şu ifadeler aranabilir:

```text
T.UTYM#2 Operatör Dashboard
SAFE_EXAMPLE_STATE
Güvenli Örnek State Yükle
14 Masa Kartı
contains_rtsp_url
```
