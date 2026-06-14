#!/usr/bin/env bash

set -e

APP_NAME="Waybar Hyprsunset TUI"

CONFIG_DIR="$HOME/.config/waybar"
SCRIPT_DIR="$CONFIG_DIR/scripts"
NIGHTLIGHT_DIR="$CONFIG_DIR/nightlight"

NIGHTLIGHT_SCRIPT_SOURCE="scripts/nightlight.sh"
NIGHTLIGHT_SCRIPT_TARGET="$SCRIPT_DIR/nightlight.sh"

echo "======================================"
echo "Installer - $APP_NAME"
echo "======================================"
echo ""

confirm() {
    local message="$1"
    read -rp "$message [y/N]: " response

    if [[ "$response" =~ ^[yY]$ ]]; then
        return 0
    fi

    return 1
}

install_with_pacman() {
    local package="$1"

    if command -v pacman >/dev/null 2>&1; then
        sudo pacman -S --needed "$package"
    else
        echo "pacman was not found."
        echo "Please install this package manually: $package"
        return 1
    fi
}

echo "Checking dependencies..."
echo ""

if ! command -v python >/dev/null 2>&1; then
    echo "Python is not installed."

    if confirm "Do you want to install Python with pacman?"; then
        install_with_pacman python
    else
        echo "You must install Python manually:"
        echo "sudo pacman -S python"
        exit 1
    fi
else
    echo "Python found."
fi

if ! command -v pipx >/dev/null 2>&1; then
    echo "pipx is not installed."

    if confirm "Do you want to install pipx with pacman?"; then
        install_with_pacman python-pipx
        pipx ensurepath || true
    else
        echo "pipx was not installed."
        echo "You can install it manually with:"
        echo "sudo pacman -S python-pipx"
    fi
else
    echo "pipx found."
fi

if ! command -v hyprsunset >/dev/null 2>&1; then
    echo "hyprsunset is not installed."

    if confirm "Do you want to install hyprsunset with pacman?"; then
        install_with_pacman hyprsunset
    else
        echo "hyprsunset was not installed."
        echo "The app can open, but it will not be able to change the night light until you install it:"
        echo "sudo pacman -S hyprsunset"
    fi
else
    echo "hyprsunset found."
fi

echo ""
echo "Preparing configuration directories..."

mkdir -p "$SCRIPT_DIR"
mkdir -p "$NIGHTLIGHT_DIR"

echo "Directories ready:"
echo "$SCRIPT_DIR"
echo "$NIGHTLIGHT_DIR"

echo ""
echo "Installing control script..."

if [ ! -f "$NIGHTLIGHT_SCRIPT_SOURCE" ]; then
    echo "Error: $NIGHTLIGHT_SCRIPT_SOURCE was not found."
    echo "Please run this installer from the project root directory."
    exit 1
fi

cp "$NIGHTLIGHT_SCRIPT_SOURCE" "$NIGHTLIGHT_SCRIPT_TARGET"
chmod +x "$NIGHTLIGHT_SCRIPT_TARGET"

echo "Control script installed at:"
echo "$NIGHTLIGHT_SCRIPT_TARGET"

echo ""
echo "Creating configuration files..."

[ -f "$NIGHTLIGHT_DIR/state" ] || echo "off" > "$NIGHTLIGHT_DIR/state"
[ -f "$NIGHTLIGHT_DIR/temp" ] || echo "4000" > "$NIGHTLIGHT_DIR/temp"
[ -f "$NIGHTLIGHT_DIR/schedule_enabled" ] || echo "off" > "$NIGHTLIGHT_DIR/schedule_enabled"
[ -f "$NIGHTLIGHT_DIR/start" ] || echo "20:00" > "$NIGHTLIGHT_DIR/start"
[ -f "$NIGHTLIGHT_DIR/end" ] || echo "07:00" > "$NIGHTLIGHT_DIR/end"

echo "Configuration files created/verified:"
echo "$NIGHTLIGHT_DIR/state"
echo "$NIGHTLIGHT_DIR/temp"
echo "$NIGHTLIGHT_DIR/schedule_enabled"
echo "$NIGHTLIGHT_DIR/start"
echo "$NIGHTLIGHT_DIR/end"

echo ""
echo "======================================"
echo "Base installation complete."
echo "======================================"
echo ""

echo "Now install the Python app with:"
echo ""
echo "pipx install ."
echo ""

echo "Then run it with:"
echo ""
echo "nightlight-tui"
echo ""

echo "Important:"
echo "Make sure hyprsunset starts with Hyprland by adding this to your hyprland.conf:"
echo ""
echo "exec-once = hyprsunset"
echo ""

echo "After that, restart your Hyprland session."