"""DTR — DeepL ile anlık çeviri için klavye odaklı Textual arayüzü."""

from __future__ import annotations

import threading

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.timer import Timer
from textual.widgets import Button, Input, Label, Static, TextArea, Select

from .config import load_api_key, load_theme, save_api_key, save_theme, load_languages, save_languages
from .theme import build_themes
from .translator import Translator, TranslationError, UsageInfo

DEBOUNCE_SECONDS = 0.35

DARK_THEME, LIGHT_THEME = build_themes()

DEFAULT_THEME = DARK_THEME.name


class ApiKeyScreen(ModalScreen[str]):
    """API anahtarı eksikse gösterilen sade ilk kurulum ekranı."""

    BINDINGS = [Binding("escape", "quit_app", "Çık", priority=True)]

    def compose(self) -> ComposeResult:
        with Vertical(id="apikey-dialog"):
            yield Static("DEEPL ERİŞİMİ", id="apikey-kicker")
            yield Label("API anahtarını ekle", id="apikey-title")
            yield Label(
                "Anahtar yalnız bu bilgisayardaki .env dosyasına kaydedilir.",
                id="apikey-copy",
            )
            yield Input(
                placeholder="DeepL API anahtarı",
                password=True,
                id="apikey-input",
            )
            with Horizontal(id="apikey-buttons"):
                yield Button("KAYDET", id="save", flat=True)
                yield Button("ÇIKIŞ", id="quit", flat=True)

    def on_mount(self) -> None:
        self.query_one("#apikey-input", Input).focus()

    @on(Button.Pressed, "#save")
    @on(Input.Submitted, "#apikey-input")
    def _save(self) -> None:
        key = self.query_one("#apikey-input", Input).value.strip()
        if key:
            self.dismiss(key)

    @on(Button.Pressed, "#quit")
    def action_quit_app(self) -> None:
        self.app.exit()


class CeviriApp(App):
    """DTR ana uygulaması."""

    CSS_PATH = "styles.tcss"
    TITLE = "DTR — Anlık Çeviri"

    BINDINGS = [
        Binding("ctrl+j", "translate", "Çevir", priority=True),
        Binding("f3", "translate_to_turkish", "AUTO → TR", priority=True),
        Binding("ctrl+e", "translate_to_english", "TR → EN", priority=True),
        Binding("f4", "translate_to_english", "TR → EN", priority=True),
        Binding("ctrl+y", "copy", "Kopyala", priority=True),
        Binding("ctrl+g", "paste", "Yapıştır", priority=True),
        Binding("ctrl+l", "clear", "Temizle", priority=True),
        Binding("f2", "toggle_theme", "Tema", priority=True),
        Binding("ctrl+q", "quit", "Çıkış", priority=True),
    ]

    def __init__(self, translator: Translator | None = None) -> None:
        super().__init__()
        self.translator = translator
        self._debounce_timer: Timer | None = None
        self._last_translated = ""
        self._source_lang_override, self._target_lang = load_languages()
        self._source_languages = {"TR": "Türkçe", "EN": "İngilizce"}
        self._target_languages = {"TR": "Türkçe", "EN": "İngilizce (ABD)"}
        if self._source_lang_override:
            self._source_languages.setdefault(self._source_lang_override, self._source_lang_override)
        self._target_languages.setdefault(self._target_lang, self._target_lang)
        self._translation_generation = 0
        self._usage_pending = False
        self._status_left = "Başlatılıyor…"
        self._status_right = "KOTA —"

    def compose(self) -> ComposeResult:
        with Vertical(id="shell"):
            with Horizontal(id="topbar"):
                with Vertical(id="identity"):
                    yield Static("DTR", id="brand")
                    yield Static("DEEPL · ANLIK ÇEVİRİ", id="descriptor")
                yield Static("API", id="api-state")

            with Vertical(id="workspace"):
                with Vertical(classes="pane", id="source-pane"):
                    with Horizontal(classes="pane-head"):
                        yield Static("01 / KAYNAK", classes="pane-title")
                        yield Static("OTOMATİK ALGILAMA", id="source-language")
                        yield Static("0 KARAKTER", id="source-count", classes="count")
                    yield TextArea(
                        id="source",
                        language=None,
                        placeholder="Çevrilecek metni yazın veya Ctrl+G ile yapıştırın…",
                    )

                with Horizontal(id="language-selectors"):
                    yield Select(
                        [("Otomatik algıla", "AUTO")] + self._language_options(self._source_languages),
                        value=self._source_lang_override or "AUTO",
                        allow_blank=False, id="source-select",
                    )
                    yield Select(
                        self._language_options(self._target_languages),
                        value=self._target_lang,
                        allow_blank=False, id="target-select",
                    )

                with Horizontal(id="direction-rail"):
                    yield Static("YÖN", id="direction-label")
                    yield Button("AUTO → TR", id="mode-tr", classes="mode", flat=True)
                    yield Button("TR → EN", id="mode-en", classes="mode", flat=True)
                    yield Static("F3 / F4", id="mode-hint")

                with Vertical(classes="pane", id="target-pane"):
                    with Horizontal(classes="pane-head"):
                        yield Static("02 / SONUÇ", classes="pane-title")
                        yield Static("TÜRKÇE", id="target-language")
                        yield Static("0 KARAKTER", id="target-count", classes="count")
                    yield TextArea(
                        id="target",
                        read_only=True,
                        show_cursor=False,
                        highlight_cursor_line=False,
                        language=None,
                        placeholder="Çeviri burada görünecek.",
                    )

            with Horizontal(id="statusbar"):
                yield Static("", id="status")
                yield Static("", id="usage")
            yield Static(
                "F2 TEMA   F3/F4 YÖN   ^Y KOPYALA   ^L TEMİZLE   ^Q ÇIKIŞ",
                id="keymap",
            )

    def on_mount(self) -> None:
        self.register_theme(DARK_THEME)
        self.register_theme(LIGHT_THEME)
        saved_theme = load_theme()
        self.theme = (
            saved_theme
            if saved_theme in {DARK_THEME.name, LIGHT_THEME.name}
            else DEFAULT_THEME
        )
        self._update_mode_ui()
        self.query_one("#source", TextArea).focus()

        if self.translator is not None:
            self._translator_ready()
            return

        key = load_api_key()
        if key:
            self._init_translator(key)
        else:
            self._api_missing()
            self.push_screen(ApiKeyScreen(), self._on_key_entered)

    def on_unmount(self) -> None:
        if self._debounce_timer is not None:
            self._debounce_timer.stop()

    def _on_key_entered(self, key: str | None) -> None:
        if key:
            save_api_key(key)
            self._init_translator(key)

    def _init_translator(self, key: str) -> None:
        try:
            self.translator = Translator(key)
        except TranslationError as exc:
            self._api_missing()
            self._set_status(str(exc), error=True)
            return
        self._translator_ready()

    def _translator_ready(self) -> None:
        state = self.query_one("#api-state", Static)
        state.update("API HAZIR")
        state.remove_class("error")
        state.add_class("ready")
        self._set_status("Hazır · yazdıkça çevrilir")
        self._refresh_usage()
        threading.Thread(target=self._load_languages, name="dtr-languages", daemon=True).start()
        self.query_one("#source", TextArea).focus()

    def _api_missing(self) -> None:
        state = self.query_one("#api-state", Static)
        state.update("API EKSİK")
        state.remove_class("ready")
        state.add_class("error")
        self._set_status("DeepL API anahtarı gerekli", error=True)

    def _update_mode_ui(self) -> None:
        tr_mode = self._target_lang == "TR" and self._source_lang_override is None
        en_mode = self._target_lang == "EN" and self._source_lang_override == "TR"
        self.query_one("#mode-tr", Button).set_class(tr_mode, "active")
        self.query_one("#mode-en", Button).set_class(en_mode, "active")
        source = self._source_languages.get(self._source_lang_override, "Otomatik algılama")
        target = self._target_languages.get(self._target_lang, self._target_lang)
        self.query_one("#source-language", Static).update(source)
        self.query_one("#target-language", Static).update(target)
        for selector, value in [
            ("#source-select", self._source_lang_override or "AUTO"),
            ("#target-select", self._target_lang),
        ]:
            widget = self.query_one(selector, Select)
            with widget.prevent(Select.Changed):
                widget.value = value

    @staticmethod
    def _language_options(languages: dict[str, str]) -> list[tuple[str, str]]:
        return [(f"{name} · {code}", code) for code, name in sorted(
            languages.items(), key=lambda item: item[1].casefold()
        )]

    def _load_languages(self) -> None:
        assert self.translator is not None
        try:
            sources, targets = self.translator.get_languages()
            self.call_from_thread(self._apply_languages, sources, targets)
        except Exception:
            try:
                self.call_from_thread(
                    self._set_status,
                    "Dil listesi alınamadı · yeniden açarak tekrar deneyin", True,
                )
            except RuntimeError:
                pass

    def _apply_languages(self, sources: dict[str, str], targets: dict[str, str]) -> None:
        # Eski EN kısayolu API sınırında EN-US olarak gönderilmeye devam eder.
        targets = dict(targets)
        if "EN-US" in targets:
            targets["EN"] = "İngilizce (ABD)"
        self._source_languages = dict(sources)
        self._target_languages = targets
        source = self._source_lang_override if self._source_lang_override in sources else None
        target = self._target_lang if self._target_lang in targets else (
            "TR" if "TR" in targets else next(iter(targets))
        )
        for selector, options, value in [
            ("#source-select", [("Otomatik algıla", "AUTO")] + self._language_options(sources), source or "AUTO"),
            ("#target-select", self._language_options(targets), target),
        ]:
            widget = self.query_one(selector, Select)
            with widget.prevent(Select.Changed):
                widget.set_options(options)
                widget.value = value
        if (source, target) != (self._source_lang_override, self._target_lang):
            self._set_translation_mode(target, source)
        else:
            self._update_mode_ui()

    @on(Select.Changed, "#source-select")
    @on(Select.Changed, "#target-select")
    def _language_changed(self, event: Select.Changed) -> None:
        if event.value is Select.BLANK:
            return
        source = self.query_one("#source-select", Select).value
        target = self.query_one("#target-select", Select).value
        if isinstance(source, str) and isinstance(target, str):
            self._set_translation_mode(target, None if source == "AUTO" else source)

    def _set_translation_mode(self, target_lang: str, source_lang: str | None) -> None:
        if (target_lang, source_lang) == (self._target_lang, self._source_lang_override):
            return
        if self._debounce_timer is not None:
            self._debounce_timer.stop()
        self._translation_generation += 1
        self._target_lang = target_lang
        self._source_lang_override = source_lang
        self._last_translated = ""
        self._update_mode_ui()
        saved = save_languages(source_lang, target_lang)
        self._set_status(f"Yön: {source_lang or 'AUTO'} → {target_lang}")
        if self.query_one("#source", TextArea).text.strip():
            self.action_translate()
        if not saved:
            self.notify("Dil tercihi kaydedilemedi.", severity="warning")

    @on(TextArea.Changed, "#source")
    def _on_source_changed(self) -> None:
        text = self.query_one("#source", TextArea).text
        self.query_one("#source-count", Static).update(f"{len(text):,} KARAKTER")
        if self._debounce_timer is not None:
            self._debounce_timer.stop()
        self._debounce_timer = self.set_timer(
            DEBOUNCE_SECONDS,
            self.action_translate,
            name="translate-debounce",
        )

    def action_translate(self) -> None:
        if self.translator is None:
            self._set_status("DeepL API anahtarı gerekli", error=True)
            return
        text = self.query_one("#source", TextArea).text.strip()
        if not text:
            self.query_one("#target", TextArea).text = ""
            self.query_one("#target-count", Static).update("0 KARAKTER")
            self._set_status("Metin bekleniyor")
            return
        if text == self._last_translated:
            return
        self._translation_generation += 1
        self._set_status("Çevriliyor…")
        threading.Thread(
            target=self._do_translate,
            args=(
                text,
                self._target_lang,
                self._source_lang_override,
                self._translation_generation,
            ),
            name="dtr-translate",
            daemon=True,
        ).start()

    def _do_translate(
        self,
        text: str,
        target_lang: str,
        source_lang: str | None,
        generation: int,
    ) -> None:
        assert self.translator is not None
        try:
            translated, detected = self.translator.translate(
                text,
                target_lang=target_lang,
                source_lang=source_lang,
            )
        except TranslationError as exc:
            try:
                self.call_from_thread(self._translation_failed, str(exc), generation)
            except RuntimeError:
                pass
            return
        try:
            self.call_from_thread(
                self._apply_translation,
                text,
                translated,
                detected,
                target_lang,
                generation,
            )
        except RuntimeError:
            pass

    def _translation_failed(self, message: str, generation: int) -> None:
        if generation == self._translation_generation:
            self._set_status(message, True)

    def _apply_translation(
        self,
        source: str,
        translated: str,
        detected: str,
        target_lang: str,
        generation: int,
    ) -> None:
        if generation != self._translation_generation:
            return
        self._last_translated = source
        target = self.query_one("#target", TextArea)
        target.text = translated
        target.refresh(repaint=True, layout=True)
        self.query_one("#target-count", Static).update(
            f"{len(translated):,} KARAKTER"
        )
        self._set_status(f"{detected or '?'} → {target_lang} · tamamlandı")
        self._refresh_usage()

    def action_translate_to_turkish(self) -> None:
        self._set_translation_mode("TR", None)

    def action_translate_to_english(self) -> None:
        if self._debounce_timer is not None:
            self._debounce_timer.stop()
        self._set_translation_mode("EN", "TR")

    @on(Button.Pressed, "#mode-tr")
    def _select_turkish_mode(self) -> None:
        self.action_translate_to_turkish()

    @on(Button.Pressed, "#mode-en")
    def _select_english_mode(self) -> None:
        self.action_translate_to_english()

    def action_copy(self) -> None:
        translated = self.query_one("#target", TextArea).text.strip()
        if not translated:
            self._set_status("Kopyalanacak çeviri yok", error=True)
            return
        try:
            import pyperclip

            pyperclip.copy(translated)
        except Exception:
            self._set_status("Panoya erişilemedi · wl-clipboard kurulumunu kontrol et", True)
            return
        self._set_status("Çeviri panoya kopyalandı")

    def action_paste(self) -> None:
        try:
            import pyperclip

            text = pyperclip.paste()
        except Exception:
            self._set_status("Panoya erişilemedi · wl-clipboard kurulumunu kontrol et", True)
            return
        if not text.strip():
            self._set_status("Pano boş", error=True)
            return
        self.query_one("#source", TextArea).text = text
        self._last_translated = ""
        self.action_translate()

    def action_clear(self) -> None:
        self._translation_generation += 1
        if self._debounce_timer is not None:
            self._debounce_timer.stop()
        self.query_one("#source", TextArea).text = ""
        self.query_one("#target", TextArea).text = ""
        self.query_one("#source-count", Static).update("0 KARAKTER")
        self.query_one("#target-count", Static).update("0 KARAKTER")
        self._last_translated = ""
        self._set_status("Temizlendi · metin bekleniyor")
        self.query_one("#source", TextArea).focus()

    def _refresh_usage(self) -> None:
        if self.translator is None or self._usage_pending:
            return
        self._usage_pending = True
        threading.Thread(
            target=self._load_usage,
            name="dtr-usage",
            daemon=True,
        ).start()

    def _load_usage(self) -> None:
        assert self.translator is not None
        usage = self.translator.get_usage()
        try:
            self.call_from_thread(self._finish_usage, usage)
        except RuntimeError:
            self._usage_pending = False

    def _finish_usage(self, usage: UsageInfo | None) -> None:
        self._usage_pending = False
        self._set_usage(usage)

    def _set_usage(self, usage: UsageInfo | None) -> None:
        if usage is None:
            self._status_right = "KOTA —"
        else:
            self._status_right = (
                f"KOTA {usage.count:,} / {usage.limit:,} · %{usage.ratio * 100:.1f}"
            ).replace(",", ".")
        self._render_status()

    def _set_status(self, message: str, error: bool = False) -> None:
        self._status_left = message
        status = self.query_one("#status", Static)
        status.set_class(error, "error")
        self._render_status()

    def _render_status(self) -> None:
        self.query_one("#status", Static).update(self._status_left)
        self.query_one("#usage", Static).update(self._status_right)

    def action_toggle_theme(self) -> None:
        new_theme = (
            LIGHT_THEME.name if self.theme == DARK_THEME.name else DARK_THEME.name
        )
        self.theme = new_theme
        save_theme(new_theme)
        label = "açık" if new_theme == LIGHT_THEME.name else "koyu"
        self._set_status(f"Tema: {label}")


def main() -> None:
    CeviriApp().run()


if __name__ == "__main__":
    main()
