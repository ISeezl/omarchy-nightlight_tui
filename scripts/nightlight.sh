#!/usr/bin/env bash

set -e

BASE_DIR="$HOME/.config/waybar/nightlight"

STATE_FILE="$BASE_DIR/state"
TEMP_FILE="$BASE_DIR/temp"

OFF_TEMP=6000

mkdir -p "$BASE_DIR"

[ -f "$STATE_FILE" ] || echo "off" > "$STATE_FILE"
[ -f "$TEMP_FILE" ] || echo "4000" > "$TEMP_FILE"

ensure_hyprsunset_running() {
    if ! pgrep -x hyprsunset >/dev/null 2>&1; then
        if command -v uwsm-app >/dev/null 2>&1; then
            setsid uwsm-app -- hyprsunset >/dev/null 2>&1 &
        else
            setsid hyprsunset >/dev/null 2>&1 &
        fi

        sleep 1
    fi
}

restart_nightlight_waybar() {
    if [ -f "$HOME/.config/waybar/config.jsonc" ] &&
       grep -q "custom/nightlight" "$HOME/.config/waybar/config.jsonc"; then
        if command -v omarchy-restart-waybar >/dev/null 2>&1; then
            omarchy-restart-waybar
        fi
    fi
}

get_state() {
    cat "$STATE_FILE" 2>/dev/null || echo "off"
}

get_temp() {
    cat "$TEMP_FILE" 2>/dev/null || echo "4000"
}

turn_on() {
    local temp
    temp="$(get_temp)"

    ensure_hyprsunset_running
    hyprctl hyprsunset temperature "$temp"

    echo "on" > "$STATE_FILE"

    if command -v notify-send >/dev/null 2>&1; then
        notify-send -u low "  Nightlight screen temperature" "${temp}K"
    fi

    restart_nightlight_waybar
}

turn_off() {
    ensure_hyprsunset_running
    hyprctl hyprsunset temperature "$OFF_TEMP"

    echo "off" > "$STATE_FILE"

    if command -v notify-send >/dev/null 2>&1; then
        notify-send -u low "  Daylight screen temperature" "${OFF_TEMP}K"
    fi

    restart_nightlight_waybar
}

apply_state() {
    local state
    state="$(get_state)"

    if [ "$state" = "on" ]; then
        turn_on
    else
        turn_off
    fi
}

toggle_state() {
    local state
    state="$(get_state)"

    if [ "$state" = "on" ]; then
        turn_off
    else
        turn_on
    fi
}

case "$1" in
    toggle)
        toggle_state
        ;;

    apply)
        apply_state
        ;;

    on)
        turn_on
        ;;

    off)
        turn_off
        ;;

    *)
        echo "Usage: $0 {toggle|apply|on|off}"
        exit 1
        ;;
esac