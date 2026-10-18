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

Install current OpenOCD with CMSIS-DAP and nRF53 support. On Debian the starting
point is `sudo apt install openocd`. The config supports both the older
`target/nrf53.cfg` and newer `target/nordic/nrf53.cfg` script paths. If neither
exists, update OpenOCD; do not substitute `nrf52.cfg`.

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
