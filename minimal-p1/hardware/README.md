# Assembly and ordering

## Population options

| Reference | Part | SWD only | USB |
|---|---|---|---|
| U1 | NORA-B106-00B | Fit | Fit |
| C1 | 4.7 µF, 10 V, X7R, 0805 | Fit | Fit |
| C2 | 100 nF, 16 V, X7R, 0805 | Fit | Fit |
| J2 | 1×5, 2.54 mm header | Optional/wires | Optional/wires |
| J3 | 1×14, 2.54 mm header | Optional/wires | Optional/wires |
| J1 | Same Sky UP2-AH-1-TH USB-A plug | Omit | Fit |
| U2 | XC6206P332MR-G, 3.3 V, SOT-23-3 | Omit | Fit |
| U3 | USBLC6-2SC6, SOT-23-6 | Omit | Fit |
| C3, C4 | 1 µF, 16 V, X7R, 0805 | Omit | Fit both |
| JP1 | Open solder bridge, no purchased part | Leave open | Bridge for USB power |

C3 bypasses USB 5 V; C4 is the regulator output capacitor and remains connected
with JP1 open. C1/C2 decouple the target's separate 3.3 V rail. Choose capacitors
with adequate effective capacitance at operating voltage. The connector and
headers can be iron-soldered after reflow; the module's hidden pads cannot.

## Power

For SWD-only use, leave JP1 open and supply J2 pin 1 from an external regulated
3.3 V source (for example a debugger Pico's 3V3 OUT). Never use Pico VBUS/VSYS.
The module's VDD and VDDH pins all share 3.3 V, selecting normal-voltage mode.

For USB power, fit the complete USB group, bridge JP1, and disconnect the
external 3.3 V supply, including Pico 3V3 OUT. Keep debugger ground connected.
J2 pin 1 then supplies a target voltage reference/measurement point. Do not tie
two supplies together. If deliberately powering externally with the USB parts
fitted, keep JP1 open to isolate the regulator output. The board does not select
or OR supplies automatically. Never inject 5 V on a header or GPIO.

VBUS connects to the module's dedicated B9 pin, U2 input and U3 supply only.
Begin below about 100 mA total target/header load and verify regulator temperature;
the family maximum current is not a guaranteed usable GPIO power budget.

## Pinouts

Component side, antenna at the top and USB at the bottom: pin 1 is the square
pad at the top of each header. Headers are optional. GPIO is 3.3 V and not
5 V tolerant. Firmware chooses UART/I2C/etc.; add I2C pull-ups externally.

| J2 | Signal |
|---|---|
| 1 | +3V3 supply/reference |
| 2 | GND |
| 3 | SWCLK |
| 4 | SWDIO |
| 5 | RESET_N |

| J3 | Signal | Module pad |
|---|---|---|
| 1 | +3V3 | A7/B7/A8 |
| 2 | GND | Ground |
| 3 | P0.24 | H1 |
| 4 | P1.06 | G1 |
| 5 | P0.17 | F1 |
| 6 | P0.18 | E1 |
| 7 | P0.15 | D1 |
| 8 | P0.10 | C1 |
| 9 | P0.08 | B1 |
| 10 | P0.12 | A2 |
| 11 | P1.03 | A3 |
| 12 | P1.00 | A4 |
| 13 | P0.20 | A5 |
| 14 | P0.07 / AIN3 | D3 |

**This new J3 pinout differs from the original revision D board.** J2 keeps
its original pinout. SWO and the other GPIOs are not exposed.

## JLCPCB settings

Use `fabrication/nora-minimal-P1-gerbers.zip`:

- 2 layers, FR4, **36.5 × 36.5 mm, 1.6 mm thickness**, 1 oz copper.
- Standard plated vias, green mask, white silk. No assembly service.
- Lead-free HASL is the low-cost starting finish; ENIG is optional.
- No gold fingers, edge chamfer, controlled impedance or via filling.
- If offered, put the order number at `JLCJLCJLCJLC` on the back.
- Top stencil artwork is `fabrication/gerbers/nora-minimal-F_Paste.gtp`.
  A stencil is helpful for U1; it is a separate order. Controlled small paste
  deposits can be used with reflow experience, but bridging hidden pads is hard
  to inspect or repair. The stencil is not required by the PCB manufacturer.

Minimum signal width/clearance is 0.18/0.15 mm, ordinary vias 0.6/0.3 mm.
Power routing is generally 0.30 mm. There are no open drilled vias in U1's
solder lands. The USB connector has plated slots plus non-plated locating holes;
keep both drill files in the upload and review the manufacturer's drill preview.
Do not substitute the old revision D's 0.8 mm order setting.

## Assembly and first checks

1. Compare the purchased connector with the manufacturer drawing linked in `reference/SOURCES.md`. Check module
   orientation against the pin-1 mark and assembly image. The module footprint
   is rotated 90 degrees relative to the manufacturer's land pattern.
2. Inspect the bare board and solder the power capacitors/components first.
   With U1 absent, check for rail-to-ground shorts. For the USB build, bridge
   JP1 and verify approximately 3.3 V at J2 pin 1 using a current-limited supply.
   Remove power before fitting U1.
3. Reflow U1, including the six antenna-end ground pads. Follow the module's
   moisture/reflow instructions, especially for modules stored open.
4. Fit headers or wires and any optional through-hole connector. Keep tall
   objects and metal at least 10 mm away from the antenna.
5. Recheck supply voltage and shorts; connect SWD ground first. Start with short
   wires and SWD at 1 MHz or slower. Follow `programming/README.md`.

An unprogrammed module need not enumerate over USB. This is a prototype:
static CAD validation cannot establish assembly yield or working USB/radio.

## Layout checks and limits

The manufacturer's antenna keepout is applied on both layers, with notches
for the designated ground pads. The module is centred on the board edge with
more than 10 mm of ground on the other three sides. Signal copper is excluded
from the bottom beneath the module. SWCLK routes around it; the antenna ground
row is protected against tracks and stitched at the empty K4/K6 positions.
Ground checking requires a continuous back ground plane and at least two vias
per top ground island.

Native USB is 12 Mbps full speed. Its main front pair is 1.25 mm wide with
0.15 mm gap over a protected back ground reference on nominal 1.6 mm FR4. This
is an approximate 90 ohm starting geometry, not a field-solver or measured
impedance guarantee. Short pad neckdowns and the post-ESD D− crossover use
narrower tracks; the crossover changes layer outside the paired section.
The board is not a USB compliance-tested product.
