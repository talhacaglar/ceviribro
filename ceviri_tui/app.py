"""ceviri-tui: DeepL ile anlık Türkçe çeviri yapan Textual TUI uygulaması."""

from __future__ import annotations

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
    TextArea,
)

from . import __version__
from .config import load_api_key, save_api_key
from .translator import Translator, TranslationError

LOGO = r""" ██████╗███████╗██╗   ██╗██╗██████╗ ██╗
██╔════╝██╔════╝██║   ██║██║██╔══██╗██║    🌍 ➜ 🇹🇷
██║     █████╗  ██║   ██║██║██████╔╝██║
╚██████╗███████╗ ╚████╔╝ ██║██║  ██║██║    DeepL ile anlık çeviri
 ╚═════╝╚══════╝  ╚═══╝  ╚═╝╚═╝  ╚═╝╚═╝"""


class ApiKeyScreen(ModalScreen[str]):
    """API anahtarı bulunamadığında gösterilen giriş ekranı."""

    def compose(self) -> ComposeResult:
        with Vertical(id="apikey-dialog"):
            yield Label("🔑 DeepL API anahtarı bulunamadı")
            yield Label(
                "Anahtarını gir (free hesaplarda ':fx' ile biter). "
                ".env dosyasına kaydedilecek.",
            )
            yield Input(
                placeholder="xxxxxxxx-xxxx-...-xxxx:fx",
                password=True,
                id="apikey-input",
            )
            with Horizontal(id="apikey-buttons"):
                yield Button("Kaydet", variant="success", id="save")
                yield Button("Çık", variant="error", id="quit")

    @on(Button.Pressed, "#save")
    @on(Input.Submitted, "#apikey-input")
    def _save(self) -> None:
        key = self.query_one("#apikey-input", Input).value.strip()
        if key:
            self.dismiss(key)

    @on(Button.Pressed, "#quit")
    def _quit(self) -> None:
        self.app.exit()


class CeviriApp(App):
    """Ana çeviri uygulaması."""

    CSS_PATH = "styles.tcss"
    TITLE = "ceviri-tui"
    SUB_TITLE = "DeepL ➜ Türkçe"

    BINDINGS = [
        ("ctrl+j", "translate", "Çevir"),
        ("ctrl+y", "copy", "Kopyala"),
        ("ctrl+l", "clear", "Temizle"),
        ("ctrl+u", "usage", "Kota"),
        ("q", "quit", "Çık"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.translator: Translator | None = None
        self._history: list[tuple[str, str]] = []

    def compose(self) -> ComposeResult:
        yield Static(LOGO, id="logo")
        with Horizontal(id="panels"):
            with Vertical(classes="panel", id="source-panel"):
                src = TextArea(id="source")
                src.border_title = "📝 Kaynak Metin"
                yield src
            with Vertical(classes="panel", id="target-panel"):
                tgt = TextArea(id="target", read_only=True)
                tgt.border_title = "🇹🇷 Türkçe Çeviri"
                yield tgt
        yield Static("🔍 Dil: —    📊 Kota: yükleniyor...", id="status-bar")
        history = ListView(id="history")
        history.border_title = "🕘 Geçmiş"
        yield history
        yield Footer()

    def on_mount(self) -> None:
        key = load_api_key()
        if key:
            self._init_translator(key)
        else:
            self.push_screen(ApiKeyScreen(), self._on_key_entered)

    def _on_key_entered(self, key: str | None) -> None:
        if key:
            save_api_key(key)
            self._init_translator(key)

    def _init_translator(self, key: str) -> None:
        try:
            self.translator = Translator(key)
        except TranslationError as exc:
            self._set_status(f"❌ {exc}")
            return
        self._refresh_usage()
        self.query_one("#source", TextArea).focus()

    # ---- Aksiyonlar ----

    def action_translate(self) -> None:
        if self.translator is None:
            self._set_status("❌ Önce API anahtarı gerekli.")
            return
        text = self.query_one("#source", TextArea).text.strip()
        if not text:
            self._set_status("ℹ️  Çevrilecek metin yok.")
            return
        self._set_status("⏳ Çevriliyor...")
        self._do_translate(text)

    @work(thread=True, exclusive=True)
    def _do_translate(self, text: str) -> None:
        assert self.translator is not None
        try:
            translated, detected = self.translator.translate(text, "TR")
        except TranslationError as exc:
            self.call_from_thread(self._set_status, f"❌ {exc}")
            return
        self.call_from_thread(self._apply_translation, text, translated, detected)

    def _apply_translation(self, source: str, translated: str, detected: str) -> None:
        self.query_one("#target", TextArea).text = translated
        self._set_status(f"✅ Dil: {detected or '—'}")
        preview_src = source.replace("\n", " ")[:28]
        preview_tgt = translated.replace("\n", " ")[:28]
        self._history.insert(0, (source, translated))
        history = self.query_one("#history", ListView)
        history.insert(0, [ListItem(Label(f"• {preview_src} ➜ {preview_tgt}"))])
        self._refresh_usage()

    def action_copy(self) -> None:
        translated = self.query_one("#target", TextArea).text.strip()
        if not translated:
            self._set_status("ℹ️  Kopyalanacak çeviri yok.")
            return
        try:
            import pyperclip

            pyperclip.copy(translated)
            self._set_status("📋 Çeviri panoya kopyalandı.")
        except Exception:
            self._set_status("⚠️  Pano erişimi yok (wl-clipboard/xclip kurulu mu?).")

    def action_clear(self) -> None:
        self.query_one("#source", TextArea).text = ""
        self.query_one("#target", TextArea).text = ""
        self._set_status("🧹 Temizlendi.")
        self.query_one("#source", TextArea).focus()

    def action_usage(self) -> None:
        self._refresh_usage()

    @work(thread=True)
    def _refresh_usage(self) -> None:
        if self.translator is None:
            return
        usage = self.translator.get_usage()
        if usage is None:
            self.call_from_thread(self._set_usage_text, "📊 Kota: bilinmiyor")
            return
        text = (
            f"📊 Kota: {usage.count:,} / {usage.limit:,} kar. "
            f"(%{usage.ratio * 100:.1f})"
        ).replace(",", ".")
        self.call_from_thread(self._set_usage_text, text)

    # ---- Yardımcılar (durum çubuğu iki bölümlü: sol mesaj | sağ kota) ----

    def _set_status(self, message: str) -> None:
        self._status_left = message
        self._render_status()

    def _set_usage_text(self, usage_text: str) -> None:
        self._status_right = usage_text
        self._render_status()

    _status_left: str = "🔍 Dil: —"
    _status_right: str = "📊 Kota: yükleniyor..."

    def _render_status(self) -> None:
        bar = self.query_one("#status-bar", Static)
        bar.update(f"{self._status_left}    {self._status_right}")


def main() -> None:
    """Giriş noktası."""
    CeviriApp().run()


if __name__ == "__main__":
    main()
