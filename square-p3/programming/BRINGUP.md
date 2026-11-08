# First physical bring-up — 2026-11-08

One user-assembled square-p3 board, populated with U1/C1/C2 only, has been
tested with a Raspberry Pi Pico 2 W running the official
`debugprobe_on_pico2.uf2` v2.3.1 release. The target is powered by Pico 3V3 OUT
through J2 with JP1 open. Target supply measured 3.3 V by the user.

OpenOCD commit `2893f940012e19cda8ccb6038766b0d77f26bd0e` was built locally
under the repository's ignored build directory. SWD at 1 MHz identified the
nRF5340 application core and read its device ID. The user observed the
six-blink GPIO register test on J3 pin 13 through a 1 kΩ series resistor and
external LED. Standalone blinky was then programmed and verified; the user
confirmed that it blinked after power cycling.

The initial standalone blinky omitted the CPU-side CTRL-AP disable keys.
After power cycling, it ran normally but application AHB-AP memory access was
blocked. UICR still allowed debug; that alone is insufficient. The old
OpenOCD offset-0x0c status check did not detect the runtime restriction.
Both standalone sources now write `0x50FA50FA` to the secure and non-secure
CPU-side CTRL-AP disable registers during startup, without changing UICR.

Before the initial blinky install, application flash (1 MiB), application
UICR (4 KiB) and application FICR (4 KiB) were backed up with SHA-256 hashes.
The application UICR backup contains the original public Bluetooth address
at offsets 0x100/0x104. Key-slot descriptors were erased; the key-data window
is not treated as restorable configuration.

With explicit user approval, **application-core-only** CTRL-AP recovery was
performed to restore debug access. The corrected UART console replaced page 0;
the saved flash contents outside page 0 were restored. Original application
APPROTECT/SECUREAPPROTECT values and the public Bluetooth address were restored
and verified. No network-core erase or programming was requested. Network flash
and UICR were not backed up, so their contents have not been independently
verified. FICR is read-only and was not written.

UART wiring: J3 pin 3/P0.24 TX to Pico GP5/physical 7; J3 pin 4/P1.06 RX to
Pico GP4/physical 6, with existing common ground. A real 115200 8N1 session
received the console startup banner and correct device ID. Automated host
commands passed `help`, `info`, LED `on`, `off`, `blink`, unknown-command and
overlong-input checks, ending in blink mode. SWD access worked after a soft
reset. After a user-confirmed physical power cycle, SWD read the correct
device ID and the full UART command test passed again. The first UART command
reported a pending input error; terminating the partial line cleared it.
The host test now sends a line terminator before exercising fresh commands.

## Bluetooth advertising firmware

Both cores' original flash and documented factory/configuration registers are
now backed up. The network flash backup is 256 KiB; the documented UICR
register span is 0x380 bytes and FICR is 0x400 bytes. Reading a full 4 KiB
network UICR window failed beyond its readable range; that partial read is
not used as the documented configuration backup. The address in network
UICR+0x300 matched the original application UICR+0x100 address. Backup hashes
are recorded separately in `network-manifest.json`.

Separate Zephyr v4.4.0 application and network images were built using ARM
GCC 14.2.1 and custom NORA board definitions. The network image uses Zephyr's
standard HCI IPC controller. Both use LF RC; the application calibrates it
and sets the module HFXO load to 20 pF. Both follow UICR for runtime debug
access. Images were audited to contain code flash only, with matching IPC
RAM and the established UART/LED mapping.

Initial programming exposed a core sequencing issue: IPC startup timed out,
and an application reflash with the network core still active stalled the
flash algorithm. A normal reset and holding the network core off allowed
application programming and verification to complete. The final flash script
clears the network debug trap/halt request and holds the network core off
while programming application code, then starts the application normally.
No mass erase or configuration programming was performed for BLE installation.
The final flashing script passed a complete fresh installation and UART test.
Independent readback of both complete code images, including padding, matched
byte-for-byte. Application configuration/OTP and the documented network UICR
were independently read back and matched their original backups.

The application then successfully initialized Bluetooth through the network
controller and reported active non-connectable advertising as
`NORA Dragon D25D`. Zephyr reported random static identity
`EF:3C:52:09:85:42`; the saved manufacturer public address is not the active
on-air identity. Real UART `info`, LED `on`, `off` and `blink` tests passed.
The user subsequently confirmed seeing the board in a Bluetooth scanner,
establishing over-the-air advertising on this assembly. The user then
unplugged and reconnected the Pico and confirmed the board reappeared in
the scanner, verifying advertising startup after a physical power cycle.
The development computer reported no available Bluetooth controller, so it
could not independently scan the advertising packets.

## Phone LED control (BLE v2)

The application now advertises a connectable custom GATT service,
`7b1e0001-8e2f-4f4a-9d6c-3a5b7c9d0100`. Characteristics with prefixes
`7b1e0002`, `7b1e0003` and `7b1e0004` respectively expose read/write mode,
read/write little-endian blink interval and a readable consistent state.
Mode is 0/off, 1/on or 2/blink; the interval is 50–5000 ms per transition.
Bluetooth and UART share mutex-protected LED state. No pairing is required;
only the test LED is controlled. Advertising is scheduled again after the
connection object is recycled following disconnection.

The v1 code images and validation metadata were saved under
`build/square-p3-ble/advertising-v1/` before the update. The network image is
unchanged. An initial GATT database-hash calculation exposed a zero-size libc
allocation arena; setting a dedicated 8192-byte arena fixed that runtime
error. The corrected v2 application built without compiler warnings and was
programmed/verified without an erase-all or UICR operation. It starts cleanly
and reports active connectable advertising.

Real UART tests passed on, off, state snapshots, interval 100 ms, rejection
of 49 ms and 5001 ms without state changes, restoration of 500 ms and blink.
The user confirmed that phone LED control works after connecting and following
the GATT mode-write instructions. The user also confirmed blink-speed control
after the 100 ms/500 ms interval-write instructions. The user then confirmed
disconnect/reconnect followed by another LED command, verifying automatic
advertising restart and renewed control. The user also confirmed the requested
Pico power-cycle, phone reconnection and LED-command check. State/interval
reads remain to be explicitly checked. The laptop still has no available Bluetooth
adapter for an independent central-role test.

## Bluetooth application updates (board 3702)

The user assembled and flashed a second minimum board, application ID
`038d3702-15454c2d`, using NEXT_BOARD.md, and confirmed its LED/phone controls.
Its original per-core backups are under `build/bringup-backups/board-02-original/`.
An additional current application flash/UICR backup was taken before OTA
provisioning under `build/bringup-backups/038d3702-15454c2d-before-ota/`.

Separate ../firmware/ble-ota/ builds MCUboot and the LED application with
MCUmgr's Bluetooth SMP transport. MCUboot uses ECDSA P-256, validates the
primary image and uses swap using offset. Application flash is partitioned
as 64 KiB boot, 448 KiB primary, 452 KiB secondary and 60 KiB reserved storage.
Both signed versions 1.0.0 and 1.0.1 passed layout/header/vector/signature
checks. Offline verification rejected a deliberately corrupted image.

Initial SWD provisioning installed the bootloader and confirmed 1.0.0 after
an identity check. Only application code/slots were erased/programmed.
Configuration readback matched the backup, and network-controller code and
documented UICR matched their prior contents. No recovery/mass erase, network
programming or UICR writes were performed. The first board D25D was not
provisioned with OTA during this session.

Before the phone upload, signed 1.0.1 was staged using SWD and requested for
test using UART. It booted unconfirmed and started Bluetooth. The next reboot
without confirmation reverted to confirmed 1.0.0 and restored Bluetooth.
The secondary was then cleared for the actual phone test.

The user downloaded `nora-ota-1.0.1.signed.bin` from a temporary local file
server and completed the Bluetooth upgrade through nRF Connect Device Manager.
Captured UART showed MCUboot starting v1.0.1. Independent `bootstatus` then
reported **1.0.1 confirmed=yes**; info and LED on/off/blink commands passed.
A further UART reboot kept **1.0.1 confirmed=yes** and restarted advertising.
The temporary file server was stopped after completion. Physical power
interruption during upload/swap has not been tested.

OTA updates the application only; the radio firmware and bootloader remain
fixed. The bench signing key is intentionally shared development material,
separate from P1 USB signing. The app does not self-confirm: the phone confirms
a successful test boot. See ../firmware/ble-ota/README.md for future updates.

The UART, blinky, BLE and BLE OTA sources are under ../firmware/; the shared P1 USB
bootloader/application artifacts remain unchanged. Bench backups and recovery
artifacts are under ignored `build/bringup-backups/` and
`build/square-p3-uart-console/recovery/` at the repository root. Keep an
additional copy of the original backups outside this working tree.

These tests establish basic operation and over-the-air Bluetooth advertising
on one assembly. Bluetooth connections/range, USB, ADC, other GPIOs, power
consumption and assembly repeatability
remain untested.

References:

- [Nordic debug protection requirements](https://docs.nordicsemi.com/r/bundle/ps_nrf5340/page/debugandtrace.html)
- [Nordic CTRL-AP recovery](https://docs.nordicsemi.com/r/bundle/ps_nrf5340/page/ctrl-ap.html)
- [u-blox address backup and restoration](https://content.u-blox.com/sites/default/files/Using-Public-IEEE-Address-From-UICR_AppNote_UBX-19055303.pdf)
