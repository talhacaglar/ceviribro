#!/usr/bin/env bash
# DTR başlatıcı: yerel sanal ortamı hazırlayıp paketi çalıştırır.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "venv bulunamadı, oluşturuluyor..."
    python3 -m venv .venv
    .venv/bin/pip install --quiet --upgrade pip
    .venv/bin/pip install --quiet -e .
fi

exec .venv/bin/python -m ceviri_tui
