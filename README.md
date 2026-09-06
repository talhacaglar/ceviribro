# DTR · Instant Translator

[English](#english) · [Türkçe](#türkçe)

![Live English → Turkish translation in DTR / DTR içinde canlı İngilizce → Türkçe çeviri](assets/screenshot-dark.png)

## English

A keyboard-first terminal translator powered by DeepL. Translate as you type, choose source and target languages, and keep your last language pair between sessions.

### Features

- Automatic translation after a short typing pause; immediate translation with `Ctrl+J`.
- DeepL language lists, automatic source detection, and persistent language selection.
- Dark/light themes, Omarchy palette integration, and clipboard shortcuts.

### Getting started

Run the launcher from the cloned repository. It creates `.venv` and installs the app. A DeepL API key is required; the setup screen stores it in the Git-ignored `.env` file.

```bash
git clone https://github.com/talhacaglar/tui-translator.git
cd tui-translator
./run.sh
```

`F3`: auto → Turkish · `F4` / `Ctrl+E`: Turkish → English · `Ctrl+G`: paste · `Ctrl+Y`: copy · `Ctrl+L`: clear · `F2`: theme · `Ctrl+Q`: quit. Clipboard support requires `wl-clipboard` on Wayland, or `xclip`/`xsel` on X11.

Language preferences live in `~/.config/ceviri-tui/languages.json` (`XDG_CONFIG_HOME` supported). Run tests with `.venv/bin/python -m unittest discover -s tests -v`.

## Türkçe

DeepL destekli, klavye odaklı terminal çeviri uygulaması. Yazarken çevirin, kaynak ve hedef dili seçin; son dil çifti sonraki açılışta korunsun.

### Özellikler

- Yazmaya kısa bir ara verildiğinde otomatik çeviri; `Ctrl+J` ile anında çeviri.
- DeepL dil listeleri, otomatik kaynak algılama ve kalıcı dil seçimi.
- Koyu/açık tema, Omarchy paletiyle uyum ve pano kısayolları.

### Başlangıç

Klonlanan depoda başlatıcıyı çalıştırın. `.venv` oluşturulur ve uygulama kurulur. DeepL API anahtarı gerekir; kurulum ekranı anahtarı Git tarafından dışlanan `.env` dosyasında saklar.

```bash
git clone https://github.com/talhacaglar/tui-translator.git
cd tui-translator
./run.sh
```

`F3`: otomatik → Türkçe · `F4` / `Ctrl+E`: Türkçe → İngilizce · `Ctrl+G`: yapıştır · `Ctrl+Y`: kopyala · `Ctrl+L`: temizle · `F2`: tema · `Ctrl+Q`: çıkış. Pano için Wayland üzerinde `wl-clipboard`, X11 üzerinde `xclip` veya `xsel` gerekir.

Dil tercihleri `~/.config/ceviri-tui/languages.json` dosyasındadır (`XDG_CONFIG_HOME` desteklenir). Test komutu: `.venv/bin/python -m unittest discover -s tests -v`.
