"""TUI para controlar hyprsunset desde Waybar/Hyprland."""

from nightlight_tui.app import NightLightTUI, main
from nightlight_tui.install_cmd import install, main as install_main

__all__ = ["NightLightTUI", "install", "install_main", "main"]
