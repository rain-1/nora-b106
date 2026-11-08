# Control the LED from a phone

Use a BLE app that can connect and read/write characteristics, such as nRF
Connect for Mobile. Keep the existing Pico power and LED wiring. The module
runs the firmware itself; the Pico supplies power and the optional UART console.

1. Scan for **NORA Dragon D25D** and tap **Connect**.
2. Discover/expand the custom service with UUID
   `7b1e0001-8e2f-4f4a-9d6c-3a5b7c9d0100`.
3. Find the characteristic beginning **7b1e0002**. Its user-description
   descriptor says **LED mode: 00 off, 01 on, 02 blink**.
4. Tap its write control and select a **hexadecimal / byte-array** value,
   using **write with response**. Send `01` to turn the LED on, `00` to turn
   it off, or `02` to blink. These are single bytes, not ASCII strings.

The remaining UUID suffix is the same for every characteristic:
`-8e2f-4f4a-9d6c-3a5b7c9d0100`.

| UUID prefix | Function | Format |
|---|---|---|
| `7b1e0002` | Read/write LED mode | One byte: `00` off, `01` on, `02` blink |
| `7b1e0003` | Read/write blink interval | Two bytes, unsigned little-endian milliseconds, 50–5000 |
| `7b1e0004` | Read current state | Four bytes: mode, commanded LED output (0/1), interval low byte, interval high byte |

For example, write `64 00` to **7b1e0003** for a 100 ms interval, or `F4 01`
for 500 ms. Then write `02` to **7b1e0002** if it is not already blinking.
The interval is the time between LED transitions: 500 ms on + 500 ms off is
one complete cycle per second. Changing the interval does not change the mode.

Reading **7b1e0004** after turning the LED on at the default interval should
return `01 01 F4 01`. There are no notifications; tap Read again to refresh.
The output byte records the firmware's commanded pin state, not optical
feedback from the LED. State reads are consistent snapshots.

Mode writes must be exactly one byte; interval writes must be exactly two.
Invalid lengths, offsets or values are rejected without changing settings.
Writes do not alter flash. Mode and interval survive disconnection but reset
to blinking/500 ms on a power cycle. The last valid UART or Bluetooth command
wins. No bonding or authentication is required for this bench LED service.

Disconnect and reconnect to check that advertising resumes automatically.
If the app cached an older service list, refresh/discover services again.

The UART console provides `info`, `state`, `on`, `off`, `blink` and
`interval 50..5000` for diagnosis. `info` reports whether a phone is connected.
Successful Bluetooth writes also print their mode/interval to UART.

## Phone acceptance checks

- Connect and discover the service.
- Send `01`, then `00`, and observe the LED change.
- Set interval `64 00`, then mode `02`, and observe faster blinking.
- Read mode, interval and state and compare with the expected settings.
- Try mode `03` or interval `00 00`: the app should report a write error and
  the previous valid settings should remain.
- Disconnect, reconnect, and repeat a write.
- Power-cycle and confirm the name reappears and mode defaults to blinking.

See [Nordic's nRF Connect for Mobile overview](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-mobile)
for the app's characteristic read/write support. Labels and icons differ
between Android and iOS releases.
