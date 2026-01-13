"""
Скрипт сборки исполняемого файла и установщика AI Teacher Quest.

Использует PyInstaller (обязательно) и опционально Inno Setup (ISCC.exe)
для генерации установщика.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "AI Teacher Quest"
APP_BINARY_NAME = "AI_Teacher_Quest"
ROOT = Path(__file__).parent.resolve()
DIST_DIR = ROOT / "dist" / APP_BINARY_NAME
INNO_SCRIPT = ROOT / "installer" / "AI_Teacher_Quest.iss"


def run(command: list[str]) -> None:
    print(f"[build] Executing: {' '.join(command)}")
    subprocess.run(command, check=True)


def ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "PyInstaller не установлен. Установите его командой:\n"
            "    pip install pyinstaller"
        ) from exc


def build_executable(debug: bool = False) -> None:
    ensure_pyinstaller()
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR.parent, ignore_errors=True)
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "main.py",
        "--name",
        APP_BINARY_NAME,
        "--noconfirm",
        "--clean",
        "--windowed",
    ]
    if debug:
        cmd.append("--debug=all")
    run(cmd)
    print(f"[build] Исполняемый файл собран в {DIST_DIR}")


def build_installer() -> bool:
    iscc = shutil.which("iscc") or shutil.which("ISCC.exe")
    if not iscc:
        print(
            "[build] Inno Setup не найден. Установите Inno Setup и убедитесь, "
            "что исполняемый файл ISCC.exe доступен в PATH."
        )
        return False
    if not DIST_DIR.exists():
        raise SystemExit("Не найден dist/ каталог. Сначала запустите сборку PyInstaller.")
    run([iscc, str(INNO_SCRIPT)])
    print("[build] Установщик собран в installer/output")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Сборка AI Teacher Quest.")
    parser.add_argument(
        "--skip-installer",
        action="store_true",
        help="Не запускать Inno Setup после PyInstaller.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Сборка PyInstaller с дополнительными логами.",
    )
    args = parser.parse_args()

    build_executable(debug=args.debug)
    if not args.skip_installer:
        build_installer()


if __name__ == "__main__":
    main()

