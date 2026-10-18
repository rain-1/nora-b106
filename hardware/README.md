# NORA-B106 breakout, revision D

A 36 x 36 mm, two-layer carrier for a **soldered NORA-B106-00B**. Order bare
PCBs and assemble locally. This is a prototype design: the CAD checks pass,
but no physical PCB, USB link, RF performance, or Pico-to-NORA session has
been tested yet. It is not a reusable socket fixture for testing loose modules.

## Choose one assembly option

| Part group | Minimum SWD build | USB build |
|---|---|---|
| U1 NORA-B106 | Fit | Fit |
| C2 4.7 uF / 10 V X7R; C3 100 nF / 16 V X7R | Fit | Fit |
| J2, 1x5 SWD header | Fit, or solder wires | Fit, or solder wires |
| J3, 1x14 GPIO/power header | Optional | Optional |
| D1 green LED and R3 1 kohm | Recommended for testing | Recommended for testing |
| SW1 reset switch | Optional | Optional |
| J1 USB-C; U2 regulator; U3 ESD; R1/R2 5.1 kohm; C1 1 uF; C4 100 nF | **Omit all** | **Fit all** |

The smallest SWD version needs only the module, two capacitors, and a few wires
or a header. Use the Pico's **3V3 OUT** to supply J2 pin 1 in this variant.

For the USB version, power the carrier through USB and leave the Pico's 3V3
wire disconnected. J2 pin 1 then exposes the regulated target supply for
measurement or a debugger's voltage reference. **Do not connect two 3.3 V
supplies together or inject 3.3 V into the fitted regulator's output.** Add
USB by fitting the whole USB group later, not just the connector. USB-C is a
5 V USB 2.0 device connection; it does not negotiate USB-PD.

All resistors, capacitors, and the LED are 0805. U2 is SOT-23-3 and U3 is
SOT-23-6. U1 has 82 hidden LGA pads, so it needs controlled reflow/hot-plate
assembly. It cannot be soldered to this board with an iron along its edges.

## Order settings for JLCPCB

Upload `fabrication/nora-b106-breakout-revD-gerbers.zip` and use:

- 2 copper layers, FR4, **0.8 mm thickness**, 1 oz copper.
- Green solder mask, white silkscreen; standard through-hole vias.
- Lead-free HASL is the low-cost starting finish; ENIG is optional.
- No assembly, via filling, blind/buried vias, or controlled-impedance service.
- Inspect the uploaded outline: **36 x 36 mm**. The USB connector's mouth
  overhangs the bottom edge slightly.
- Select "Specify a location" for the order number if offered and use the
  `JLCJLCJLCJLC` location on the back, away from solder lands.
- A top paste stencil is useful for the hidden module pads. Quote it separately;
  the ZIP includes the top paste artwork. Review the stencil process with your
  paste/reflow setup rather than assuming it is included in the PCB price.

There is no firm price estimate: quantity, shipping, finish, stencil, and parts
supplier dominate a small order. The same board supports the smaller BOM above.
The minimum copper/space is 0.15 mm; ordinary vias are 0.6 mm diameter / 0.3 mm
finished drill. The design uses no paid via-in-pad process. Do not select 1.6 mm
without reviewing the USB geometry.

## Pinout

Both headers use 2.54 mm pitch. Pin 1 has a square pad; all pinout directions
are shown from the component side in the assembly image.

| J2 pin | Signal | Module pad |
|---|---|---|
| 1 | 3V3 supply / voltage reference | A7, B7, A8 |
| 2 | Ground | All module ground pads |
| 3 | SWCLK | J2 |
| 4 | SWDIO | H2 |
| 5 | RESET_N | J3 |

| J3 pin | Signal | Module pad |
|---|---|---|
| 1 | 3V3 | A7, B7, A8 |
| 2 | Ground | All module ground pads |
| 3 | P0.18 | E1 |
| 4 | P0.15 | D1 |
| 5 | P0.31 | J9 |
| 6 | P1.11 | H9 |
| 7 | P1.15 | F9 |
| 8 | P1.05 | E9 |
| 9 | P1.12, suggested UART TX | G8 |
| 10 | P1.13, suggested UART RX | G9 |
| 11 | P0.04 / AIN0 | D8 |
| 12 | P0.05 / AIN1 | E8 |
| 13 | P1.02, suggested I2C SDA | B4 |
| 14 | P1.03, suggested I2C SCL | A3 |

Revision D consolidates all twelve GPIOs and power onto one continuous J3
header on the right edge. **Its pinout differs from revisions A–C.** The
separate five-pin SWD header J2 remains on the left with its original pinout.
Pin 1 is the square pad, at the top when viewing the component side with the
antenna at the top and USB connector at the bottom. J3 is optional: fit a
standard 1x14, 2.54 mm-pitch pin header with a 2.54 mm-wide body, or solder wires
to its holes. No additional surface-mount components are required for the GPIOs.

The UART/I2C roles are firmware choices, not fixed connections. I2C pull-ups
must be added externally when needed. GPIO is **3.3 V only, not 5 V tolerant**.
P0.20 (module A5) drives D1 through R3, active high. SW1 grounds RESET_N;
the module provides its reset pull-up. SWO and the other GPIO are not exposed.

## Assemble and check

1. Inspect the bare board under magnification. Confirm the module's A1 marker
   against the assembly drawing. Its antenna faces the top edge; **the module
   footprint is rotated 90 degrees** relative to the manufacturer's top-view
   land pattern. The antenna has six additional ground pads which must solder.
2. Fit C2/C3 and the chosen power components. Before fitting U1, check for a
   supply-to-ground short. In the USB build, test at 5 V through a current-limited
   USB supply and measure approximately 3.3 V at J2 pin 1. Never put USB 5 V on
   J2 pin 1 or a GPIO. Remove power before fitting the module.
3. Apply controlled paste deposits or use a stencil and reflow U1 using the
   module's specified profile. Follow the manufacturer's MSL/reflow guidance,
   especially for modules that have been stored open. No open drilled vias
   are placed in U1's solder lands.
4. Fit the headers, optional LED/resistor, and reset switch. The reset switch
   footprint is for a 6 mm tactile switch with 6.5 x 4.5 mm pin spacing. Use
   the exact USB-C **HRO TYPE-C-31-M-12** land pattern; similarly named USB-C
   connectors can have different peg/shell geometry.
5. Check the supply again, then connect SWD ground first. For the first attempt
   keep the wires short and use 1 MHz or slower SWD. See `programming/README.md`.

D1 is a GPIO test LED, not a power indicator. It will stay off until driven by
firmware or the supplied SWD register test. An unprogrammed module need not
enumerate over USB; that alone is not a fault.

## Design decisions and limits

- VDD (A7/B7) and VDDH (A8) share 3.3 V, selecting normal-voltage mode.
  VBUS (B9) gets USB 5 V only in the USB build. No software setting is needed
  to make the GPIO voltage 3.3 V in this supply mode.
- Both USB-C CC pins have independent 5.1 kohm pull-downs. USB DP/DM go to the
  module's C9/D9 pins through the two channels of USBLC6-2SC6, whose I/O pins
  are also connected by PCB copper. No USB-to-serial bridge is fitted.
- USB has a via-free route and a 0.70 mm / 0.15 mm paired section over a
  protected bottom ground plane. With a nominal 0.8 mm, 1 oz FR4 board this is
  an approximate 90-ohm starting geometry. Pad neckdowns are narrower, and
  the actual laminate/impedance has not been measured or field-solver
  validated. This is a **12 Mbps full-speed prototype**, not a certified USB
  layout or a high-speed USB board.
- The antenna keepout is on both copper layers. Small notches allow only the
  designated M2/M8 antenna ground pads and their short ground connections.
  Ground extends over 10 mm beyond the other three module sides. Keep metal,
  cables, and fingers away from the antenna during RF tests. The RF design
  still needs a real radio check after assembly.
- Revision D retains the revision B routing of SWCLK around the right side of
  the module and reserves
  the antenna ground row against signal tracks. Ground vias at the empty K4
  and K6 positions connect that row directly to the back plane. A separate
  track keepout reserves the back copper under the module as ground; SWDIO,
  RESET_N, and P1.13 route outside it. There are 39 ground stitching vias,
  with at least two in every separate piece of top-layer ground copper.
- Supply tracks are 0.30 mm where clearance permits, with 0.18 mm sections
  retained between closely spaced pads and tracks. The intended initial load
  remains below about 100 mA.
- The external low-frequency crystal pins are unused. Select the internal LF
  RC clock in firmware. The module provides its own high-frequency clock.
- The regulator's 200 mA family rating is not a promise of 200 mA usable header
  current. Start with the module and light GPIO loads; keep total 3.3 V load
  below about 100 mA for initial bench use and verify regulator temperature.
- This checks only parts of the module in the first SWD/LED test. A later
  full functional test should exercise the application and network cores,
  flash/RAM, GPIO, native USB firmware, and a known-good Bluetooth peer.

## Files and verification

Open `nora-b106-board.kicad_pro` in KiCad 9. Footprints and the module symbol are
project-local under `hardware/`; tables use `${KIPRJMOD}`. The schematic and PCB
are the delivered design. `tools/generate_board.py` records initial placement,
footprint derivation, and preroutes; it does **not** reproduce the finished route
by itself. Do not regenerate over the routed PCB. Future direct edits should
preserve the existing schematic UUIDs and PCB connectivity.

The export script reruns schematic ERC and PCB DRC with schematic parity, then
checks the module ground reference with `tools/check_module_ground.py`, then
exports Gerbers and separate plated/non-plated drill files. All checks must
pass before a new ZIP is made. Reports and source hashes are in
`fabrication/reports/` and `fabrication/manifest.json`. These are static checks,
not evidence that physical hardware has worked.

References and component sources are listed in `reference/SOURCES.md`.
