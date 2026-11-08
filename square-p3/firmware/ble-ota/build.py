#!/usr/bin/env python3
"""Build separate MCUboot/BLE OTA images; never flashes a connected board."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BLE = HERE.parent / "ble"
ENV = ROOT / "build/ble-env"
WS = ROOT / "build/ble-workspace"
OUT = ROOT / "build/square-p3-ble-ota"
KEY = HERE / "keys/development.pem"
SLOT_SIZE = 0x70000


def run(*args, cwd=WS):
    env = dict(os.environ, PATH=str(ENV / "bin") + os.pathsep + os.environ["PATH"],
               ZEPHYR_TOOLCHAIN_VARIANT="gnuarmemb", GNUARMEMB_TOOLCHAIN_PATH="/usr")
    subprocess.run([str(a) for a in args], cwd=cwd, env=env, check=True)


def build(version):
    OUT.mkdir(parents=True, exist_ok=True)
    if not KEY.exists():
        raise SystemExit("Development key missing: restore it; do not silently change bootloader keys")
    imgtool = WS / "bootloader/mcuboot/scripts/imgtool.py"
    signing = OUT / "signing.conf"
    signing.write_text("CONFIG_BOOT_SIGNATURE_KEY_FILE=" + json.dumps(str(KEY)) + "\n")
    common = ["-DBOARD_ROOT=" + str(BLE)]
    run(ENV / "bin/west", "build", "-b", "nora_dragon/nrf5340/cpuapp",
        WS / "bootloader/mcuboot/boot/zephyr", "-d", OUT / "bootloader", "--", *common,
        "-DDTC_OVERLAY_FILE=" + str(HERE / "bootloader.overlay"),
        "-DCONF_FILE=" + str(HERE / "bootloader.conf"), "-DEXTRA_CONF_FILE=" + str(signing))
    appdir = OUT / ("app-" + version)
    app_version = OUT / ("version-" + version + ".conf")
    app_version.write_text("CONFIG_BT_DIS_FW_REV_STR=" + json.dumps(version) + "\n")
    run(ENV / "bin/west", "build", "-b", "nora_dragon/nrf5340/cpuapp", HERE / "app",
        "-d", appdir, "--", *common, "-DCONF_FILE=" + str(BLE / "app/prj.conf"),
        "-DDTC_OVERLAY_FILE=" + str(HERE / "layout.overlay"),
        "-DEXTRA_CONF_FILE=" + str(HERE / "app/ota.conf") + ";" + str(app_version),
        "-DNORA_FIRMWARE_VERSION=" + version)
    dist = OUT / "dist"
    dist.mkdir(exist_ok=True)
    signed = dist / ("nora-ota-" + version + ".signed.bin")
    confirmed = dist / ("nora-ota-" + version + ".confirmed.bin")
    sign_args = [ENV / "bin/python", imgtool, "sign", "--key", KEY, "--align", "4",
                 "--header-size", "0x200", "--slot-size", hex(SLOT_SIZE),
                 "--max-sectors", "113", "--version", version]
    run(*sign_args, appdir / "zephyr/zephyr.bin", signed)
    run(*sign_args, "--pad", "--confirm", appdir / "zephyr/zephyr.bin", confirmed)
    run(ENV / "bin/python", imgtool, "verify", "--key", KEY, signed)
    run(ENV / "bin/python", imgtool, "verify", "--key", KEY, confirmed)
    # Validation and sparse factory HEX generation run in the dependency venv.
    run(ENV / "bin/python", HERE / "validate.py", version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="1.0.0")
    args = parser.parse_args()
    if not re.fullmatch(r"\d{1,3}\.\d{1,3}\.\d{1,5}", args.version):
        parser.error("Version must be major.minor.revision")
    build(args.version)
