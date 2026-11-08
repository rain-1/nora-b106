#!/usr/bin/env python3
"""Install project-local tools for the separate BLE OTA build."""
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
subprocess.run([sys.executable, str(HERE.parent / 'ble/build.py'), 'setup'], check=True, cwd=ROOT)
subprocess.run([str(ROOT / 'build/ble-env/bin/python'), '-m', 'pip', 'install', '-r',
                str(HERE / 'requirements.lock')], check=True, cwd=ROOT)
if not (HERE / 'keys/development.pem').exists():
    raise SystemExit('Restore the existing OTA development key; do not silently replace the key of installed bootloaders.')
print('BLE OTA build tools ready. No hardware was programmed.')
