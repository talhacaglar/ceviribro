# ceviri-tui 🌍 ➜ 🇹🇷

DeepL ile **anlık Türkçe çeviri** yapan, şık bir terminal (TUI) uygulaması.
Textual ile yazıldı; renkli paneller, geçmiş listesi, kota göstergesi ve
klavye kısayolları içerir.

```
 ██████╗███████╗██╗   ██╗██╗██████╗ ██╗
██╔════╝██╔════╝██║   ██║██║██╔══██╗██║    🌍 ➜ 🇹🇷
██║     █████╗  ██║   ██║██║██████╔╝██║
╚██████╗███████╗ ╚████╔╝ ██║██║  ██║██║    DeepL ile anlık çeviri
 ╚═════╝╚══════╝  ╚═══╝  ╚═╝╚═╝  ╚═╝╚═╝
```

## Özellikler

- 📝 Sol panele metin yaz, `Ctrl+J` ile anında Türkçeye çevir
- 🔍 Kaynak dili otomatik algılar (DeepL)
- 📋 `Ctrl+Y` ile çeviriyi panoya kopyala
- 🕘 Son çevirilerin geçmişi
- 📊 DeepL karakter kotası göstergesi
- 🔑 API anahtarı `.env` dosyasında saklanır; yoksa açılışta sorulur

## Kurulum

```bash
git clone https://github.com/talhacaglar/ceviri-tui.git
cd ceviri-tui
./run.sh
```

`run.sh` ilk çalıştırmada sanal ortamı (`.venv`) kurar ve bağımlılıkları
yükler. Sonraki çalıştırmalarda doğrudan uygulamayı açar.

### API anahtarı

DeepL API anahtarını iki şekilde verebilirsin:

1. `.env.example` dosyasını `.env` olarak kopyala ve anahtarını yaz:
   ```bash
   cp .env.example .env
   # .env içindeki DEEPL_AUTH_KEY değerini düzenle
   ```
2. Veya uygulamayı çalıştır; anahtar yoksa açılış ekranında sorulur ve
   otomatik olarak `.env` dosyasına kaydedilir.

> Free/developer hesaplarında anahtar `:fx` ile biter ve `api-free.deepl.com`
> uç noktası kullanılır. Resmi `deepl` paketi bunu otomatik seçer.

## Kısayollar

| Kısayol    | İşlev                     |
| ---------- | ------------------------- |
| `Ctrl+J`   | Çevir                     |
| `Ctrl+Y`   | Çeviriyi panoya kopyala   |
| `Ctrl+L`   | Alanları temizle          |
| `Ctrl+U`   | Kotayı yenile             |
| `Q`        | Çıkış                     |

## Pano desteği (Linux)

Kopyalama için sistemde bir pano aracı gerekir:

- Wayland: `wl-clipboard`
- X11: `xclip` veya `xsel`

## Lisans

MIT
