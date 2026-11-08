# Bluetooth application updates — Dragon P3

This is a separate MCUboot + MCUmgr build of the phone LED application. It
uses the same board, Pico power/SWD/UART wiring and working network-core
controller as ../ble/. Only the **application core** is updatable over
Bluetooth; network firmware, MCUboot and UICR remain outside this update path.
The shared P1 USB firmware is unchanged.

The first OTA target is the second board, `038d3702-15454c2d`, advertising as
**NORA Dragon 3702**. Its pre-OTA application flash and configuration are
backed up under `build/bringup-backups/038d3702-15454c2d-before-ota/` at the
repository root. The first board remains on its previous LED firmware until
separately provisioned.

## Phone update

Use **nRF Connect Device Manager**, not the legacy nRF Device Firmware Update
app. Disconnect any BLE scanner/LED-control connection first: the board accepts
one connection at a time.

1. Copy `build/square-p3-ble-ota/dist/nora-ota-1.0.1.signed.bin` to your phone.
2. Open Device Manager, scan and select **NORA Dragon 3702**.
3. Open its firmware-upgrade screen and select that **signed `.bin`** file.
4. Select **Test and Confirm** and start the upgrade. This uploads into the
   secondary slot, requests a test boot, reboots, reconnects and confirms the
   running image. The network-core image is not part of the file.
5. Keep power connected during the first test. The local swap/reboot test took
   about **13 seconds** before Bluetooth returned. If the app offers a swap-time
   setting, allow at least 20 seconds.
6. After completion, check that the image list reports **1.0.1**, active and
   confirmed. You can also read Firmware Revision in the standard Device
   Information Service or type `bootstatus`/`info` on UART.
7. Check LED control, then power-cycle and confirm version 1.0.1 remains active.

Do not upload the `.factory.hex`, `.confirmed.bin`, old application ELF or a
network image. The unpadded `.signed.bin` is the Bluetooth update file.
The application does not automatically confirm itself; Device Manager must
confirm a successful test boot. If left unconfirmed, the next reset reverts
to the previously confirmed image. Reversion requires a reset; there is no
automatic hang watchdog in this bench application. `confirm` on UART is an
explicit fallback for confirming an image you have checked.

### Optional local phone download

To serve just a copy of the signed file over your LAN, from the repository root:

```sh
python3 square-p3/firmware/ble-ota/serve_update.py --bind YOUR_COMPUTER_LAN_IP
```

Open the printed URL in your phone's browser on the same Wi-Fi, save the file,
then choose it in Device Manager. The server serves a dedicated copied-update
directory, not the key/source/backup directories. Ctrl-C stops it; it also
stops automatically after an hour. Your IP can change between sessions.
If your Wi-Fi isolates clients, transfer the signed file by USB or your usual
file-transfer method instead.

## Initial Pico provisioning

This is for a board **already running the working BLE host/controller pair**.
For a new assembly, follow ../../programming/NEXT_BOARD.md first, including
its original per-module backups. Never copy another module's identity.

Build and validate both versions before initial installation:

```sh
python3 square-p3/firmware/ble-ota/build.py --version 1.0.0
python3 square-p3/firmware/ble-ota/build.py --version 1.0.1
```

After saving a fresh copy of the current application's flash/UICR, install
the baseline on the identified board:

```sh
export NORA_EXPECT_DEVICE_ID=038d3702-15454c2d
build/tools/openocd/bin/openocd -f square-p3/programming/pico-nrf53.cfg \
  -f square-p3/programming/ota-install.cfg
```

Use the other board's **own full ID** if provisioning it separately. The
script checks the actual ID before programming and refuses a mismatch.
It erases application flash **0x00000–0xf0fff**, installs MCUboot and a
confirmed primary 1.0.0 image, verifies it, then restarts. The secondary slot
starts empty. It does not erase-all, program network flash or write UICR;
the reserved storage at 0xf1000 is also left untouched. Keep the original
backup: installing this layout replaces the previous direct-boot application.

The Pico remains useful for power, UART diagnostics and recovery. Ordinary
future application changes use Bluetooth and do not need another SWD install.
Replacing MCUboot, its signing key, the partition layout or the radio image
still requires SWD and the corresponding build changes.

## Build environment and signing

The build shares the project-local Zephyr v4.4.0 checkout and GNU ARM compiler
environment under `build/ble-*`. MCUboot is manifest-pinned to
`ee39e2d694bd827ffd1bebbce2f571a9154e6ec2`. Fresh setup:

```sh
python3 square-p3/firmware/ble-ota/setup.py
```

Subsequent versions can be built with, for example:

```sh
python3 square-p3/firmware/ble-ota/build.py --version 1.0.2
```

The version is used in the signed image header, UART output and Bluetooth
Device Information firmware revision. The build generates and verifies the
ECDSA P-256 signature, audits layout/debug/clock settings and image vectors,
then produces per-version manifests and a sparse factory HEX. It does not
flash a board. Never change partition addresses/sizes for an update intended
for an already installed bootloader.

`keys/development.pem` is a deliberately shared **bench development key**,
separate from P1's USB key. It is not a production security boundary. Keep it
paired with these bootloaders: changing the key means an SWD bootloader
reinstallation. The update service currently allows unpaired connections;
signature verification authenticates accepted images only relative to that
shared development key. Production keys/access policy are a separate task.

## Flash layout

| Region | Start | Size |
|---|---:|---:|
| MCUboot | `0x00000` | 64 KiB |
| Primary application | `0x10000` | 448 KiB |
| Secondary application | `0x80000` | 452 KiB |
| Reserved storage | `0xf1000` | 60 KiB |

Both MCUboot and application use **swap using offset**. The secondary has an
extra 4 KiB sector; the uploaded image normally begins at **0x81000**. MCUmgr
and MCUboot manage this offset; do not manually prepend a page to the update
`.bin`. The running application has a 0x200-byte signed header and vectors at
0x10200. Both slots, bootloader and storage fit in the 1 MiB application flash.

## Diagnostics and tests

Existing `info`, `on`, `off`, `blink`, `interval` and `state` commands remain.
OTA adds:

| UART command | Meaning |
|---|---|
| `bootstatus` | Runtime version, confirmation status, slot offsets |
| `confirm` | Explicitly confirm the running test image |
| `reboot` | Restart through MCUboot |
| `otatest` | Request a test boot of an already staged secondary image; does not upload or reboot |

Build/layout/signature checks passed for 1.0.0 and 1.0.1. Offline verification
rejected a deliberately corrupted image. Initial SWD installation booted
confirmed 1.0.0, started Bluetooth and passed UART LED/state/interval checks.
A signed 1.0.1 image staged through SWD was test-booted using the UART command;
it ran unconfirmed and started Bluetooth. Rebooting without confirming reverted
to confirmed 1.0.0 and restored Bluetooth. The test secondary was then erased,
leaving confirmed 1.0.0 ready for the phone upload. Readback confirmed factory
configuration and the network-controller code are unchanged.

The user then completed the actual 1.0.1 Bluetooth upload using Device Manager.
UART independently verified version **1.0.1 active and confirmed**, and LED
on/off/blink still worked. A subsequent UART reboot retained confirmed 1.0.1
and restarted Bluetooth. The local download server was stopped after transfer.
This establishes the real phone-to-board application update path on board 3702.
Power-interruption testing during upload/swap has not been performed.

References:

- [Zephyr OTA update overview](https://docs.zephyrproject.org/latest/services/device_mgmt/ota.html)
- [Nordic Device Manager](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-Device-Manager)
- [Nordic Test and Confirm flow](https://academy.nordicsemi.com/?nds_version_content=nrf-connect-sdk-intermediate-lesson-9-exercise-5-fota-over-bluetooth-low-energy-v3-1-0-v3-0-0)
