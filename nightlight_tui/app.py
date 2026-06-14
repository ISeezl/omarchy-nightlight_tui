#!/usr/bin/env python3

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive
from textual.widgets import Static, Header, Button, Input, Select

from nightlight_tui.config import (
    ASCII_MOON_LENS,
    ASCII_SUN_LENS,
    CSS_PATH,
    DEFAULT_END,
    DEFAULT_SCHEDULE,
    DEFAULT_START,
    DEFAULT_STATE,
    DEFAULT_TEMP,
    END_FILE,
    PRESET_OPTIONS,
    PRESET_TEMPS,
    SCHEDULE_FILE,
    START_FILE,
    STATE_FILE,
    TEMP_FILE,
    TEMP_STEP,
)
from nightlight_tui.storage import (
    clamp_temp,
    ensure_files,
    normalize_temp,
    read_file,
    read_temp,
    run_script,
    validate_time,
    write_file,
)


class NightLightTUI(App):
    CSS_PATH = CSS_PATH

    BINDINGS = [
        ("q", "quit", "Salir"),
        ("escape", "quit", "Salir"),
        ("ctrl+c", "quit", "Cerrar"),
        ("r", "refresh", "Refrescar"),
        ("a", "toggle_light", "Activar/apagar"),
        ("p", "toggle_schedule", "Programación"),
        ("s", "save", "Guardar"),
        ("+", "warmer_up", "Menos cálido"),
        ("-", "warmer_down", "Más cálido"),
        ("1", "apply_preset(5000)", "5000K"),
        ("2", "apply_preset(4000)", "4000K"),
        ("3", "apply_preset(3500)", "3500K"),
        ("4", "apply_preset(3000)", "3000K"),
        ("5", "apply_preset(2500)", "2500K"),
    ]

    state = reactive(DEFAULT_STATE)
    temp = reactive(str(DEFAULT_TEMP))
    schedule = reactive(DEFAULT_SCHEDULE)
    start_time = reactive(DEFAULT_START)
    end_time = reactive(DEFAULT_END)

    def __init__(self) -> None:
        super().__init__()
        self.syncing_preset = False
        self._batching_state = False

    def compose(self) -> ComposeResult:
        ensure_files()

        yield Header(show_clock=False)

        with Container(id="root"):
            yield Static("☾ Protección de vista / Luz nocturna", id="title")

            with Horizontal(id="main-layout"):
                with Vertical(id="left-panel"):
                    with Container(id="status-panel", classes="panel"):
                        yield Static("Estado actual", classes="panel-title")
                        yield Static("", id="status-display")

                    with Container(id="ascii-panel", classes="panel"):
                        yield Static("Indicador visual", classes="panel-title")
                        yield Static("", id="ascii-art", markup=False)

                with Vertical(id="right-panel"):
                    with Container(id="actions-panel", classes="panel"):
                        yield Static("Acciones", classes="panel-title")
                        yield Button("Apagado", id="toggle-button")

                    with Container(id="presets-panel", classes="panel"):
                        yield Static("Presets de intensidad", classes="panel-title")
                        yield Select(
                            PRESET_OPTIONS,
                            prompt="Selecciona intensidad",
                            allow_blank=True,
                            id="preset-select",
                        )

                    with Container(id="config-panel", classes="panel"):
                        yield Static("Configuración", classes="panel-title")

                        with Horizontal(classes="config-row"):
                            yield Static("Programación:", classes="config-label")
                            yield Button("☐", id="schedule-toggle")
                            yield Static(
                                "Apagada",
                                id="schedule-status",
                                classes="schedule-status schedule-status-off",
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Desde:", classes="config-label-small")
                            yield Input(
                                placeholder=DEFAULT_START,
                                id="start-input",
                                classes="config-input time-input",
                            )
                            yield Static(
                                "Hasta:",
                                classes="config-label-small second-label",
                            )
                            yield Input(
                                placeholder=DEFAULT_END,
                                id="end-input",
                                classes="config-input time-input",
                            )

                        yield Static("", id="message")

            yield Static(
                "A activar | P programación | S guardar | R refrescar | Q salir",
                id="help",
            )

    def on_mount(self) -> None:
        self.load_state()
        self.set_message("Listo.")

    def load_state(self) -> None:
        self._batching_state = True
        try:
            self.state = read_file(STATE_FILE, DEFAULT_STATE)
            self.temp = read_file(TEMP_FILE, str(DEFAULT_TEMP))
            self.schedule = read_file(SCHEDULE_FILE, DEFAULT_SCHEDULE)
            self.start_time = read_file(START_FILE, DEFAULT_START)
            self.end_time = read_file(END_FILE, DEFAULT_END)
        finally:
            self._batching_state = False

        if self.is_mounted:
            self.refresh_ui()

    def watch_state(self, state: str) -> None:
        self._maybe_refresh_ui()

    def watch_temp(self, temp: str) -> None:
        self._maybe_refresh_ui()

    def watch_schedule(self, schedule: str) -> None:
        self._maybe_refresh_ui()

    def watch_start_time(self, start_time: str) -> None:
        self._maybe_refresh_ui()

    def watch_end_time(self, end_time: str) -> None:
        self._maybe_refresh_ui()

    def _maybe_refresh_ui(self) -> None:
        if self._batching_state or not self.is_mounted:
            return

        self.refresh_ui()

    def refresh_ui(self) -> None:
        state_text = "Activada" if self.state == "on" else "Apagada"
        schedule_text = "Activada" if self.schedule == "on" else "Apagada"
        state_style = "green" if self.state == "on" else "red"
        schedule_style = "green" if self.schedule == "on" else "red"

        status_display = self.query_one("#status-display", Static)
        status_display.update(
            f"Protección:   [{state_style}]{state_text}[/]\n"
            f"Intensidad:   {self.temp}K\n"
            f"Programación: [{schedule_style}]{schedule_text}[/]\n"
            f"Desde:        {self.start_time}\n"
            f"Hasta:        {self.end_time}"
        )

        toggle_button = self.query_one("#toggle-button", Button)
        if self.state == "on":
            toggle_button.label = "Activado"
            toggle_button.variant = "success"
        else:
            toggle_button.label = "Apagado"
            toggle_button.variant = "error"

        schedule_button = self.query_one("#schedule-toggle", Button)
        schedule_status = self.query_one("#schedule-status", Static)

        if self.schedule == "on":
            schedule_button.label = "☑"
            schedule_button.variant = "success"
            schedule_status.update("Activa")
            schedule_status.remove_class("schedule-status-off")
            schedule_status.add_class("schedule-status-on")
        else:
            schedule_button.label = "☐"
            schedule_button.variant = "default"
            schedule_status.update("Apagada")
            schedule_status.remove_class("schedule-status-on")
            schedule_status.add_class("schedule-status-off")

        self.query_one("#start-input", Input).value = self.start_time
        self.query_one("#end-input", Input).value = self.end_time

        self.sync_preset_select()
        self.refresh_ascii_art()

    def refresh_ascii_art(self) -> None:
        ascii_art = self.query_one("#ascii-art", Static)

        if self.state == "on":
            ascii_art.update(ASCII_MOON_LENS)
            ascii_art.remove_class("off")
            ascii_art.add_class("on")
        else:
            ascii_art.update(ASCII_SUN_LENS)
            ascii_art.remove_class("on")
            ascii_art.add_class("off")

    def sync_preset_select(self) -> None:
        preset_select = self.query_one("#preset-select", Select)
        preset_values = {value for _, value in PRESET_OPTIONS}

        self.syncing_preset = True
        try:
            preset_select.value = self.temp if self.temp in preset_values else Select.BLANK
        finally:
            self.syncing_preset = False

    def set_message(self, message: str, error: bool = False) -> None:
        widget = self.query_one("#message", Static)
        widget.update(message)
        widget.styles.color = "#ff5f5f" if error else "#87ff87"

    def apply_and_refresh(self, *script_args: str, message: str | None = None) -> bool:
        if script_args and not run_script(*script_args):
            self.set_message("Error al ejecutar nightlight.sh.", True)
            return False

        self.load_state()

        if message:
            self.set_message(message)

        return True

    def save_config(self) -> bool:
        start = self.query_one("#start-input", Input).value.strip()
        end = self.query_one("#end-input", Input).value.strip()

        if not validate_time(start):
            self.set_message("Hora 'Desde' inválida. Usa HH:MM, ejemplo 20:00.", True)
            return False

        if not validate_time(end):
            self.set_message("Hora 'Hasta' inválida. Usa HH:MM, ejemplo 07:00.", True)
            return False

        write_file(START_FILE, start)
        write_file(END_FILE, end)

        return self.apply_and_refresh("apply", "schedule", message="Configuración guardada.")

    def apply_preset(self, value: int) -> None:
        write_file(TEMP_FILE, str(clamp_temp(value)))
        write_file(STATE_FILE, "on")
        self.apply_and_refresh("apply", message=f"Preset aplicado: {value}K.")

    def adjust_temp(self, delta: int) -> None:
        new_temp = clamp_temp(read_temp() + delta)
        write_file(TEMP_FILE, str(new_temp))
        write_file(STATE_FILE, "on")
        self.apply_and_refresh("apply", message=f"Intensidad ajustada: {new_temp}K.")

    def action_toggle_light(self) -> None:
        self.apply_and_refresh("toggle", message="Protección activada/apagada.")

    def action_toggle_schedule(self) -> None:
        current = read_file(SCHEDULE_FILE, DEFAULT_SCHEDULE)
        new_value = "off" if current == "on" else "on"
        write_file(SCHEDULE_FILE, new_value)

        message = "Programación activada." if new_value == "on" else "Programación apagada."
        self.apply_and_refresh("apply", "schedule", message=message)

    def action_save(self) -> None:
        self.save_config()

    def action_refresh(self) -> None:
        self.load_state()
        self.set_message("Estado actualizado.")

    def action_warmer_down(self) -> None:
        self.adjust_temp(-TEMP_STEP)

    def action_warmer_up(self) -> None:
        self.adjust_temp(TEMP_STEP)

    def action_apply_preset(self, value: int) -> None:
        if value not in PRESET_TEMPS:
            self.set_message("Preset inválido.", True)
            return

        self.apply_preset(value)

    def on_select_changed(self, event: Select.Changed) -> None:
        if self.syncing_preset or event.select.id != "preset-select":
            return

        if event.value == Select.BLANK:
            return

        temp = normalize_temp(str(event.value))
        if temp is None:
            self.set_message("Preset inválido.", True)
            return

        self.apply_preset(temp)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "toggle-button":
            self.action_toggle_light()
        elif event.button.id == "schedule-toggle":
            self.action_toggle_schedule()


def main() -> None:
    NightLightTUI().run()


if __name__ == "__main__":
    main()
