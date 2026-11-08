# Pico UART console bring-up

Standalone nRF5340 secure application-core firmware, separate from the shared
P1 USB firmware. Uses the same first-page linker layout as ../blinky/ and
requires no SDK. Build from the repository root:

```sh
make -C square-p3/firmware/uart-console
```

Keep the SWD-only power wiring from ../../programming/README.md. With power
off, connect J3 pin 3 (P0.24 TX) to Pico GP5 (physical 7), and J3 pin 4
(P1.06 RX) to Pico GP4 (physical 6). Retain common ground. Keep the external
LED and 1 kΩ series resistor on J3 pin 13. UART is 115200 baud, 8N1, no
hardware flow control. Pin/register definitions were checked against Nordic
nrfx v3.2.0 `mdk/nrf5340_application{,_bitfields}.h`.

After backing up existing application flash and configuration, install with:

```sh
build/tools/openocd/bin/openocd -f square-p3/programming/pico-nrf53.cfg \
  -c init -c 'targets nrf53.cpuapp' \
  -c 'program build/square-p3-uart-console/console.hex verify reset exit'
```

This replaces the first application flash page. It does not write UICR,
network-core flash or request recovery/mass erase. The linker rejects images
over 4 KiB and any initialized or zero-initialized global RAM requirements.

The Pico exposes its UART as a USB serial port. On Linux, find it under
`/dev/serial/by-id/`. A terminal using Python's standard library is included:

```sh
python3 square-p3/firmware/uart-console/console.py /dev/ttyACM0
```

Type `help`, `info`, `on`, `off` or `blink`, followed by Enter. Ctrl-C exits
the host terminal. The host uses local line editing; the target does not echo
individual characters. It starts in blink mode, uses the internal high-frequency
clock and an approximately 500 ms LED interval. The polled single-byte DMA
receiver is intended for one human command at a time; do not stream commands
while replies are being transmitted. Invalid/overlong commands are rejected.

`--test` exercises the actual serial connection, command parsing and replies,
finishing in blink mode. It currently expects the first bench module's ID
`3804d25d-e462b092`. `--wait-startup` opens the port first and waits up to
60 seconds for a startup banner, allowing a separate SWD programming command.

Build passes with warnings treated as errors. The initial installation
attempt failed during processor examination before programming. The first
standalone blinky omitted CPU-side CTRL-AP disable keys, causing SWD memory
access to close after a power cycle even though UICR permits debugging. Both
sources now write the secure and non-secure runtime keys during startup;
UICR is not changed by firmware. The old OpenOCD CTRL-AP offset 0x0c check
does not establish full runtime access on this device: check AHB-AP CSW as
described in Nordic's nRF5340 product specification, Debug and trace.
After explicit approval, application-core recovery was performed, followed by
restoration of saved application flash outside page 0, original APPROTECT and
SECUREAPPROTECT configuration and the saved public Bluetooth address. The
console was installed and verified. A real Pico UART session passed startup,
device identity, help, LED on/off/blink, unknown-command and overlong-command
tests. After a user-confirmed physical power cycle, SWD memory access and all
UART command tests passed again. The first UART command encountered a pending
input error; the host smoke test now terminates any partial line before testing
fresh commands. This can also be cleared manually with Enter.

UICR verification emitted a checksum mismatch followed by a successful binary
comparison of all 16 restored bytes. The independently read configuration and
address matched the backup. See ../../programming/BRINGUP.md.
