# NORA Compact P2 USB firmware

Built for the **new Compact P2 board**, with the J3 pinout in `../hardware/README.md`.
Use this firmware only on Compact P2. Minimal P1 and revision D have different
J3 pinouts. P2 has distinct USB IDs and a separate development signing key.

The package contains a compiled MCUboot USB CDC ACM recovery bootloader and a
compiled USB serial shell application. Both run on the nRF5340 application core.
The network core stays off; no Bluetooth/network-core firmware is programmed.
No physical board, USB enumeration, ADC accuracy or SWD session has been tested.

## First install over SWD

Fit the complete USB population (U1/C1/C2 plus J1/U2/U3/C3/C4), close JP1,
power through USB, and leave Pico 3V3 OUT disconnected. Keep the debugger's
GND/SWCLK/SWDIO connected. See `../programming/README.md` for the exact Pico
pins and the required nRF53-capable OpenOCD; Debian 13 OpenOCD 0.12.0 is too old.

From the **project root**, using that newer OpenOCD:

```sh
openocd -f programming/pico-nrf53.cfg \
  -c 'init; targets nrf53.cpuapp; program firmware/dist/nora-factory.hex verify reset exit'
```

This command writes application-core flash. Inspect/back up existing accessible
firmware/UICR before overwriting a module containing data you want to keep.
There is no mass erase/recover command here. The factory HEX has no UICR,
network-core flash, storage or secondary-slot records. It preserves the factory
Bluetooth identity storage; it does not prove that any pre-existing firmware
itself can safely be overwritten for your use case.

Power-cycle after programming. Normal startup exposes a recovery USB port for
**8 seconds**, then disconnects/re-enumerates as the application serial port.
After a reset through RESET_N, recovery stays active until commanded to reset.
An invalid/missing application also leaves recovery active.

## Talk to the board

Linux should provide `/dev/ttyACM*`. The tty number can change between recovery
and the application; find it with:

```sh
python3 -m pip install pyserial
python3 -m serial.tools.list_ports -v
python3 -m serial.tools.miniterm /dev/ttyACM0 115200
```

The 115200 setting is a host convention for native USB, not the USB bus speed.
Open the **application** port after the 8-second window; press Enter for `nora>`.
Use your existing venv if your distribution restricts system pip, or the prepared
`build/firmware/venv/bin/python` instead of `python3`. Miniterm exits with Ctrl-].

| Command | Result |
|---|---|
| `nora info` | Firmware version, uptime and device ID |
| `nora pins` | J3 pinout |
| `nora input 3 none` | Set J3 pin 3 as a floating input |
| `nora input 3 up` | Input with internal pull-up (`down` also supported) |
| `nora read 3` | Read J3 pin 3 |
| `nora write 5 1` | Drive J3 pin 5 / P0.20 high |
| `nora write 5 0` | Drive that pin low |
| `nora adc` | Read J3 pin 6 / P0.07 / AIN3, reporting raw and mV |
| `nora dfu` | Reboot and remain in USB recovery |
| `nora reboot` | Reboot normally, including the 8-second recovery window |

GPIO numbers in commands are **J3 header pin numbers**, not Nordic GPIO numbers.
Only J3 pins 3–6 are accepted; power, SWD and reset pins cannot be driven by
these commands. All four GPIOs start as floating inputs; outputs change only
on an explicit write command. Keep external voltages in 0–3.3 V and disconnect
conflicting external drivers before commanding an output. An external LED can
use J3 pin 5 → 1 kohm → LED anode, cathode → GND. There is no automatic blink.

`nora adc` temporarily disconnects the digital input and restores its prior
input/pull state. It refuses to read if J3 pin 6 is configured as an output;
use `nora input 6 none` first. The ADC conversion scale is not a guarantee that
pins tolerate voltages above VDD. The ADC path has not been calibrated or tested.

## Update over USB

Close other terminals using the port. On Linux x86_64 an Apache `mcumgr` binary
is available locally under `host-tools/linux-amd64/`. A fresh Git checkout
builds it with `python3 firmware/tools/install_mcumgr.py` (no system Go install
required); the large host executable is not tracked in Git. The helper needs only Python plus
pyserial and checks the expected image header/vectors and USB device before
invoking it. From the project root:

```sh
build/firmware/venv/bin/python firmware/tools/usb_update.py \
  --enter --port /dev/ttyACM0 firmware/dist/nora-app.signed.bin
```

`--enter` sends `nora dfu` to the application, identifies the recovery device
on the same physical USB connection, uploads the image and resets. The uploader
uses the standard MCUboot SMP serial protocol through Apache mcumgr. It never
issues a mass erase or recover operation. It refuses an ambiguous port choice.
The bootloader verifies the application signature before booting it.

To enter recovery manually, run `nora dfu` and close the terminal. Find the new
recovery tty and run the same upload command **without `--enter`**. You can also
briefly connect RESET_N (J2 pin 5) to GND with an external button/wire, then
release it. If the application is broken and no reset wire is fitted, power-cycle
with the uploader ready and contact the recovery port within the 8-second
window. Any valid mcumgr request in that window keeps recovery active.

Recovery port: VID:PID `2fe3:0006`, product `NORA Compact P2 recovery`.
Application port: `2fe3:0007`, product `NORA Compact P2 console`.
These are bench prototype identifiers using Zephyr's sample VID. Obtain suitable
identifiers before distributing a finished USB product.

This first version updates the application core only. It does not update the
bootloader, radio/network core or factory configuration over USB. Initial
installation, debugger access and bootloader replacement remain SWD operations.
A USB upload directly replaces the primary image; this is recovery-oriented
bring-up, not a power-failure-safe rollback system. If an upload is interrupted,
re-enter recovery and upload the valid signed image again.

## Build or change the firmware

The installed build environment is project-local under `build/firmware/`.
A fresh Linux x86_64 environment needs git, uv, make, a host C compiler and xz.
No system packages or shell profiles are changed by the setup script.

```sh
make firmware-setup
make firmware
make firmware-check
```

Setup pins Zephyr v4.4.0 (`684c9e8f32e4373a21098559f748f06915f950c9`), its
manifest-pinned MCUboot and modules, Zephyr SDK 1.0.1 (ARM GNU compiler only),
and the Python packages in `requirements-build.lock`. SDK downloads are checked
against pinned SHA-256 hashes. The pinned MCUboot uses the legacy USB stack for
recovery, while the application uses Zephyr's newer USB stack. Upstream emits
legacy-stack deprecation notices and shared-register DT alias warnings; these
are not suppressed. There are no custom C compiler warnings in this build.

Edit `usb_bringup/src/main.c` for application behaviour, and bump
`usb_bringup/VERSION` for a new image version. `make firmware` builds both images,
signs the application, creates a factory HEX, audits resolved GPIOs/clocks/
partitions/vectors, verifies the signature and runs uploader tests. Upload the
new `.signed.bin` for later application changes. Keep the signing key paired
with the already-installed bootloader; a different key requires SWD reinstall.

`keys/development.pem` is deliberately included as a **shared development key**
so this bench board can be rebuilt and updated. It is not a production secret or
a production security boundary. Do not enable readback protection or erase the
module's UICR as part of this bring-up procedure.

## Artifacts and validation

- `dist/nora-factory.hex`: bootloader + signed application for initial SWD install.
- `dist/nora-app.signed.bin`: subsequent USB updates.
- `dist/nora-app.signed.hex`: signed app at its flash address.
- `dist/nora-bootloader.hex`: bootloader only; preserve matching app/key.
- `.elf` files: debugger symbols; the application ELF alone is not an install image.
- `dist/manifest.json`: versions, source hashes and artifact SHA-256 hashes.
- `dist/validation.json`: static checks, flash ranges and header pin mapping.

Flash layout: bootloader 0x00000–0x2ffff (192 KiB), primary app
0x30000–0x8ffff (384 KiB), reserved secondary 0x90000–0xeffff (384 KiB),
storage 0xf0000–0xfffff (64 KiB). Both images use calibrated LF RC and runtime
20 pF HFXO load configuration, following the NORA-B1 data sheet. No external
32.768 kHz crystal is assumed and no DK LEDs/buttons/serial pins are inherited.

The bootloader uses about 56 KiB flash; the application uses about 79 KiB
flash and 20 KiB RAM. Build/static validation is complete; run the physical
power, SWD, USB re-enumeration/update and GPIO loopback tests before relying on it.
This package does not establish a working RF link or test the network core.
