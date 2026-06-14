#!/usr/bin/env python3

from pathlib import Path
import subprocess
import re

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, DataTable, Footer, Header, Button, Input, Select
from textual.reactive import reactive


HOME = Path.home()

SCRIPT = HOME / ".config/waybar/scripts/nightlight.sh"
BASE_DIR = HOME / ".config/waybar/nightlight"

STATE_FILE = BASE_DIR / "state"
TEMP_FILE = BASE_DIR / "temp"
SCHEDULE_FILE = BASE_DIR / "schedule_enabled"
START_FILE = BASE_DIR / "start"
END_FILE = BASE_DIR / "end"


PRESET_OPTIONS = [
    ("5000K - Suave", "5000"),
    ("4000K - Normal de noche", "4000"),
    ("3500K - Cálido", "3500"),
    ("3000K - Muy naranja", "3000"),
    ("2500K - Extremo", "2500"),
]


def ensure_files() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    defaults = {
        STATE_FILE: "off",
        TEMP_FILE: "4000",
        SCHEDULE_FILE: "off",
        START_FILE: "20:00",
        END_FILE: "07:00",
    }

    for path, value in defaults.items():
        if not path.exists():
            path.write_text(value)


def read_file(path: Path, default: str) -> str:
    try:
        return path.read_text().strip()
    except FileNotFoundError:
        return default


def write_file(path: Path, value: str) -> None:
    path.write_text(str(value).strip())


def run_script(*args: str) -> None:
    subprocess.run([str(SCRIPT), *args], check=False)


def validate_time(value: str) -> bool:
    if not re.match(r"^\d{2}:\d{2}$", value):
        return False

    hour, minute = value.split(":")
    h = int(hour)
    m = int(minute)

    return 0 <= h <= 23 and 0 <= m <= 59


def normalize_temp(value: str) -> int | None:
    if not value.isdigit():
        return None

    temp = int(value)

    if temp < 2500:
        temp = 2500

    if temp > 6500:
        temp = 6500

    return temp


class NightLightTUI(App):
    CSS = """
    Screen {
        background: #0b0b0f;
    }

    #root {
        height: 100%;
        width: 100%;
        padding: 1 2;
    }

    #title {
        height: 3;
        content-align: center middle;
        text-style: bold;
        color: #ffafd7;
        border: round #8a5cf6;
        margin-bottom: 1;
    }

    .panel {
        border: round #c0c0c0;
        padding: 0 1;
        margin-bottom: 0;
    }

    .panel-title {
        color: #ffd787;
        text-style: bold;
        margin-bottom: 0;
    }

    #main-layout {
        height: auto;
        margin-top: 0;
        margin-bottom: 0;
    }

    #left-panel {
        width: 48%;
        height: auto;
        margin-right: 1;
    }

    #right-panel {
        width: 52%;
        height: auto;
    }

    #status-panel {
        height: auto;
        margin-top: 0;
        margin-bottom: 0;
    }

    #status-table {
        height: auto;
    }

    #actions-panel {
        height: 5;
        width: 100%;
        margin-top: 0;
        margin-bottom: 0;
    }

    #presets-panel {
        height: 6;
        width: 100%;
        margin-top: 0;
        margin-bottom: 0;
    }

    #preset-select {
        width: 100%;
        height: 3;
        min-height: 3;
        max-height: 3;
        margin-top: 0;
        margin-bottom: 0;
        background: #16161d;
        color: #d0d0d0;
        border: none;
    }

    #preset-select:focus {
        background: #242433;
        border: none;
    }

    #config-panel {
        height: auto;
        width: 100%;
        margin-top: 0;
        margin-bottom: 0;
    }

    .config-row {
        height: 1;
        min-height: 1;
        max-height: 1;
        margin-bottom: 1;
        align: left middle;
    }

    .config-label {
        width: 14;
        height: 1;
        content-align: left middle;
        color: #d0d0d0;
    }

    .config-label-small {
        width: 6;
        height: 1;
        content-align: left middle;
        color: #d0d0d0;
    }

    .second-label {
        margin-left: 2;
    }

    .config-input {
        height: 1;
        min-height: 1;
        max-height: 1;
        border: none;
        padding-left: 1;
        padding-right: 0;
        margin: 0 1;
        background: #16161d;
    }

    .config-input:focus {
        border: none;
        background: #242433;
    }

    .time-input {
        width: 8;
        min-width: 8;
        max-width: 8;
    }

    #schedule-toggle {
        width: 3;
        min-width: 3;
        max-width: 3;
        height: 1;
        min-height: 1;
        max-height: 1;
        margin: 0;
        padding: 0;
    }

    .schedule-status {
        width: 10;
        height: 1;
        content-align: left middle;
        margin-left: 1;
    }

    .schedule-status-on {
        color: #87ff87;
        text-style: bold;
    }

    .schedule-status-off {
        color: #ff5f5f;
        text-style: bold;
    }

    #toggle-button {
        width: 100%;
        min-width: 0;
        height: 1;
        min-height: 1;
        max-height: 1;
        margin: 0;
        padding: 0 1;
    }

    DataTable {
        height: auto;
    }

    Button {
        min-width: 14;
        margin-right: 1;
        margin-bottom: 0;
    }

    #message {
        height: 3;
        color: #87ff87;
        border: round #444444;
        padding: 0 1;
        content-align: left middle;
        margin-top: 1;
    }

    #help {
        height: 3;
        color: #a0a0a0;
        content-align: center middle;
        border: round #444444;
        margin-top: 0;
        margin-bottom: 0;
    }
    """

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
        ("1", "preset_5000", "5000K"),
        ("2", "preset_4000", "4000K"),
        ("3", "preset_3500", "3500K"),
        ("4", "preset_3000", "3000K"),
        ("5", "preset_2500", "2500K"),
    ]

    state = reactive("off")
    temp = reactive("4000")
    schedule = reactive("off")
    start_time = reactive("20:00")
    end_time = reactive("07:00")

    def __init__(self) -> None:
        super().__init__()
        self.syncing_preset = False

    def compose(self) -> ComposeResult:
        ensure_files()

        yield Header(show_clock=False)

        with Container(id="root"):
            yield Static("☾ Protección de vista / Luz nocturna", id="title")

            with Horizontal(id="main-layout"):
                with Vertical(id="left-panel"):
                    with Container(id="status-panel", classes="panel"):
                        yield Static("Estado actual", classes="panel-title")
                        yield DataTable(id="status-table")

                with Vertical(id="right-panel"):
                    with Container(id="actions-panel", classes="panel"):
                        yield Static("Acciones", classes="panel-title")
                        yield Button(
                            "Apagado",
                            id="toggle-button",
                        )

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
                                placeholder="20:00",
                                id="start-input",
                                classes="config-input time-input",
                            )

                            yield Static(
                                "Hasta:",
                                classes="config-label-small second-label",
                            )
                            yield Input(
                                placeholder="07:00",
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
        self.setup_tables()
        self.refresh_ui()
        self.set_message("Listo.")

    def load_state(self) -> None:
        self.state = read_file(STATE_FILE, "off")
        self.temp = read_file(TEMP_FILE, "4000")
        self.schedule = read_file(SCHEDULE_FILE, "off")
        self.start_time = read_file(START_FILE, "20:00")
        self.end_time = read_file(END_FILE, "07:00")

    def setup_tables(self) -> None:
        status_table = self.query_one("#status-table", DataTable)
        status_table.clear(columns=True)
        status_table.add_columns("Campo", "Valor")

    def refresh_ui(self) -> None:
        status_table = self.query_one("#status-table", DataTable)
        status_table.clear()

        state_text = "Activada" if self.state == "on" else "Apagada"
        schedule_text = "Activada" if self.schedule == "on" else "Apagada"

        status_table.add_row("Protección", state_text)
        status_table.add_row("Intensidad", f"{self.temp}K")
        status_table.add_row("Programación", schedule_text)
        status_table.add_row("Desde", self.start_time)
        status_table.add_row("Hasta", self.end_time)

        toggle_button = self.query_one("#toggle-button", Button)
        schedule_button = self.query_one("#schedule-toggle", Button)
        schedule_status = self.query_one("#schedule-status", Static)

        if self.state == "on":
            toggle_button.label = "Activado"
            toggle_button.variant = "success"
        else:
            toggle_button.label = "Apagado"
            toggle_button.variant = "error"

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

    def sync_preset_select(self) -> None:
        preset_select = self.query_one("#preset-select", Select)

        self.syncing_preset = True

        try:
            preset_values = {value for _, value in PRESET_OPTIONS}

            if self.temp in preset_values:
                preset_select.value = self.temp
            else:
                preset_select.value = Select.BLANK
        finally:
            self.syncing_preset = False

    def set_message(self, message: str, error: bool = False) -> None:
        widget = self.query_one("#message", Static)
        widget.update(message)
        widget.styles.color = "#ff5f5f" if error else "#87ff87"

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

        run_script("apply")

        self.load_state()
        self.refresh_ui()
        self.set_message("Configuración guardada.")
        return True

    def apply_preset(self, value: int) -> None:
        write_file(TEMP_FILE, str(value))
        write_file(STATE_FILE, "on")
        run_script("apply")

        self.load_state()
        self.refresh_ui()
        self.set_message(f"Preset aplicado: {value}K.")

    def adjust_temp(self, delta: int) -> None:
        current = normalize_temp(read_file(TEMP_FILE, "4000"))

        if current is None:
            current = 4000

        new_temp = current + delta

        if new_temp < 2500:
            new_temp = 2500

        if new_temp > 6500:
            new_temp = 6500

        write_file(TEMP_FILE, str(new_temp))
        write_file(STATE_FILE, "on")
        run_script("apply")

        self.load_state()
        self.refresh_ui()
        self.set_message(f"Intensidad ajustada: {new_temp}K.")

    def action_toggle_light(self) -> None:
        run_script("toggle")
        self.load_state()
        self.refresh_ui()
        self.set_message("Protección activada/apagada.")

    def action_toggle_schedule(self) -> None:
        current = read_file(SCHEDULE_FILE, "off")

        if current == "on":
            write_file(SCHEDULE_FILE, "off")
            self.set_message("Programación apagada.")
        else:
            write_file(SCHEDULE_FILE, "on")
            self.set_message("Programación activada.")

        run_script("apply")
        self.load_state()
        self.refresh_ui()

    def action_save(self) -> None:
        self.save_config()

    def action_refresh(self) -> None:
        self.load_state()
        self.refresh_ui()
        self.set_message("Estado actualizado.")

    def action_warmer_down(self) -> None:
        self.adjust_temp(-250)

    def action_warmer_up(self) -> None:
        self.adjust_temp(250)

    def action_preset_5000(self) -> None:
        self.apply_preset(5000)

    def action_preset_4000(self) -> None:
        self.apply_preset(4000)

    def action_preset_3500(self) -> None:
        self.apply_preset(3500)

    def action_preset_3000(self) -> None:
        self.apply_preset(3000)

    def action_preset_2500(self) -> None:
        self.apply_preset(2500)

    def on_select_changed(self, event: Select.Changed) -> None:
        if self.syncing_preset:
            return

        if event.select.id != "preset-select":
            return

        if event.value == Select.BLANK:
            return

        temp = normalize_temp(str(event.value))

        if temp is None:
            self.set_message("Preset inválido.", True)
            return

        self.apply_preset(temp)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "toggle-button":
            self.action_toggle_light()
        elif button_id == "schedule-toggle":
            self.action_toggle_schedule()


def main() -> None:
    NightLightTUI().run()


if __name__ == "__main__":
    main()