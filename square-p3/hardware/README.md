# Assembly and ordering

## Population options

| Reference | Part | SWD only | USB |
|---|---|---|---|
| U1 | NORA-B106-00B | Fit | Fit |
| C1 | 4.7 µF, 10 V, X7R, 0805 | Fit | Fit |
| C2 | 100 nF, 16 V, X7R, 0805 | Fit | Fit |
| J2 | 1×5, 2.54 mm header | Optional/wires | Optional/wires |
| J3 | 1×14, 2.54 mm header | Optional/wires | Optional/wires |
| J1 | HRO TYPE-C-31-M-12 USB-C receptacle | Omit | Fit |
| U2 | XC6206P332MR-G, 3.3 V, SOT-23-3 | Omit | Fit |
| U3 | USBLC6-2SC6, SOT-23-6 | Omit | Fit |
| C3, C4 | 1 µF, 16 V, X7R, 0805 | Omit | Fit both |
| JP1 | Open solder bridge, no purchased part | Leave open | Bridge for USB power |
| R1, R2 | 5.1 kΩ, 1%, 0805; one per CC pin | Omit both | Fit both |
| SW1 | Normally-open 6 mm through-hole reset button | Optional | Optional |

C3 bypasses USB 5 V; C4 is the regulator output capacitor and remains connected
with JP1 open. C1/C2 decouple the target's separate 3.3 V rail. Choose capacitors
with adequate effective capacitance at operating voltage. Reflow the USB-C SMD contacts with the module and other SMD parts. Its shell
anchors, headers and optional switch can be iron-soldered afterwards. The
module's hidden pads cannot be assembled with an ordinary iron alone.

## Power

For SWD-only use, leave JP1 open and supply J2 pin 1 from an external regulated
3.3 V source (for example a debugger Pico's 3V3 OUT). Never use Pico VBUS/VSYS.
The module's VDD and VDDH pins all share 3.3 V, selecting normal-voltage mode.

For USB power, fit the complete USB group **including both CC resistors**,
bridge JP1, and disconnect the
external 3.3 V supply, including Pico 3V3 OUT. Keep debugger ground connected.
J2 pin 1 then supplies a target voltage reference/measurement point. Do not tie
two supplies together. If deliberately powering externally with the USB parts
fitted, keep JP1 open to isolate the regulator output. The board does not select
or OR supplies automatically. Never inject 5 V on a header or GPIO.

VBUS connects to the module's dedicated B9 pin, U2 input and U3 supply only.
Begin below about 100 mA total target/header load and verify regulator temperature.
The built bootloader/application each advertise 100 mA (bMaxPower=50 in 2 mA
units). USB-C does not increase this budget: the fixed CC pull-downs do not
detect or negotiate higher current, and regulator maximum current is not a
guaranteed usable GPIO power budget.

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

**J2/J3 match Minimal P1 exactly.** Compact P2 and revision D have different
GPIO headers. Use P1 firmware; SWO and the remaining GPIOs are not exposed.

## JLCPCB settings

Use `fabrication/nora-dragon-P3_2-gerbers.zip`:

- 2 layers, FR4, **40.5 × 49.5 mm, 1.6 mm thickness**, 1 oz copper.
- Standard plated vias, green mask, white silk. No assembly service.
- Lead-free HASL is the low-cost starting finish; ENIG is optional.
- No gold fingers, edge chamfer, controlled impedance or via filling.
- Mark on PCB: **None**. JLCPCB retired the old order-number placeholder in
  May 2026; the current board has that placeholder removed.
- Top stencil artwork is `fabrication/gerbers/nora-minimal-F_Paste.gtp`.
  Use a small frameless stencil for U1; see [stencil options](STENCIL.md). It is a separate order. Controlled small paste
  deposits can be used with reflow experience, but bridging hidden pads is hard
  to inspect or repair. The stencil is not required by the PCB manufacturer.

Minimum signal width/clearance is 0.18/0.155 mm, ordinary vias 0.6/0.3 mm.
Main target-power routing is 0.40 mm; USB supply routing is 0.25–0.30 mm. C2 (100 nF) is closest to U1; C1 is the
bulk capacitor below it. There are no open drilled vias in U1's
solder lands. The USB connector has plated slots plus non-plated locating holes;
keep both drill files in the upload and review the manufacturer's drill preview.
Do not substitute the old revision D's 0.8 mm order setting.

## Assembly and first checks

1. Compare the purchased connector with the manufacturer drawing linked in `../reference/SOURCES.md`. Check module
   orientation against the pin-1 mark and assembly image. The module footprint
   is rotated 90 degrees relative to the manufacturer's land pattern.
2. Inspect the bare board and solder the power capacitors/components first.
   With U1 absent, check for rail-to-ground shorts. For the USB build, bridge
   JP1 and verify approximately 3.3 V at J2 pin 1 using a current-limited supply.
   Remove power before fitting U1.
3. Reflow U1, including the six antenna-end ground pads. Follow the module's
   moisture/reflow instructions, especially for modules stored open.
4. Fit headers or wires and the four USB-C shell anchors (if fitted). Keep tall
   objects and metal at least 10 mm away from the antenna.
5. Recheck supply voltage and shorts; connect SWD ground first. Start with short
   wires and SWD at 1 MHz or slower. Follow `programming/README.md`.

An unprogrammed module need not enumerate over USB. This is a prototype:
static CAD validation cannot establish assembly yield or working USB/radio.

## Layout checks and limits

The manufacturer's antenna keepout is applied on both layers, with notches
for the designated ground pads. The module is centred on the board edge with
more than 10 mm of ground on the other three sides. Headers, the USB connector
and mounting-hole courtyards remain at least 10 mm from the antenna. Signal copper is excluded
from the bottom beneath the module. SWCLK routes around it; the antenna ground
row is protected against tracks and stitched at the empty K4/K6 positions.
Ground checking requires a continuous back ground plane and at least two vias
per top ground island.

Native USB is 12 Mbps full speed. Its main front pair is 1.25 mm wide with
0.16 mm gap over a protected back ground reference on nominal 1.6 mm FR4. This
is an approximate 90 ohm starting geometry, not a field-solver or measured
impedance guarantee. Short pad neckdowns and the post-ESD D− crossover use
narrower tracks; the crossover changes layer outside the paired section.
The board is not a USB compliance-tested product.

## Mounting, reset and size tier

Four 2.2 mm unplated holes suit optional M2 hardware. In the component-side
view, with the origin at the top-left:

| Hole | Centre (mm) |
|---|---|
| H1 | (3.5, 46) |
| H2 | (37, 46) |
| H3 | (3.5, 3.5) |
| H4 | (37, 3.5) |

Use M2 heads/spacers that fit inside the 4.4 mm footprint courtyards. The top
holes retain at least 10 mm of courtyard-to-antenna separation; oversized metal
washers or spacers would consume that clearance. Mounting is optional and has
no electrical connection.

SW1 is optional: a normally-open 6 mm through-hole pushbutton with 6.5 mm
spacing across its paired legs and 4.5 mm spacing between rows. Check the
purchased switch against `Breakout:SW_PUSH_6mm`. It grounds RESET_N while held;
release it to restart into the P1 firmware's USB recovery mode. No external
pull-up or capacitor is added; reset retains the module's internal pull-up.
Iron-solder this button, headers and USB-C shell anchors after SMD reflow. Omit SW1 to keep
the minimum assembly unchanged. The firmware guide describes normal power-on
recovery timeout versus a RESET_N reset.

The rectangular outline is 40.5 × 49.5 mm; board thickness remains 1.6 mm. The
USB-C socket body is centred at x=20.25 mm. Use the actual outline dimensions in a
quote. This still fits a 50 mm square tier and does not lower its base price.

The dragon and credit are white **B.Silkscreen** ink. No decorative copper or
mask cutouts are added. Green mask/white silk is the default low-cost choice;
other mask colours change the background of the same single-colour art.

## USB-C assembly details

Fit the exact **HRO TYPE-C-31-M-12** footprint, also identified as LCSC C165948.
A similar-looking USB-C socket may have a different land pattern. This connector
has 0.5 mm-pitch SMD signal contacts, four plated shell-anchor slots, and two
0.65 mm non-plated locating holes. Use the new paste file and keep both drill
files in the manufacturing ZIP. The socket lip overhangs the PCB by about
0.35 mm; the socket origin is (20.25, 46.2) mm. Its body no longer projects like
the old USB-A plug.

R1 connects **CC1 to GND** and R2 connects **CC2 to GND**, each 5.1 kΩ, 1%.
Do not join the CC pins together or omit one resistor for a USB build. Both
D+ contacts share USB_DP; both D− contacts share USB_DM. SBU1/SBU2 are unused.
The shell is connected to ground. No USB-PD/high-voltage circuit is present;
USB is for 5 V power, USB full-speed data and the installed recovery firmware.

The optional switch is through-hole; the USB-C contacts and CC resistors are
SMD and should be reflowed. Inspect the connector joints before powering the
board. Use a data-capable cable; a charger alone cannot upload firmware.

## Quick order selections

| Option | Selection |
|---|---|
| Material | Standard FR4 |
| Layers | 2 |
| Dimensions | 40.5 × 49.5 mm |
| Quantity | 5 for a small prototype order |
| Delivery format | Single PCB; 1 design |
| Thickness | 1.6 mm |
| Solder mask / silk | Green / white; keep front and back silk |
| Surface finish | Lead-free HASL |
| Outer copper | 1 oz |
| Via covering | Tented; no filling/capping |
| Gold fingers / castellations / edge plating | No |
| Controlled impedance | No |
| PCB assembly | No |
| Mark on PCB | None |

Keep ordinary electrical testing and other standard defaults. The four M2 holes
are ordinary non-plated holes, not countersunk/counterbored holes. USB-C shell
slots are plated and are already described in the drill files. Do not omit either
drill file or select a special hole/edge process for the mounting holes.

Stencil: quantity 1, top only, stainless steel, no frame, customized finished
size 100 × 100 mm, thickness 0.12 mm, no fiducials. Use the current F.Paste file;
see STENCIL.md for the suggested aperture remark. Compare shipping again after
selecting the small finished sheet. One stencil is reused for all the PCBs.

[JLCPCB's current marking guidance](https://jlcpcb.com/help/article/how-to-mark-on-pcb)
says no mark is added by default and order numbers are no longer offered from
May 2026. Do not add the former JLCJLCJLCJLC placeholder to new orders.
