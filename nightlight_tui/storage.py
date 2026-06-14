"""File I/O and validation for nightlight configuration."""

import re
import subprocess
from pathlib import Path

from nightlight_tui.config import (
    BASE_DIR,
    DEFAULT_TEMP,
    FILE_DEFAULTS,
    MAX_TEMP,
    MIN_TEMP,
    SCRIPT,
    TEMP_FILE,
    constants_env_content,
    CONSTANTS_FILE,
)


def ensure_files() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    for path, value in FILE_DEFAULTS.items():
        if not path.exists():
            path.write_text(value)

    CONSTANTS_FILE.write_text(constants_env_content())


def read_file(path: Path, default: str) -> str:
    try:
        return path.read_text().strip()
    except FileNotFoundError:
        return default


def write_file(path: Path, value: str) -> None:
    path.write_text(str(value).strip())


def validate_time(value: str) -> bool:
    if not re.match(r"^\d{2}:\d{2}$", value):
        return False

    hour, minute = value.split(":")
    h = int(hour)
    m = int(minute)

    return 0 <= h <= 23 and 0 <= m <= 59


def clamp_temp(temp: int) -> int:
    return max(MIN_TEMP, min(MAX_TEMP, temp))


def normalize_temp(value: str) -> int | None:
    if not value.isdigit():
        return None

    return clamp_temp(int(value))


def read_temp(default: str = str(DEFAULT_TEMP)) -> int:
    normalized = normalize_temp(read_file(TEMP_FILE, default))
    return normalized if normalized is not None else int(default)


def run_script(*args: str) -> bool:
    if not SCRIPT.is_file():
        return False

    result = subprocess.run([str(SCRIPT), *args], check=False)
    return result.returncode == 0
