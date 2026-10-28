# ceviribro · Instant Translator

[English](#english) · [Türkçe](#türkçe)

![Live English → Turkish translation in ceviribro / ceviribro içinde canlı İngilizce → Türkçe çeviri](assets/screenshot-dark.png)

## English

A keyboard-first terminal translator powered by DeepL. Translate as you type, choose source and target languages, and keep your last language pair between sessions.

### Features

- Automatic translation after a short typing pause; immediate translation with `Ctrl+J`.
- DeepL language lists, automatic source detection, and persistent language selection.
- Minimal layout that stays readable in small windows: one language row, two text areas, a status line and a shortcut line.
- Dark/light themes, Omarchy palette integration, and clipboard shortcuts.

### Getting started

On Arch Linux, install it from the AUR and run `ceviribro`:

```bash
yay -S ceviribro
```

Or run the launcher from a cloned repository. It creates `.venv` and installs the app. A DeepL API key is required; the setup screen stores it in `~/.config/ceviribro/.env` with owner-only permissions (`XDG_CONFIG_HOME` supported). Existing project `.env` files remain readable.

```bash
git clone https://github.com/talhacaglar/ceviribro.git
cd ceviribro
./run.sh
```

`F3`: auto → Turkish · `F4` / `Ctrl+E`: Turkish → English · `Ctrl+G`: paste · `Ctrl+Y`: copy · `Ctrl+L`: clear · `F2`: theme · `Ctrl+Q`: quit. Clipboard support requires `wl-clipboard` on Wayland, or `xclip`/`xsel` on X11.

Language preferences live in `~/.config/ceviribro/languages.json` (`XDG_CONFIG_HOME` supported). Run tests with `.venv/bin/python -m unittest discover -s tests -v`.

## Türkçe

DeepL destekli, klavye odaklı terminal çeviri uygulaması. Yazarken çevirin, kaynak ve hedef dili seçin; son dil çifti sonraki açılışta korunsun.

### Özellikler

- Yazmaya kısa bir ara verildiğinde otomatik çeviri; `Ctrl+J` ile anında çeviri.
- DeepL dil listeleri, otomatik kaynak algılama ve kalıcı dil seçimi.
- Küçük pencerede de okunan sade düzen: tek satır dil seçimi, iki metin alanı, durum ve kısayol satırı.
- Koyu/açık tema, Omarchy paletiyle uyum ve pano kısayolları.

### Başlangıç

Arch Linux'ta AUR'dan kurup `ceviribro` ile çalıştırın:

```bash
yay -S ceviribro
```

Ya da klonlanan depoda başlatıcıyı çalıştırın. `.venv` oluşturulur ve uygulama kurulur. DeepL API anahtarı gerekir; kurulum ekranı anahtarı yalnız kullanıcının okuyabildiği `~/.config/ceviribro/.env` dosyasında saklar (`XDG_CONFIG_HOME` desteklenir). Mevcut proje `.env` dosyaları da okunmaya devam eder.

```bash
git clone https://github.com/talhacaglar/ceviribro.git
cd ceviribro
./run.sh
```

`F3`: otomatik → Türkçe · `F4` / `Ctrl+E`: Türkçe → İngilizce · `Ctrl+G`: yapıştır · `Ctrl+Y`: kopyala · `Ctrl+L`: temizle · `F2`: tema · `Ctrl+Q`: çıkış. Pano için Wayland üzerinde `wl-clipboard`, X11 üzerinde `xclip` veya `xsel` gerekir.

Dil tercihleri `~/.config/ceviribro/languages.json` dosyasındadır (`XDG_CONFIG_HOME` desteklenir). Test komutu: `.venv/bin/python -m unittest discover -s tests -v`.
