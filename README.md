# Waybar Hyprsunset TUI

A terminal user interface for controlling night light / blue light filtering on **Hyprland / Omarchy** using **hyprsunset**.

The app is built with **Python + Textual** and is designed to work nicely with **Waybar**.

It allows you to:

* Turn night light on or off.
* Change color temperature presets.
* Configure a start and end time.
* Save settings into simple configuration files.
* Control everything from a clean terminal UI.

---

## Interface Layout

The interface is organized into simple panels:

```text
Current Status | Actions
Visual Indicator | Temperature Presets
               | Configuration
```

Main sections:

* **Current Status**: shows whether night light is enabled, current temperature, schedule status, start time, and end time.
* **Visual Indicator**: ASCII sun/moon with lenses that reflects the current state.
* **Actions**: button to enable or disable night light.
* **Temperature Presets**: dropdown with predefined temperature values.
* **Configuration**: schedule toggle and time inputs.

---

## Requirements

This project is intended for Arch-based Linux systems, especially:

* Arch Linux
* Omarchy
* Hyprland
* Waybar

Required packages:

* Python 3.11+
* pipx
* hyprsunset
* Waybar
* Hyprland

Install dependencies on Arch Linux:

```bash
sudo pacman -S python python-pipx hyprsunset
```

---

## Install hyprsunset

On Arch Linux:

```bash
sudo pacman -S hyprsunset
```

Check that it is available:

```bash
hyprsunset --help
```

You can also test if Hyprland recognizes the hyprsunset command:

```bash
hyprctl hyprsunset identity
```

If this command fails, make sure `hyprsunset` is installed and running.

---

## Start hyprsunset with Hyprland

Edit your Hyprland configuration file.

It is usually located at:

```bash
~/.config/hypr/hyprland.conf
```

Add this line:

```ini
exec-once = hyprsunset
```

Then restart your Hyprland session.

---

## Installation

Install directly from GitHub with `pipx`:

```bash
pipx install "git+https://github.com/ISeezl/omarchy-nightlight_tui.git"
```

If you already installed an older version, remove it first and install again:

```bash
pipx uninstall waybar-hyprsunset-tui
pipx install "git+https://github.com/ISeezl/omarchy-nightlight_tui.git"
```

Install configuration files, the control script, and the schedule timer:

```bash
nightlight-tui-install
```

Run the app:

```bash
nightlight-tui
```

---

## Local Installation

Clone the repository:

```bash
git clone https://github.com/ISeezl/omarchy-nightlight_tui.git
cd omarchy-nightlight_tui
```

Run the installer:

```bash
./install.sh
```

---

## Development Installation

Clone the repository:

```bash
git clone https://github.com/ISeezl/omarchy-nightlight_tui.git
cd omarchy-nightlight_tui
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode:

```bash
pip install -e .
```

Run the installer:

```bash
./install.sh
nightlight-tui-install
```

Run the app:

```bash
nightlight-tui
```

Or run it directly with Python:

```bash
python -m nightlight_tui
```

---

## Project Structure

```text
waybar-hyprsunset-tui/
├── nightlight_tui/
│   ├── __init__.py
│   ├── __main__.py
│   ├── app.py
│   ├── config.py
│   ├── storage.py
│   ├── install_cmd.py
│   ├── styles.tcss
│   └── assets/
│       ├── nightlight.sh
│       ├── nightlight-schedule.service
│       └── nightlight-schedule.timer
├── scripts/
│   └── nightlight.sh
├── install.sh
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

File descriptions:

```text
nightlight_tui/app.py          Textual TUI application.
nightlight_tui/config.py       Shared paths, presets, and constants.
nightlight_tui/storage.py      File I/O, validation, and script runner.
nightlight_tui/install_cmd.py  Installs scripts, config, and systemd timer.
nightlight_tui/styles.tcss     TUI stylesheet.
scripts/nightlight.sh          Control script that talks to hyprsunset.
install.sh                     Dependency checker and bootstrap installer.
pyproject.toml                 Python package configuration.
README.md                      Project documentation.
```

---

## Configuration Files

The app uses this directory:

```bash
~/.config/waybar/nightlight
```

The following files are created automatically:

```text
~/.config/waybar/nightlight/state
~/.config/waybar/nightlight/temp
~/.config/waybar/nightlight/schedule_enabled
~/.config/waybar/nightlight/start
~/.config/waybar/nightlight/end
~/.config/waybar/nightlight/constants.env
```

Default values:

```text
state=off
temp=4000
schedule_enabled=off
start=20:00
end=07:00
```

Shared temperature limits used by both the TUI and `nightlight.sh`:

```text
MIN_TEMP=2500
MAX_TEMP=6500
DEFAULT_TEMP=4000
OFF_TEMP=6000
TEMP_STEP=250
```

---

## Control Script

The TUI runs this script:

```bash
~/.config/waybar/scripts/nightlight.sh
```

This script is responsible for applying the color temperature using `hyprsunset`.

Expected usage:

```bash
~/.config/waybar/scripts/nightlight.sh toggle
```

This toggles night light on or off.

```bash
~/.config/waybar/scripts/nightlight.sh apply
```

This applies the current saved state.

```bash
~/.config/waybar/scripts/nightlight.sh schedule
```

This evaluates the saved schedule and turns night light on or off when needed.

```bash
~/.config/waybar/scripts/nightlight.sh open-tui
```

This opens the TUI from Waybar or another launcher.

---

## Automatic Schedule

When schedule is enabled in the TUI, a user systemd timer checks the saved start/end times every minute and applies the correct state.

Install or refresh the timer with:

```bash
nightlight-tui-install
```

Check timer status:

```bash
systemctl --user status nightlight-schedule.timer
```

Run a schedule check manually:

```bash
~/.config/waybar/scripts/nightlight.sh schedule
```

Overnight ranges such as `20:00` to `07:00` are supported.

---

## Temperature Presets

The app includes these default presets:

```text
5000K - Soft
4000K - Normal night mode
3500K - Warm
3000K - Very warm
2500K - Extreme
```

Lower values make the screen warmer and more orange.

---

## Keyboard Shortcuts

Inside the TUI:

```text
A       Toggle night light
P       Toggle schedule
S       Save configuration
R       Refresh state
Q       Quit
Esc     Quit
Ctrl+C  Quit
```

Preset shortcuts:

```text
1       5000K
2       4000K
3       3500K
4       3000K
5       2500K
```

---

## Waybar Integration

You can add a custom Waybar module to open the TUI.

Example:

```json
"custom/nightlight": {
  "format": "󰖔",
  "tooltip": true,
  "on-click": "kitty -e nightlight-tui"
}
```

If you use another terminal, replace `kitty`.

For Alacritty:

```json
"on-click": "alacritty -e nightlight-tui"
```

For Foot:

```json
"on-click": "foot -e nightlight-tui"
```

Then add the module to your Waybar modules list:

```json
"modules-right": [
  "custom/nightlight",
  "pulseaudio",
  "network",
  "clock"
]
```

Restart Waybar:

```bash
pkill waybar
waybar &
```

---

## Useful Commands

Run the TUI:

```bash
nightlight-tui
```

Apply the current saved state:

```bash
~/.config/waybar/scripts/nightlight.sh apply
```

Toggle night light manually:

```bash
~/.config/waybar/scripts/nightlight.sh toggle
```

Check current state:

```bash
cat ~/.config/waybar/nightlight/state
```

Check current temperature:

```bash
cat ~/.config/waybar/nightlight/temp
```

Change temperature manually:

```bash
echo 3500 > ~/.config/waybar/nightlight/temp
~/.config/waybar/scripts/nightlight.sh apply
```

---

## Troubleshooting

### `nightlight-tui` command was not found

Check if the app was installed with `pipx`:

```bash
pipx list
```

If it is missing, install it again:

```bash
pipx install .
```

Make sure `pipx` is available in your PATH:

```bash
pipx ensurepath
```

Then close and reopen your terminal.

---

### `hyprctl hyprsunset` does not work

Check if `hyprsunset` is installed:

```bash
pacman -Qs hyprsunset
```

Install it if needed:

```bash
sudo pacman -S hyprsunset
```

Make sure it starts with Hyprland:

```ini
exec-once = hyprsunset
```

Then restart your Hyprland session.

---

### The TUI opens, but the screen temperature does not change

Check that the control script exists:

```bash
ls -l ~/.config/waybar/scripts/nightlight.sh
```

Make sure it is executable:

```bash
chmod +x ~/.config/waybar/scripts/nightlight.sh
```

Test it manually:

```bash
~/.config/waybar/scripts/nightlight.sh toggle
```

---

### The preset changes, but the temperature is not applied

Check the saved temperature:

```bash
cat ~/.config/waybar/nightlight/temp
```

Apply it manually:

```bash
~/.config/waybar/scripts/nightlight.sh apply
```

---

### Schedule does not apply automatically

Make sure the timer is installed and active:

```bash
nightlight-tui-install
systemctl --user status nightlight-schedule.timer
```

You can also run a manual check:

```bash
~/.config/waybar/scripts/nightlight.sh schedule
```

Make sure schedule is enabled in the TUI and the start/end times are valid.

---

## Security Notes

This project does not require `sudo` to copy files into your personal configuration directory.

The installer only creates or modifies files inside:

```bash
~/.config/waybar/
```

However, the installer may ask for confirmation before installing missing system dependencies with `pacman`.

You can review the installer before running it:

```bash
cat install.sh
```

Avoid installing projects using commands like:

```bash
curl ... | bash
```

Clone the repository, inspect the files, and then run the installer manually.

---

## Uninstallation

Remove the Python app installed with `pipx`:

```bash
pipx uninstall waybar-hyprsunset-tui
```

Remove configuration files and timer:

```bash
systemctl --user disable --now nightlight-schedule.timer
rm -f ~/.config/systemd/user/nightlight-schedule.service
rm -f ~/.config/systemd/user/nightlight-schedule.timer
systemctl --user daemon-reload
rm -rf ~/.config/waybar/nightlight
rm -f ~/.config/waybar/scripts/nightlight.sh
```

If you added a custom Waybar module, remove it from your Waybar configuration as well.

---

## Roadmap

Possible future improvements:

* Add direct Waybar status output.
* Add configurable presets.
* Add support for other backends such as `wlsunset` or `gammastep`.
* Add install options for different terminals.
* Add an AUR package when the project is more stable.

---
