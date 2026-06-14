#!/usr/bin/env bash

set -e

BASE_DIR="$HOME/.config/waybar/nightlight"

STATE_FILE="$BASE_DIR/state"
TEMP_FILE="$BASE_DIR/temp"

OFF_TEMP=6000
DEFAULT_TEMP=4000
STEP=250
MIN_TEMP=2500
MAX_TEMP=5000

mkdir -p "$BASE_DIR"

[ -f "$STATE_FILE" ] || echo "off" > "$STATE_FILE"
[ -f "$TEMP_FILE" ] || echo "$DEFAULT_TEMP" > "$TEMP_FILE"

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

restart_waybar_module() {
    pkill -RTMIN+8 waybar 2>/dev/null || true
}

restart_nightlighted_waybar() {
    if [ -f "$HOME/.config/waybar/config.jsonc" ] &&
       grep -q "custom/nightlight" "$HOME/.config/waybar/config.jsonc"; then
        restart_waybar_module
    fi
}

get_state() {
    cat "$STATE_FILE" 2>/dev/null || echo "off"
}

get_temp() {
    cat "$TEMP_FILE" 2>/dev/null || echo "$DEFAULT_TEMP"
}

set_temp() {
    local temp="$1"

    if [ "$temp" -lt "$MIN_TEMP" ]; then
        temp="$MIN_TEMP"
    fi

    if [ "$temp" -gt "$MAX_TEMP" ]; then
        temp="$MAX_TEMP"
    fi

    echo "$temp" > "$TEMP_FILE"
}

status() {
    local state
    local temp
    local text
    local tooltip
    local class

    state="$(get_state)"
    temp="$(get_temp)"

    if [ "$state" = "on" ]; then
        text="󰖔 ${temp}K"
        tooltip="Nightlight enabled - ${temp}K"
        class="on"
    else
        text="󰖨"
        tooltip="Nightlight disabled"
        class="off"
    fi

    printf '{"text":"%s","tooltip":"%s","class":"%s"}\n' "$text" "$tooltip" "$class"
}

turn_on() {
    local temp
    temp="$(get_temp)"

    ensure_hyprsunset_running
    hyprctl hyprsunset temperature "$temp"

    echo "on" > "$STATE_FILE"

    if command -v notify-send >/dev/null 2>&1; then
        notify-send -u low " Nightlight screen temperature" "${temp}K"
    fi

    restart_nightlighted_waybar
}

turn_off() {
    ensure_hyprsunset_running
    hyprctl hyprsunset temperature "$OFF_TEMP"

    echo "off" > "$STATE_FILE"

    if command -v notify-send >/dev/null 2>&1; then
        notify-send -u low " Daylight screen temperature" "${OFF_TEMP}K"
    fi

    restart_nightlighted_waybar
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

increase_temp() {
    local temp
    temp="$(get_temp)"
    temp=$((temp + STEP))

    set_temp "$temp"

    if [ "$(get_state)" = "on" ]; then
        apply_state
    else
        restart_nightlighted_waybar
    fi
}

decrease_temp() {
    local temp
    temp="$(get_temp)"
    temp=$((temp - STEP))

    set_temp "$temp"

    if [ "$(get_state)" = "on" ]; then
        apply_state
    else
        restart_nightlighted_waybar
    fi
}

case "$1" in
    status)
        status
        ;;

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

    up)
        increase_temp
        ;;

    down)
        decrease_temp
        ;;

    *)
        echo "Usage: $0 {status|toggle|apply|on|off|up|down}"
        exit 1
        ;;
esac