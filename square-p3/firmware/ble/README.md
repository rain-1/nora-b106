# Dragon P3 Bluetooth LED control

This separate firmware supports the U1/C1/C2 minimum assembly, using the
existing Pico SWD/power/UART wiring. It does not change the shared P1 USB
bootloader/application. No USB hardware is required.

For a new assembly on this machine, start with the [step-by-step next-board
guide](../../programming/NEXT_BOARD.md), including its per-module backup.

For signed application updates over Bluetooth, use the separate
[MCUboot/OTA guide](../ble-ota/README.md). That layout needs one initial Pico
installation; it has been tested on the second board, NORA Dragon 3702.

The application core runs Zephyr's Bluetooth host, a UART shell and the external
P0.20 LED. The network core runs Zephyr's standard `hci_ipc` controller. Both
use custom NORA board definitions, the internal LF RC clock, matching shared
RAM at 0x20070000, and runtime debug initialization that follows UICR. The
application enables RC calibration and the module's 20 pF HFXO load setting.
No DK buttons, LEDs, USB, external LF crystal or flash partitions are inherited.

Advertising is now connectable, with one phone connection at a time and the name
`NORA Dragon XXXX`, where XXXX is the low 16 bits of the application device ID.
The first bench board is `NORA Dragon D25D`. A custom GATT service controls LED
mode and blink interval and exposes a readable state. No pairing is required;
this bench service allows a nearby connected device to control the LED.
Advertising restarts after disconnection once the connection object is free.
Zephyr uses a random static Bluetooth identity; the manufacturer's
public Bluetooth address remains preserved in UICR but is not used on air by
this firmware. Two IDs could theoretically share the same four-digit suffix.

## Build

Requirements on Linux: Python 3.12+, Python venv support, Git, and Debian's
`gcc-arm-none-eabi` / `libnewlib-arm-none-eabi` toolchain. The bench build used
ARM GCC 14.2.1. Python tools are installed under the repository's ignored
`build/ble-env/`, sources under `build/ble-workspace/`, and outputs under
`build/square-p3-ble/`. Setup uses the included Python dependency lock and
Zephyr v4.4.0, commit `684c9e8f32e4373a21098559f748f06915f950c9`, with
manifest-pinned Nordic, CMSIS, crypto and IPC modules. It does not replace
system Python or the P1 firmware build environment.

From the repository root:

```sh
python3 square-p3/firmware/ble/build.py setup
python3 square-p3/firmware/ble/build.py build
python3 square-p3/firmware/ble/build.py check
```

`build` also audits both code-only HEX ranges, debug startup settings, clocks,
shared RAM and application UART/LED pins, then records source/artifact hashes
in `build/square-p3-ble/manifest.json`. No UICR records are allowed in either
firmware image. The images boot directly from each core's flash base; do not
combine these with the P1 USB bootloader layout.

## Wiring and installation

Use ../../programming/README.md for power and SWD. JP1 stays open with the
minimum assembly powered from Pico 3V3 OUT. UART is 115200 8N1:

| Target | Debugger Pico |
|---|---|
| J3 pin 3, P0.24 TX | GP5, physical pin 7 |
| J3 pin 4, P1.06 RX | GP4, physical pin 6 |
| J3 pin 13, P0.20 | 1 kΩ → external LED anode; cathode → GND |

Before first installation on **each** module, identify it and back up both
cores' accessible flash, documented UICR and factory information separately.
The network core has 256 KiB flash; its documented UICR registers occupy
0x380 bytes, including the address copy at UICR+0x300. Network FICR occupies
0x400 bytes. Application UICR contains the public address at +0x100. Avoid
treating unreadable or read-masked register windows as restorable key data.
Do not restore one module's identity backup onto another module.

With backups complete and audit passing:

```sh
build/tools/openocd/bin/openocd -f square-p3/programming/pico-nrf53.cfg \
  -f square-p3/programming/ble-flash.cfg
```

The script programs/verifies network code first. It clears the network debug
trap/halt request, holds that core off while programming application code,
then restarts the application. The application starts the network core.
Keeping the network core running during application programming caused a
flash-algorithm timeout on the bench; leaving its debug halt request asserted
prevented IPC startup. Do not substitute ad hoc core-by-core reset sequences.
The script does not recover/mass erase or write UICR. If debug access is
protected, stop and assess recovery separately rather than automatically
erasing either core.

## Console and phone check

The existing standard-library UART terminal still works:

```sh
python3 square-p3/firmware/uart-console/console.py /dev/ttyACM0
```

Type `info`, `on`, `off`, `blink`, `interval 100`, `state` or Zephyr's `help`,
followed by Enter. Blink intervals are 50–5000 ms per transition. Settings
are shared with Bluetooth and reset to blinking at 500 ms on reboot.
Ctrl-C exits the host terminal. `info` prints the advertised name, device ID,
Bluetooth identity and whether advertising started successfully.

The BLE-specific host smoke test uses the build environment's pyserial:

```sh
build/ble-env/bin/python square-p3/firmware/ble/smoke_test.py /dev/ttyACM0
```

Add `--wait-startup` before resetting/programming if capturing startup logs.
Close other terminals on that port first. Prefer the Pico's stable
`/dev/serial/by-id/` path where possible.

On a phone, use a BLE scanner (for example nRF Connect), start scanning and
look for `NORA Dragon D25D` on the first board. A generic Bluetooth pairing
screen is not needed. There is no need to pair. For connection and characteristic
writes, follow [phone LED control](PHONE_LED.md).

## Validation status

The advertising-only v1 images built and verified on the first physical board. Independent
readback of each complete code image, including padding, matched byte-for-byte.
Application configuration/OTP and the complete documented network UICR matched
the original backups after installation. The host and
controller exchanged HCI commands through IPC; `bt_enable` and advertising
startup succeeded, and real UART `info`, `on`, `off`, `blink` tests passed.
The controller reported its HCI identity and the application reported active
advertising. The user subsequently confirmed seeing `NORA Dragon D25D` in
a Bluetooth scanner, establishing over-the-air advertising on this assembly.
The user also confirmed that it reappeared in the scanner after unplugging
and reconnecting the Pico, verifying advertising startup after a power cycle.
The current v2 adds a connectable GATT LED service and has been built,
programmed and verified. Its unchanged network controller is the same as v1.
The application starts without runtime errors; UART mode/state reads, interval
changes and rejection of out-of-range intervals passed, with invalid requests
leaving the previous setting unchanged. A dedicated 8 KiB libc allocation arena
supports GATT database-hash crypto, separate from the kernel heap. The user
confirmed that phone LED control works after connecting and following the
mode-write instructions, and subsequently confirmed blink-speed control after
the interval-write instructions. Disconnect/reconnect followed by another LED
command also passed. The user confirmed the subsequent power-cycle,
phone-reconnection and LED-command check as well. Phone state/interval reads
remain to be explicitly checked. USB, RF range, ADC and
power consumption remain untested. See ../../programming/BRINGUP.md.

References:

- [Zephyr Bluetooth samples and nRF5340 core pairing](https://docs.zephyrproject.org/latest/samples/bluetooth/bluetooth.html)
- [Zephyr HCI IPC controller](https://docs.zephyrproject.org/latest/samples/bluetooth/hci_ipc/README.html)
