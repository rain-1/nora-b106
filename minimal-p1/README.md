# NORA-B106 minimal breakout, prototype P1

A new 36.5 × 36.5 mm, two-layer board designed using Backplane's KiCad IPC
and sketch router. It prioritises SWD, twelve unloaded GPIOs, and optional
native USB. It is a soldered carrier, not a socket for testing loose modules.
The original revision D project is separate and unchanged.

**Minimum assembly: U1 NORA-B106, C1 4.7 µF and C2 100 nF.** Headers are
optional; wires can be soldered to the through-hole pads. Power from a
regulated 3.3 V supply through J2 pin 1 and connect its ground to J2 pin 2.
The module has 82 hidden LGA pads and needs controlled reflow/hot-plate
assembly. It cannot be soldered only along its edges with an iron.

For USB later, fit J1, U2, U3, C3 and C4 and bridge JP1. The connector is a
**Same Sky UP2-AH-1-TH through-hole USB-A male plug**, not a generic USB socket.
Use the exact mechanical pattern. An ordinary USB-A extension cable can
reduce strain on the computer port and board. The connector overhangs the
bottom edge; its outline is shown in the assembly image.

- [Assembly options, pinouts and JLCPCB settings](hardware/README.md)
- [Pico/SWD bring-up](programming/README.md)
- [Bill of materials](hardware/BOM.csv)
- [Assembly drawing](preview/assembly.png)
- [Schematic](preview/nora-minimal.svg)
- [Fabrication package](fabrication/nora-minimal-P1-gerbers.zip)
- [Validation](fabrication/reports/) and [source hashes](fabrication/manifest.json)

Open `nora-minimal.kicad_pro` in **KiCad 9**. This working copy was exported
from Backplane's pinned KiCad 10.99 fork and passes ERC, DRC, parity and module
ground checks. Its routed PCB is authoritative in this repository. The original
Backplane native files are retained under `backplane-source/` for provenance;
the downgrade removes only footprint gate-swap unit metadata, with no pads,
nets or copper removed. Do not edit both copies independently. Project-local
symbol snapshots keep ERC independent of the installed stock-library revision.

Run `make check` for CAD checks and `make fabrication` to regenerate exports.
Use `/usr/bin/python3` with Debian's pcbnew module for the board audits.
`make firmware-setup`, `make firmware` and `make firmware-check` handle the
separate firmware workflow. Backplane itself, its private profile and build
SDKs are not committed.

The design has no on-board LED or reset button. J2 exposes RESET_N (the module
has its own pull-up); an external momentary button can connect it to ground.
J3 exposes P0.20 for an external LED and resistor. Native USB is a peripheral,
not an automatic programmer: install a suitable bootloader through SWD first.
The [USB recovery and serial GPIO/ADC firmware](firmware/README.md) has been
compiled and statically checked; its physical operation remains untested. No assembled hardware, USB enumeration, radio performance or
Pico programming session has been physically tested.

The delivered routed PCB is authoritative. Scripts in the lab's `bridge/`
record individual design operations and are not a safe regeneration script.
Do not rerun placement/import scripts over the completed board.
