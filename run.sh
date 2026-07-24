#!/usr/bin/env bash
# ceviri-tui başlatıcı: venv'i kullanarak uygulamayı çalıştırır.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "venv bulunamadı, oluşturuluyor..."
    python3 -m venv .venv
    .venv/bin/pip install --quiet --upgrade pip
    .venv/bin/pip install --quiet textual deepl pyperclip python-dotenv
fi

exec .venv/bin/python -m ceviri_tui
