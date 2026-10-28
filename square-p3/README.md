# NORA-B106 Dragon P3.2 — USB-C

**40.5 × 49.5 mm**, two layers, **1.6 mm FR4**. The USB-C socket is centred
on the bottom edge and all **four M2 mounting holes** are present. This is
slightly wider than P3.1 to keep the top mounting hardware clear of the antenna,
and still fits within a 50 × 50 mm size tier. The directory name `square-p3/`
is retained; these are the current P3.2 files.

Minimum assembly remains **U1 + C1 (4.7 µF) + C2 (100 nF)**. Headers, USB and
SW1 are optional. Power the SWD-only build from regulated 3.3 V. The optional
6 mm through-hole reset button makes USB recovery convenient without an extra
reset wire. It adds no required components.

- [Current USB-C Gerber ZIP](fabrication/nora-dragon-P3_2-gerbers.zip)
- [Assembly, pinouts and order settings](hardware/README.md)
- [Front assembly drawing](preview/assembly.png)
- [Dragon on the back](preview/back-artwork.png) and [native silk preview](preview/back-labels.svg)
- [Schematic](preview/nora-minimal.svg)
- [Top paste stencil Gerber](fabrication/gerbers/nora-minimal-F_Paste.gtp)
- [Small frameless stencil options](hardware/STENCIL.md)
- [Pico/SWD and USB installation](programming/README.md)
- [BOM](hardware/BOM.csv) and [validation](verification.md)

USB uses the **HRO TYPE-C-31-M-12** sixteen-contact USB 2.0 receptacle. Its
contacts are SMD and its four shell anchors are through-hole. CC1 and CC2 each
have their own **5.1 kΩ, 1%, 0805** pull-down resistor. Both D+ contacts are
joined, and both D− contacts are joined, supporting either cable orientation.
SBU1/SBU2 remain unconnected. This is a 5 V USB device: no USB-PD controller,
higher-voltage negotiation, USB host or USB 3 data function is implemented.
Use a data-capable A-to-C or C-to-C cable to a computer for programming/console.

The module, twelve GPIOs, power isolation jumper, protection device and reset
button retain the P1-compatible electrical interfaces. Use the unchanged
[built P1 USB firmware](../minimal-p1/firmware/README.md); USB product names
still say NORA Minimal P1. Install the bootloader through SWD first. Press and
release SW1 to enter USB recovery after that installation. P2 and revision D
have different GPIO headers; use this project's pinout guide.

The native KiCad 9 PCB is authoritative. Module/SWD/GPIO routing was retained;
the connector area was rerouted. The antenna keepout, six antenna-end grounds,
continuous back ground beneath U1, local 100 nF capacitor and 0.4 mm main power
routes are retained. The white back-silkscreen cyber dragon and Codex/Backplane
credit add no decorative copper or solder-mask openings. [Artwork](artwork/README.md)
includes the original generated source, cleaned vectors and prompt.

Open `nora-minimal.kicad_pro` with its local libraries. Run `make check`,
`make fabrication` or `make firmware-check` here. Checks include the USB-C pad
mapping, separate CC pull-downs, unchanged firmware-facing interfaces and shared
P1 artifact hashes, plus eight uploader tests. No firmware rebuild is required.

CAD/static checks pass. **No PCB assembly, paste transfer, SWD/USB, GPIO/ADC
or RF performance has been physically tested.** Older P3/P3.1 files are in Git
history; current order files use **P3.2**. P1/P2/revision D remain separate.
