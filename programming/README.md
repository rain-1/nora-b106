# First tests with a Raspberry Pi Pico

This is a low-cost CMSIS-DAP route to try, **not a hardware-tested combination
in this project**. The NORA-B106 uses a dual-core nRF5340; use software with
nRF53 support, not an nRF52 target file. The manufacturer's documented supported
programmer route is SEGGER J-Link. Keep that as a fallback if your particular
Pico firmware/tool version cannot attach or recover this device.

## Set up the Pico

Use the official Raspberry Pi `debugprobe_on_pico.uf2` release for an RP2040
Pico, or `debugprobe_on_pico2.uf2` for Pico 2. Hold BOOTSEL while connecting the
Pico by USB and copy the matching UF2 onto its USB drive. Do not use the
`debugprobe.uf2` image intended for the separate Debug Probe accessory.

Firmware and instructions:
https://github.com/raspberrypi/debugprobe/releases/tag/debugprobe-v2.3.1
https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html

## OpenOCD version requirement

**Debian 13's packaged OpenOCD 0.12.0 does not support the nRF5340. Installing
`openocd` from its standard repositories is insufficient for these steps.**
Use a newer OpenOCD binary and the scripts installed with that same build;
copying just `nrf53.cfg` into an old installation is insufficient because the
flash driver also needs nRF53 support. Do not substitute `nrf52.cfg`.

One source-build route on Debian 13 is below. This pins the upstream source
revision inspected for this project; it installs under the ignored `build/`
directory and does not replace the system OpenOCD. From the project root:

```sh
sudo apt install build-essential git autoconf automake libtool pkg-config \
  texinfo libusb-1.0-0-dev libhidapi-dev libjim-dev libssl-dev
git clone https://github.com/openocd-org/openocd.git build/tools/openocd-src
git -C build/tools/openocd-src checkout 2893f940012e19cda8ccb6038766b0d77f26bd0e
(
  cd build/tools/openocd-src
  ./bootstrap
  ./configure --prefix="$(pwd)/../openocd" \
    --enable-cmsis-dap --enable-cmsis-dap-v2 --disable-werror
  make -j2
  make install
)
export PATH="$PWD/build/tools/openocd/bin:$PATH"
openocd --version
```

For non-root USB access, install the upstream device rules once, then unplug
and reconnect the Pico:

```sh
sudo install -m 644 build/tools/openocd-src/contrib/60-openocd.rules \
  /etc/udev/rules.d/60-openocd.rules
sudo udevadm control --reload-rules
```

If the source checkout already exists, skip `git clone`. Reapply the PATH line
in each new terminal. Check the target configuration without connecting to
hardware:

```sh
openocd -f programming/pico-nrf53.cfg -c 'noinit; echo [target names]; shutdown'
```

This should list `nrf53.cpuapp` and `nrf53.cpunet`. It proves that the installed
binary can parse the target/flash-driver configuration, not that a Pico can
program a physical module. The project config accepts both the older
`target/nrf53.cfg` and newer `target/nordic/nrf53.cfg` script locations.
Upstream [build instructions](https://github.com/openocd-org/openocd/blob/2893f940012e19cda8ccb6038766b0d77f26bd0e/README.md)
and the [Debian 13 package version](https://packages.debian.org/trixie/openocd)
document the two installation routes. SEGGER J-Link remains the manufacturer's
supported alternative.

In this workspace, that pinned OpenOCD revision has also been built locally at
`build/tools/openocd/bin/openocd`, with build dependencies extracted under
`build/tools/openocd-deps/` rather than installed system-wide. The offline
configuration check passed for both cores. These ignored local binaries are
not included in Git or the project ZIP; use the build recipe on a fresh
checkout. No USB adapter or target was connected during this check.

## Wire the target

Connect GND first, then signals, with power removed while wiring.
The Pico pins here refer to the **debugger Pico**, not its own three debug pads.

| Debugger Pico | Physical pin | Carrier |
|---|---|---|
| GND | 3, or another GND | J2 pin 2, GND |
| GP2 | 4 | J2 pin 3, SWCLK |
| GP3 | 5 | J2 pin 4, SWDIO |
| GP1 | 2 | J2 pin 5, RESET_N; optional initially |
| 3V3 OUT | 36 | J2 pin 1 **only in the SWD-only assembly, with U2/J1 omitted** |

For the USB assembly, power the target through its USB connector and leave
Pico 3V3 OUT disconnected. Both variants use 3.3 V signalling. Do not connect
Pico VBUS/VSYS to this 3.3 V header. The Pico firmware has no target voltage
measurement, so verify the rail with a multimeter before connecting signals.

For UART later: J3 pin 3 (target P1.12 TX) goes to Pico GP5 (RX, physical 7),
and J3 pin 4 (target P1.13 RX) goes to Pico GP4 (TX, physical 6). Your firmware
must first configure these target pins as UART.

## Read-only identification

From the project root:

```sh
openocd -f programming/pico-nrf53.cfg \
  -c 'init; targets nrf53.cpuapp; halt; mdw 0x00FF0204 3; shutdown'
```

This attempts to halt the application core and read its FICR device-ID words
and part code. It does not erase or program flash. The CPU remains halted;
power-cycle afterward to restart existing firmware. Successful attach/read
shows that power and basic SWD communication work; it is not a complete
functional test of both cores.

## Blink the LED without building firmware

Fit D1/R3 and run:

```sh
openocd -f programming/pico-nrf53.cfg -f programming/led-test.cfg
```

The script uses the secure GPIO alias to blink P0.20 six times while halted,
then restores that pin's prior configuration/output. It writes only GPIO
registers, not flash, UICR, or protection settings. It requires unlocked secure
application-core access. With existing firmware that changes security/ownership,
this test may be unavailable even if the board is healthy. If access is denied,
check wiring, supply voltage, adapter firmware, and protection state first.

**Do not blindly run recover/mass erase.** nRF53 recovery can erase both cores
and UICR, including manufacturer production data such as the stored Bluetooth
address. Back up accessible flash/UICR before destructive operations, and use
the manufacturer's recovery/identity-restoration procedure if recovery is
actually necessary. None of the provided scripts performs recovery.

## First standalone firmware

`firmware/blinky/` is a small Zephyr application source, using P0.20 active high
and the internal LF RC clock. It has not been compiled in this workspace: no
Zephyr/nRF Connect SDK is installed. In a current configured Zephyr/Nordic SDK
workspace, a starting build command is:

```sh
west build -b nrf5340dk/nrf5340/cpuapp \
  /absolute/path/to/nora-b106-board/firmware/blinky \
  -d build-nora-blinky
```

The DK target supplies the SoC/memory configuration; `app.overlay` replaces
its LED0 pin. Verify the resolved devicetree has P0.20 active high and that the
build selected LF RC, not a 32 kHz crystal, before flashing. This is a blinky
bring-up shortcut, not a full board definition. The source does not enable
USB or Bluetooth. Those need their own firmware, and Bluetooth also needs
the correct network-core image.

With the correct secure application ELF built for this module and after
reviewing what it will overwrite, OpenOCD's basic programming form is:

```sh
openocd -f programming/pico-nrf53.cfg \
  -c 'program build-nora-blinky/zephyr/zephyr.elf verify reset exit'
```

This last command **does program flash**. Do not use RP2040 UF2 application
binaries on the NORA module, or assume J-Link-only `nrfjprog` works through a
Pico. The Pico's USB port is the debugger connection; the carrier's USB-C
connector is the target's separate native USB peripheral.

## Native USB firmware updates

The USB hardware does not provide flashing by itself. A USB-capable bootloader
must first be configured and programmed through SWD, and applications must use
its flash layout. MCUboot's USB CDC ACM serial recovery is one option. Its
`CONFIG_BOOT_SERIAL_PIN_RESET` option can make the existing RESET button select
recovery, without a second button or GPIO jumper. This bootloader configuration
has not yet been built or tested for this carrier; `firmware/blinky/` does not
include it. Keep SWD available for debugging and bootloader recovery.
See [Nordic's serial recovery documentation](https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/app_dev/bootloaders_dfu/mcuboot_serial_recovery.html).
