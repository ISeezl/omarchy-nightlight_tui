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
               | Temperature Presets
               | Configuration
```

Main sections:

* **Current Status**: shows whether night light is enabled, current temperature, schedule status, start time, and end time.
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

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/waybar-hyprsunset-tui.git
cd waybar-hyprsunset-tui
```

Make the installer executable:

```bash
chmod +x install.sh
```

Run the installer:

```bash
./install.sh
```

Install the Python app with `pipx`:

```bash
pipx install .
```

Run the app:

```bash
nightlight-tui
```

---

## Development Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/waybar-hyprsunset-tui.git
cd waybar-hyprsunset-tui
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
```

Run the app:

```bash
nightlight-tui
```

Or run it directly with Python:

```bash
python -m nightlight_tui.app
```

---

## Project Structure

```text
waybar-hyprsunset-tui/
├── nightlight_tui/
│   ├── __init__.py
│   └── app.py
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
nightlight_tui/app.py      Main Textual TUI application.
scripts/nightlight.sh      Control script that talks to hyprsunset.
install.sh                 Installer for local configuration files.
pyproject.toml             Python package configuration.
README.md                  Project documentation.
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
```

Default values:

```text
state=off
temp=4000
schedule_enabled=off
start=20:00
end=07:00
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

---

## Example `nightlight.sh`

The file `scripts/nightlight.sh` should use logic similar to this:

```bash
#!/usr/bin/env bash

set -e

BASE_DIR="$HOME/.config/waybar/nightlight"

STATE_FILE="$BASE_DIR/state"
TEMP_FILE="$BASE_DIR/temp"

mkdir -p "$BASE_DIR"

[ -f "$STATE_FILE" ] || echo "off" > "$STATE_FILE"
[ -f "$TEMP_FILE" ] || echo "4000" > "$TEMP_FILE"

STATE="$(cat "$STATE_FILE")"
TEMP="$(cat "$TEMP_FILE")"

case "$1" in
  toggle)
    if [ "$STATE" = "on" ]; then
      hyprctl hyprsunset identity
      echo "off" > "$STATE_FILE"
    else
      hyprctl hyprsunset temperature "$TEMP"
      echo "on" > "$STATE_FILE"
    fi
    ;;

  apply)
    if [ "$STATE" = "on" ]; then
      hyprctl hyprsunset temperature "$TEMP"
    else
      hyprctl hyprsunset identity
    fi
    ;;

  *)
    echo "Usage: $0 {toggle|apply}"
    exit 1
    ;;
esac
```

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

The TUI can save schedule settings, but automatic scheduling requires a process to check the saved time values.

Possible options:

* A Waybar script running on an interval.
* A systemd user timer.
* A small background daemon.
* Direct schedule handling inside `nightlight.sh`.

This depends on how your Waybar and Hyprland setup is configured.

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

Remove configuration files:

```bash
rm -rf ~/.config/waybar/nightlight
rm -f ~/.config/waybar/scripts/nightlight.sh
```

If you added a custom Waybar module, remove it from your Waybar configuration as well.

---

## Roadmap

Possible future improvements:

* Add a background daemon for automatic scheduling.
* Add direct Waybar status output.
* Add configurable presets.
* Add support for other backends such as `wlsunset` or `gammastep`.
* Add install options for different terminals.
* Add an AUR package when the project is more stable.

---
