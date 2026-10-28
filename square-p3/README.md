# NORA-B106 Square P3

**49.5 × 49.5 mm**, two layers, 1.6 mm FR4. This board fits inside a
50 × 50 mm manufacturing tier with 0.5 mm nominal margin. It restores twelve
GPIOs on a 1×14 header, spreads the USB parts out and adds four optional M2
mounting holes. Minimum assembly remains **U1 + C1 (4.7 µF) + C2 (100 nF)**.
Headers are optional; power the SWD-only build from regulated 3.3 V.

The routed native KiCad 9 PCB is authoritative. This revision derives from the
Backplane-assisted Minimal P1 circuit, with a new layout edited and routed using
KiCad's Python API. The back silkscreen carries the requested signature:
**Designed by Codex / with Backplane / for rain-1**.

- [Gerber ZIP](fabrication/nora-square-P3-gerbers.zip)
- [Assembly, pinouts and order settings](hardware/README.md)
- [Assembly drawing](preview/assembly.png) and [back signature](preview/back-labels.png)
- [Schematic](preview/nora-minimal.svg)
- [Top paste stencil Gerber](fabrication/gerbers/nora-minimal-F_Paste.gtp)
- [Stencil ordering and DIY options](hardware/STENCIL.md)
- [Pico/SWD and USB firmware installation](programming/README.md)
- [BOM](hardware/BOM.csv) and [validation](verification.md)

J2 and J3 have **exactly the same pinout as Minimal P1**. Use its existing
[built USB firmware](../minimal-p1/firmware/README.md); no new build or signing
key is required. The USB product name remains NORA Minimal P1. P2 and revision D
have different GPIO headers; use the P3/P1 pinout. The optional USB-A plug is
Same Sky UP2-AH-1-TH; it extends beyond the stated bare-PCB dimensions. Install
the recovery bootloader over SWD before trying USB communication/updates.

Open `nora-minimal.kicad_pro` in KiCad 9, keeping the local libraries alongside.
From this directory, run `make check`, `make fabrication` or `make firmware-check`.
The firmware check verifies shared P1 source/image hashes and electrical/header
compatibility, and runs its eight uploader tests. To change firmware, use the
P1 firmware build instructions. Earlier P1/P2/revision D files remain separate.

CAD and static firmware compatibility checks pass. **No assembled board,
SWD/USB session, GPIO/ADC or RF performance has been physically tested.**
The larger size adds working space; it does not lower the price relative to
P1/P2 within the same manufacturer's size tier. Shipping depends on the basket.
