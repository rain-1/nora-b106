#!/usr/bin/env python3
"""Audit OTA layout and create a sparse SWD factory image; no hardware access."""
from pathlib import Path
import hashlib
import json
import pickle
import struct
import sys

from intelhex import IntelHex

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "build/square-p3-ble-ota"
WS = ROOT / "build/ble-workspace"
version = sys.argv[1]
sys.path.insert(0, str(WS / "zephyr/scripts/dts/python-devicetree/src"))
layout = {"boot_partition": (0, 0x10000), "slot0_partition": (0x10000, 0x70000),
          "slot1_partition": (0x80000, 0x71000), "storage_partition": (0xf1000, 0xf000)}
configs = {}
for name, directory in [("boot", OUT / "bootloader"), ("app", OUT / ("app-" + version))]:
    configs[name] = dict(line.split("=", 1) for line in (directory / "zephyr/.config").read_text().splitlines()
                         if line.startswith("CONFIG_") and "=" in line)
    with (directory / "zephyr/edt.pickle").open("rb") as handle:
        edt = pickle.load(handle)
    for label, expected in layout.items():
        reg = edt.label2node[label].regs[0]
        assert (reg.addr, reg.size) == expected, (name, label, reg)
    assert edt.label2node['hfxo'].props['load-capacitance-femtofarad'].val == 20000
    assert edt.label2node['lfxo'].status == 'disabled'
    for key in ['NRF_APPROTECT_USE_UICR', 'NRF_SECURE_APPROTECT_USE_UICR', 'CLOCK_CONTROL_NRF_K32SRC_RC']:
        assert configs[name]['CONFIG_' + key] == 'y', (name, key)
    assert int(configs[name]['CONFIG_FLASH_LOAD_OFFSET'], 0) == (0 if name == 'boot' else 0x10000)
boot = IntelHex(str(OUT / "bootloader/zephyr/zephyr.hex"))
assert all(0 <= s < e <= 0x10000 for s, e in boot.segments()), boot.segments()
app = IntelHex(str(OUT / ("app-" + version) / "zephyr/zephyr.hex"))
assert all(0x10000 <= s < e <= 0x80000 for s, e in app.segments()), app.segments()
assert configs['boot']['CONFIG_BOOT_SWAP_USING_OFFSET'] == 'y'
assert configs['boot']['CONFIG_BOOT_VALIDATE_SLOT0'] == 'y'
assert configs['app']['CONFIG_MCUBOOT_BOOTLOADER_MODE_SWAP_USING_OFFSET'] == 'y'
assert configs['app']['CONFIG_MCUMGR_TRANSPORT_BT'] == 'y'
assert configs['app']['CONFIG_MCUMGR_GRP_IMG'] == 'y'
assert configs['app']['CONFIG_MCUMGR_GRP_OS'] == 'y'
assert configs['app']['CONFIG_SOC_NRF53_CPUNET_ENABLE'] == 'y'
assert configs['boot'].get('CONFIG_SOC_NRF53_CPUNET_ENABLE') != 'y'
dist = OUT / 'dist'
signed = (dist / ('nora-ota-' + version + '.signed.bin')).read_bytes()
confirmed = (dist / ('nora-ota-' + version + '.confirmed.bin')).read_bytes()
magic, load, header_size = struct.unpack_from('<IIH', signed)
assert magic == 0x96f3b83d and load == 0 and header_size == 0x200
major, minor, revision = map(int, version.split('.'))
assert struct.unpack_from('<BBHI', signed, 20) == (major, minor, revision, 0)
assert len(confirmed) == 0x70000 and len(signed) < 0x6f000
stack, entry = struct.unpack_from('<II', signed, 0x200)
assert 0x20000000 < stack <= 0x20070000
assert 0x10200 <= (entry & ~1) < 0x80000 and entry & 1
# No network flash or UICR records: only MCUboot, primary image and its trailer.
factory = IntelHex()
factory.merge(boot, overlap='error')
for index in range(0, len(confirmed), 4):
    word = confirmed[index:index + 4]
    if word != b'\xff' * len(word):
        factory.puts(0x10000 + index, word)
assert all(0 <= s < e <= 0x80000 for s, e in factory.segments())
factory.write_hex_file(str(dist / ('nora-ota-' + version + '.factory.hex')))
report = {'version': version, 'layout': layout, 'bootloader_bytes': len(boot),
          'signed_app_bytes': len(signed), 'signature': 'ECDSA P-256; imgtool verify passed',
          'network_controller': 'unchanged; no network records', 'uicr': 'no records',
          'runtime_entry': hex(entry), 'hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
           for p in dist.glob('nora-ota-' + version + '.*') if not p.name.endswith('.manifest.json')}}
(dist / ('nora-ota-' + version + '.manifest.json')).write_text(json.dumps(report, indent=2) + '\n')
print('PASS: matching OTA partitions, offset swap, debug startup, signatures, vectors and application-only factory image')
