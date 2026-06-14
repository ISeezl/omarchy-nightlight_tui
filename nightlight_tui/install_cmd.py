"""Install nightlight assets into the user configuration directory."""

from __future__ import annotations

import shutil
import subprocess
from importlib import resources
from pathlib import Path

from nightlight_tui.config import (
    BASE_DIR,
    FILE_DEFAULTS,
    HOME,
    SCRIPT,
    SYSTEMD_SERVICE,
    SYSTEMD_TIMER,
    constants_env_content,
    CONSTANTS_FILE,
)

ASSETS = resources.files("nightlight_tui.assets")
SYSTEMD_USER_DIR = HOME / ".config/systemd/user"


def _copy_asset(name: str, target: Path, *, executable: bool = False) -> None:
    with resources.as_file(ASSETS / name) as source:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

    if executable:
        target.chmod(0o755)


def _write_systemd_units() -> None:
    with resources.as_file(ASSETS / SYSTEMD_SERVICE) as source:
        service_template = source.read_text(encoding="utf-8")

    service_content = service_template.replace("__NIGHTLIGHT_SCRIPT__", str(SCRIPT))

    SYSTEMD_USER_DIR.mkdir(parents=True, exist_ok=True)
    (SYSTEMD_USER_DIR / SYSTEMD_SERVICE).write_text(service_content, encoding="utf-8")
    _copy_asset(SYSTEMD_TIMER, SYSTEMD_USER_DIR / SYSTEMD_TIMER)


def _enable_schedule_timer() -> bool:
    commands = [
        ["systemctl", "--user", "daemon-reload"],
        ["systemctl", "--user", "enable", "--now", SYSTEMD_TIMER],
    ]

    for command in commands:
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            return False

    return True


def install(*, enable_timer: bool = True) -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    SCRIPT.parent.mkdir(parents=True, exist_ok=True)

    for path, value in FILE_DEFAULTS.items():
        if not path.exists():
            path.write_text(value)

    CONSTANTS_FILE.write_text(constants_env_content())
    _copy_asset("nightlight.sh", SCRIPT, executable=True)
    _write_systemd_units()

    print("Control script installed at:")
    print(f"  {SCRIPT}")
    print("Configuration directory:")
    print(f"  {BASE_DIR}")
    print("Shared constants:")
    print(f"  {CONSTANTS_FILE}")

    if enable_timer:
        if _enable_schedule_timer():
            print("Schedule timer enabled:")
            print(f"  {SYSTEMD_USER_DIR / SYSTEMD_TIMER}")
        else:
            print("Could not enable the schedule timer automatically.")
            print("Run manually:")
            print("  systemctl --user daemon-reload")
            print(f"  systemctl --user enable --now {SYSTEMD_TIMER}")


def main() -> None:
    print("Installing nightlight configuration...")
    print("")
    install()
    print("")
    print("Done.")


if __name__ == "__main__":
    main()
