# NORA-B106 Dragon P3.1

**38 × 49.5 mm**, two layers, **1.6 mm FR4**. The USB-A plug is centred on the
bottom edge. The board is 23% narrower than P3 and still fits inside a 50 × 50 mm
manufacturing tier. It retains twelve GPIOs and the P1-compatible J2/J3 pinout.
The directory name `square-p3/` is retained; its current PCB is rectangular P3.1.

Minimum assembly remains **U1 + C1 (4.7 µF) + C2 (100 nF)**. Headers and SW1 are
optional. Power the SWD-only build with regulated 3.3 V. The optional 6 mm
through-hole reset button makes USB recovery convenient without external reset
wires. Its footprint adds no required parts. Two optional M2 mounting holes are
at the bottom; mounting metal stays away from the antenna.

- [Current Gerber ZIP](fabrication/nora-dragon-P3_1-gerbers.zip)
- [Assembly, pinouts and order settings](hardware/README.md)
- [Front assembly drawing](preview/assembly.png)
- [Dragon on the back](preview/back-artwork.png) and [native silk preview](preview/back-labels.svg)
- [Schematic](preview/nora-minimal.svg)
- [Top paste stencil Gerber](fabrication/gerbers/nora-minimal-F_Paste.gtp)
- [Stencil ordering and DIY options](hardware/STENCIL.md)
- [Pico/SWD and USB installation](programming/README.md)
- [BOM](hardware/BOM.csv) and [validation](verification.md)

The USB protection device is closer to the plug, main target-power routes are
0.4 mm wide, the local 100 nF capacitor stays closest to the module, and both
layers retain continuous ground regions with 32 ground stitching vias. The
module's antenna keepout, six antenna-end grounds and back ground reference
are retained. No GPIO is loaded by an onboard LED.

The cyber dragon is **white back silkscreen**, as selected, with the Codex +
Backplane / rain-1 credit below it. It adds no exposed copper or solder-mask
openings. The [artwork source, vectors and generation prompt](artwork/README.md)
are included. This is artwork on the board, not a solder-paste stencil pattern.

The routed native KiCad 9 PCB is authoritative. P3.1 derives from the original
Backplane-assisted P1 circuit; this relayout uses native KiCad/Python edits.
J2/J3 retain **exactly P1's pinout**, so use the unchanged
[built P1 USB firmware](../minimal-p1/firmware/README.md). Its USB names still
say NORA Minimal P1. P2 and revision D use different GPIO headers.
The optional Same Sky UP2-AH-1-TH USB plug extends beyond the PCB dimensions.
Install its recovery bootloader over SWD before USB communication/updates.

Open `nora-minimal.kicad_pro` in KiCad 9 with its local libraries. Run
`make check`, `make fabrication` or `make firmware-check` here. The firmware
check verifies electrical/header compatibility and shared P1 source/image
hashes, then runs eight uploader tests. No separate P3.1 firmware build is needed.
Use P1's build instructions to change firmware, preserving its signing key.

CAD and static compatibility checks pass. **No board assembly, paste printing,
SWD/USB, GPIO/ADC or RF performance has been physically tested.** Earlier P3
files remain in Git history; P1/P2/revision D remain separate projects. The
narrower outline does not change pricing within the same size tier.
