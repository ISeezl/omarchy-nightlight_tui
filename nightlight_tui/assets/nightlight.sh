#!/usr/bin/env bash

set -e

BASE_DIR="$HOME/.config/waybar/nightlight"
CONSTANTS_FILE="$BASE_DIR/constants.env"

STATE_FILE="$BASE_DIR/state"
TEMP_FILE="$BASE_DIR/temp"
SCHEDULE_FILE="$BASE_DIR/schedule_enabled"
START_FILE="$BASE_DIR/start"
END_FILE="$BASE_DIR/end"

if [ -f "$CONSTANTS_FILE" ]; then
    # shellcheck disable=SC1090
    source "$CONSTANTS_FILE"
fi

OFF_TEMP="${OFF_TEMP:-6000}"
DEFAULT_TEMP="${DEFAULT_TEMP:-4000}"
TEMP_STEP="${TEMP_STEP:-250}"
MIN_TEMP="${MIN_TEMP:-2500}"
MAX_TEMP="${MAX_TEMP:-6500}"

mkdir -p "$BASE_DIR"

[ -f "$STATE_FILE" ] || echo "off" > "$STATE_FILE"
[ -f "$TEMP_FILE" ] || echo "$DEFAULT_TEMP" > "$TEMP_FILE"
[ -f "$SCHEDULE_FILE" ] || echo "off" > "$SCHEDULE_FILE"
[ -f "$START_FILE" ] || echo "20:00" > "$START_FILE"
[ -f "$END_FILE" ] || echo "07:00" > "$END_FILE"

ensure_hyprsunset_running() {
    if pgrep -x hyprsunset >/dev/null 2>&1; then
        return 0
    fi

    if command -v uwsm-app >/dev/null 2>&1; then
        setsid uwsm-app -- hyprsunset >/dev/null 2>&1 &
    else
        setsid hyprsunset >/dev/null 2>&1 &
    fi

    local attempt
    for attempt in $(seq 1 10); do
        if pgrep -x hyprsunset >/dev/null 2>&1; then
            return 0
        fi
        sleep 0.2
    done

    return 1
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

get_schedule_enabled() {
    cat "$SCHEDULE_FILE" 2>/dev/null || echo "off"
}

get_start_time() {
    cat "$START_FILE" 2>/dev/null || echo "20:00"
}

get_end_time() {
    cat "$END_FILE" 2>/dev/null || echo "07:00"
}

is_integer() {
    case "$1" in
        ''|*[!0-9]*)
            return 1
            ;;
        *)
            return 0
            ;;
    esac
}

is_valid_time() {
    local value="$1"
    local hour minute

    case "$value" in
        [0-2][0-9]:[0-5][0-9])
            ;;
        *)
            return 1
            ;;
    esac

    hour="${value%%:*}"
    minute="${value##*:}"

    [ "$hour" -le 23 ] && [ "$minute" -le 59 ]
}

set_temp() {
    local temp="$1"

    if ! is_integer "$temp"; then
        temp="$DEFAULT_TEMP"
    fi

    if [ "$temp" -lt "$MIN_TEMP" ]; then
        temp="$MIN_TEMP"
    fi

    if [ "$temp" -gt "$MAX_TEMP" ]; then
        temp="$MAX_TEMP"
    fi

    echo "$temp" > "$TEMP_FILE"
}

time_to_minutes() {
    local value="$1"
    local hour="${value%%:*}"
    local minute="${value##*:}"

    echo $((10#$hour * 60 + 10#$minute))
}

should_schedule_be_on() {
    local start end start_min end_min now_min

    start="$(get_start_time)"
    end="$(get_end_time)"

    if ! is_valid_time "$start" || ! is_valid_time "$end"; then
        echo "Invalid schedule time. Expected HH:MM." >&2
        return 1
    fi

    start_min="$(time_to_minutes "$start")"
    end_min="$(time_to_minutes "$end")"
    now_min="$(time_to_minutes "$(date +%H:%M)")"

    if [ "$start_min" -lt "$end_min" ]; then
        [ "$now_min" -ge "$start_min" ] && [ "$now_min" -lt "$end_min" ]
        return
    fi

    [ "$now_min" -ge "$start_min" ] || [ "$now_min" -lt "$end_min" ]
}

run_schedule() {
    local enabled desired state

    enabled="$(get_schedule_enabled)"

    if [ "$enabled" != "on" ]; then
        return 0
    fi

    if should_schedule_be_on; then
        desired="on"
    else
        desired="off"
    fi

    state="$(get_state)"

    if [ "$desired" = "$state" ]; then
        return 0
    fi

    if [ "$desired" = "on" ]; then
        turn_on
    else
        turn_off
    fi
}

status() {
    local state temp text tooltip class

    state="$(get_state)"
    temp="$(get_temp)"

    if [ "$state" = "on" ]; then
        text="󰖔"
        tooltip="Nightlight enabled - ${temp}K\nLeft click: disable\nRight click: open settings\nScroll: adjust temperature"
        class="on"
    else
        text="󰖨"
        tooltip="Nightlight disabled\nLeft click: enable\nRight click: open settings\nScroll: adjust temperature"
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

    restart_nightlighted_waybar
}

turn_off() {
    ensure_hyprsunset_running
    hyprctl hyprsunset temperature "$OFF_TEMP"

    echo "off" > "$STATE_FILE"

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
    if ! is_integer "$temp"; then
        temp="$DEFAULT_TEMP"
    fi

    temp=$((temp + TEMP_STEP))

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
    if ! is_integer "$temp"; then
        temp="$DEFAULT_TEMP"
    fi

    temp=$((temp - TEMP_STEP))

    set_temp "$temp"

    if [ "$(get_state)" = "on" ]; then
        apply_state
    else
        restart_nightlighted_waybar
    fi
}

open_tui() {
    if command -v nightlight-tui >/dev/null 2>&1; then
        exec nightlight-tui
    fi

    if command -v python >/dev/null 2>&1; then
        exec python -m nightlight_tui
    fi

    echo "nightlight-tui is not installed." >&2
    exit 1
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

    schedule)
        run_schedule
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

    open-tui)
        open_tui
        ;;

    *)
        echo "Usage: $0 {status|toggle|apply|schedule|on|off|up|down|open-tui}"
        exit 1
        ;;
esac
