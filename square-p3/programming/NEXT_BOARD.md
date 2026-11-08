# Flash the next square-p3 board with your Pico 2 W

This installs the **phone-controlled Bluetooth LED firmware** that worked on
the first board. It is for the minimum **U1 + C1 + C2** assembly, with JP1
open and power supplied by the Pico. The existing Pico already has programmer
firmware; do not put it back into BOOTSEL or replace that firmware.

The same NORA firmware works on subsequent boards. Each board gets its own
`NORA Dragon XXXX` name from its device ID. Keep a separate original backup
for every module; never copy the first board's factory identity onto the next.

## 1. Move the wires with power disconnected

Unplug the Pico from USB. Disconnect the first target board completely and
connect only the next board. Looking at the component side with the antenna
at the top, **J2 is on the left**. Its top square pad is pin 1. J3 is the
right-hand header, also numbered from its top square pad.

| Pico signal | Pico physical pin | Target connection |
|---|---:|---|
| GND | 3 | J2 pin 2, GND |
| 3V3 OUT | 36 | J2 pin 1, 3V3 |
| GP2 | 4 | J2 pin 3, SWCLK |
| GP3 | 5 | J2 pin 4, SWDIO |
| GP5, UART RX | 7 | J3 pin 3, P0.24 TX |
| GP4, UART TX | 6 | J3 pin 4, P1.06 RX |

Leave J2 pin 5/RESET_N disconnected. UART is optional for flashing but useful
for checking the result. Keep SWD wires short. These are the Pico's header
pins, not its own small debug pads.

For the external LED:

**J3 pin 13 → 1 kΩ resistor → LED anode (long leg)**

**LED cathode (short leg) → J3 pin 2/GND**

Keep **JP1 open**. Use **3V3 OUT**, never Pico VBUS or VSYS. The board's
headers and GPIOs are not 5 V tolerant. This guide assumes no other target
power source is connected. See [the hardware guide](../hardware/README.md)
if your assembly also includes USB power components.

## 2. Check power

With power disconnected, check for a persistent short between J2 pins 1
and 2. A brief continuity beep while a capacitor charges is possible; a
continuous beep or resistance staying near zero needs investigation.

Plug in the Pico and measure DC voltage: black probe to J2 pin 2, red probe
to J2 pin 1. Expect approximately **3.3 V**. Disconnect power if that is wrong
and recheck the wiring before continuing.

## 3. Open a terminal in this repository

All following commands run from the repository root:

```sh
cd /home/riv/Code/nora-b106
```

The working nRF53-capable OpenOCD and firmware images are already installed
locally on this machine. Check the images before flashing:

```sh
python3 square-p3/firmware/ble/build.py check
```

It should print `PASS`. On a fresh checkout, the ignored build files will be
missing: follow the [BLE build guide](../firmware/ble/README.md#build) and
the [OpenOCD setup guide](README.md#openocd-version-requirement) first.
The standard system OpenOCD 0.12.0 is insufficient; use the explicit local
binary in the commands below.

## 4. Identify the module without programming it

```sh
build/tools/openocd/bin/openocd \
  -f square-p3/programming/pico-nrf53.cfg \
  -c init -c 'targets nrf53.cpuapp' -c poll -c 'halt 3000' \
  -c 'mdw 0x00ff0204 3' -c shutdown
```

Look for `Cortex-M33`, successful examination, and a line beginning
`0x00ff0204:` containing two device-ID words followed by `00005340`.
The device-ID words will differ from the first board. This leaves the
application core halted; the backup/flash steps below handle that.

If access fails, stop here. Check voltage, SWCLK/SWDIO, ground and soldering.
Do not run `recover`, `nrf53_recover` or erase-all commands as a troubleshooting
shortcut. They can erase factory data. Save the output if you need help.

## 5. Back up this board's original contents

Choose a new directory for this board. The example uses `board-02-original`;
change that label for later boards. **If `mkdir` says it already exists,
stop and choose a new name.** Do not reuse another module's backup folder.

```sh
export NORA_BACKUP_DIR="$PWD/build/bringup-backups/board-02-original"
mkdir -p build/bringup-backups
mkdir "$NORA_BACKUP_DIR"

build/tools/openocd/bin/openocd \
  -f square-p3/programming/pico-nrf53.cfg \
  -f square-p3/programming/backup.cfg
```

The backup script refuses to overwrite its expected output files. It saves
both cores' flash and documented configuration/factory registers, records
the module ID, and restarts the target. It changes runtime debug state but
does not program or erase flash. Expect six `dumped ... bytes` messages and
`Backup complete for ...`. If any command fails, stop before flashing.
Partial backups are not sufficient.

Verify lengths and record SHA-256 hashes with this complete command:

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib, json, os

folder = Path(os.environ['NORA_BACKUP_DIR'])
expected = {
    'app-flash.bin': 1048576,
    'app-uicr.bin': 4096,
    'app-ficr.bin': 4096,
    'net-flash.bin': 262144,
    'net-uicr-documented.bin': 896,
    'net-ficr.bin': 1024,
}
device_id = (folder / 'device-id.txt').read_text().strip()
records = {}
for name, size in expected.items():
    data = (folder / name).read_bytes()
    if len(data) != size:
        raise SystemExit(f'STOP: {name} has {len(data)} bytes; expected {size}')
    records[name] = {'bytes': size, 'sha256': hashlib.sha256(data).hexdigest()}
manifest = {'device_id': device_id, 'files': records}
(folder / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('PASS: all six backups have expected lengths; hashes recorded for', device_id)
PY
```

This detects missing/truncated files and records hashes; it does not prove
that read-protected or read-masked contents were accessible. Stop if OpenOCD
reported read/access errors even if some files exist. Keep another copy of
this backup folder somewhere outside the repository's ignored `build/` tree.

## 6. Flash both Bluetooth images

Close any terminal using the Pico's serial port. Keep the board connected:

```sh
build/tools/openocd/bin/openocd \
  -f square-p3/programming/pico-nrf53.cfg \
  -f square-p3/programming/ble-flash.cfg
```

This replaces code in **both cores** with the Bluetooth host and controller.
It erases the code pages needed for those images, verifies their contents,
and restarts the board. It does not write UICR or perform erase-all/recovery.
The original backup is what preserves your ability to restore previous code.

Let it finish before unplugging. The script handles the network-core
halt/reset sequence that we established on the first board. Do not add an
extra erase/recover step or replace it with a one-core programming command.

OpenOCD can print erase-range padding warnings; those describe the code pages
being written. An actual `Error`, write timeout, failed verification or failed
examination is a reason to stop and save the output. A shell exit code alone
does not establish that every OpenOCD command succeeded.

## 7. Check the result

The LED should blink by itself. For UART, find the Pico serial port:

```sh
ls /dev/serial/by-id/
python3 square-p3/firmware/uart-console/console.py /dev/ttyACM0
```

If it is not `/dev/ttyACM0`, use the Pico's actual path shown by the first
command. Type `info` then Enter. Expect the board's own ID,
`advertising: active`, and `NORA Dragon XXXX`. Type `on`, `off`, `blink`,
`interval 100` or `state` to try the local controls. Ctrl-C exits the terminal.

You can also run the automatic UART checks while the phone is disconnected:

```sh
build/ble-env/bin/python square-p3/firmware/ble/smoke_test.py /dev/ttyACM0
```

Then use your phone to scan for the new `NORA Dragon XXXX` name, connect, and
follow [phone LED control](../firmware/ble/PHONE_LED.md). The first board's
`D25D` suffix is not expected on the next module.

Finally, unplug and reconnect the Pico, reconnect from the phone and send
another LED command. This checks startup from flash and operation after a
power cycle, just as we did with the first board.

## Reflashing this same board later

Keep its original backup. Rebuild only when you change the firmware:

```sh
python3 square-p3/firmware/ble/build.py build
```

Then repeat the audit, flash and functional checks. Never restore another
board's UICR/identity files. A protected or unresponsive module needs a
separate diagnosis; this guide deliberately does not perform automatic recovery.
