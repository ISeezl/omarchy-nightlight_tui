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
    echo "Uso: $0 {toggle|apply}"
    exit 1
    ;;
esac