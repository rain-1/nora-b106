#!/usr/bin/env python3
"""Set up, build and audit Dragon P3's separate Zephyr BLE firmware."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import pickle
import subprocess
import sys
import venv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ENV = ROOT / "build/ble-env"
WS = ROOT / "build/ble-workspace"
OUT = ROOT / "build/square-p3-ble"
ZREV = "684c9e8f32e4373a21098559f748f06915f950c9"
MODULES = ["cmsis", "cmsis_6", "hal_nordic", "mbedtls", "tf-psa-crypto", "libmetal", "open-amp", "mcuboot", "zcbor"]


def environment():
    return dict(os.environ, PATH=str(ENV / "bin") + os.pathsep + os.environ["PATH"],
                ZEPHYR_TOOLCHAIN_VARIANT="gnuarmemb", GNUARMEMB_TOOLCHAIN_PATH="/usr")


def run(*args, cwd=ROOT):
    subprocess.run([str(a) for a in args], cwd=cwd, env=environment(), check=True)


def setup():
    if not (ENV / "bin/python").exists():
        venv.create(ENV, with_pip=True)
    run(ENV / "bin/python", "-m", "pip", "install", "-r", HERE / "requirements.lock")
    WS.mkdir(parents=True, exist_ok=True)
    if not (WS / "zephyr/.git").exists():
        run("git", "clone", "--depth", "1", "--branch", "v4.4.0",
            "https://github.com/zephyrproject-rtos/zephyr.git", WS / "zephyr")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=WS / "zephyr", text=True).strip()
    if revision != ZREV:
        raise RuntimeError("Existing Zephyr checkout differs from pinned revision; left unchanged")
    if not (WS / ".west/config").exists():
        run(ENV / "bin/west", "init", "-l", WS / "zephyr")
    run(ENV / "bin/west", "update", "--narrow", "-o=--depth=1", *MODULES, cwd=WS)


def build():
    run(ENV / "bin/west", "build", "-b", "nora_dragon/nrf5340/cpuapp", HERE / "app",
        "-d", OUT / "app", "--", "-DBOARD_ROOT=" + str(HERE), cwd=WS)
    run(ENV / "bin/west", "build", "-b", "nora_dragon/nrf5340/cpunet",
        WS / "zephyr/samples/bluetooth/hci_ipc", "-d", OUT / "net", "--",
        "-DBOARD_ROOT=" + str(HERE), "-DEXTRA_CONF_FILE=" + str(HERE / "network.conf"), cwd=WS)


def audit():
    # Run with the build environment so intelhex and devicetree classes match.
    if Path(sys.prefix).resolve() != ENV.resolve():
        run(ENV / "bin/python", __file__, "check")
        return
    from intelhex import IntelHex
    sys.path.insert(0, str(WS / "zephyr/scripts/dts/python-devicetree/src"))
    results = {}
    for core, start, end in [("app", 0, 0x100000), ("net", 0x1000000, 0x1040000)]:
        directory = OUT / core / "zephyr"
        image = IntelHex(str(directory / "zephyr.hex"))
        assert image.minaddr() == start
        assert all(start <= s < e <= end for s, e in image.segments()), "Unexpected flash/UICR record"
        config = dict(line.split("=", 1) for line in (directory / ".config").read_text().splitlines()
                      if line.startswith("CONFIG_") and "=" in line)
        for key in ["NRF_APPROTECT_USE_UICR", "CLOCK_CONTROL_NRF_K32SRC_RC", "CLOCK_CONTROL_NRF_K32SRC_500PPM", "IPC_SERVICE"]:
            assert config["CONFIG_" + key] == "y", (core, key)
        with (directory / "edt.pickle").open("rb") as handle:
            edt = pickle.load(handle)
        shared = edt.label2node["sram0_shared"].regs[0]
        assert (shared.addr, shared.size) == (0x20070000, 0x10000)
        if core == "app":
            for key in ["NRF_SECURE_APPROTECT_USE_UICR", "CLOCK_CONTROL_NRF_K32SRC_RC_CALIBRATION", "SOC_NRF53_CPUNET_ENABLE", "BT_HCI_IPC"]:
                assert config["CONFIG_" + key] == "y", key
            assert config["CONFIG_BT_PERIPHERAL"] == "y"
            assert config["CONFIG_BT_MAX_CONN"] == "1"
            assert int(config["CONFIG_COMMON_LIBC_MALLOC_ARENA_SIZE"]) >= 8192
            assert edt.label2node["hfxo"].props["load-capacitance-femtofarad"].val == 20000
            assert edt.label2node["lfxo"].status == "disabled"
            gpio = edt.label2node["test_led"].props["gpios"].val[0]
            assert gpio.controller == edt.label2node["gpio0"] and gpio.data == {"pin": 20, "flags": 0}
            uart = edt.label2node["uart0"]
            assert uart.props["current-speed"].val == 115200
            groups = edt.label2node["uart0_default"].children
            assert groups["tx"].props["psels"].val == [24]
            assert groups["rx"].props["psels"].val == [(1 << 24) | 38]
        else:
            assert config["CONFIG_BT_LL_SW_SPLIT"] == "y"
            assert config.get("CONFIG_SERIAL") != "y"
        results[core] = {"segments": image.segments(), "sha256": hashlib.sha256((directory / "zephyr.hex").read_bytes()).hexdigest()}
    results["zephyr_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=WS / "zephyr", text=True).strip()
    assert results["zephyr_commit"] == ZREV
    results["compiler"] = subprocess.check_output(["arm-none-eabi-gcc", "--version"], text=True).splitlines()[0]
    results["source_sha256"] = {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(HERE.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
    (OUT / "manifest.json").write_text(json.dumps(results, indent=2) + "\n")
    print("PASS: code-only images, debug startup, RC clocks, 20 pF HFXO, IPC RAM, UART and LED pin mapping")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["setup", "build", "check"], default="build", nargs="?")
    action = parser.parse_args().action
    if action == "setup":
        setup()
    elif action == "build":
        build()
        audit()
    else:
        audit()
