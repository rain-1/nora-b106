# Standalone SWD LED smoke test

For square-p3 with U1/C1/C2 and an external LED on J3 pin 13 (P0.20):
pin 13 → 1 kΩ → LED anode; cathode → GND. Use the power and SWD wiring
in ../../programming/README.md. This does not use the USB firmware or bootloader.

Build from the repository root with the Debian ARM bare-metal compiler:

```sh
make -C square-p3/firmware/blinky
```

The secure application-core image starts at address zero and blinks continuously
using the reset-default CPU clock and an approximate software delay. No USB,
radio, interrupts, external LF crystal, or SDK is used. Only P0.20 is configured.
The linker limits the image to the first 4 KiB flash page and asserts that no
RAM initialization is needed. The network core remains off after power-on.

Before programming, back up accessible application flash/UICR and any factory
identity data. With the project's newer OpenOCD, from the repository root:

```sh
build/tools/openocd/bin/openocd -f square-p3/programming/pico-nrf53.cfg \
  -c init -c 'targets nrf53.cpuapp' \
  -c 'program build/square-p3-blinky/blinky.hex verify reset exit'
```

This overwrites the first application flash page, replacing existing startup
code. It contains no UICR/network-core records and does not request recovery
or mass erase. Keep the original backup outside Git. After programming,
power-cycle and check that blinking starts without an OpenOCD connection.

This smoke test is separate from the unchanged shared P1 USB firmware.

Startup writes the CPU-side non-secure and secure CTRL-AP disable keys to
`0x50FA50FA`, preserving development SWD access after power cycling when UICR
allows debugging. These are runtime register writes, not UICR writes. The
first bench image omitted these keys: it blinked successfully, but lost SWD
memory access after power cycling. Do not flash that earlier build. The
corrected source builds successfully. The UART console, which contains the
same fix, was installed through approved application-core recovery and tested
over UART and SWD. See ../../programming/BRINGUP.md for results and pending checks.
