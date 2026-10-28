# NORA-B106 Compact P2

**31.5 × 27.5 mm**, two layers, 1.6 mm FR4: about **35% less PCB area** than
Minimal P1. This is the smaller four-GPIO revision, derived from the P1 circuit
and checked module footprint. Its routed KiCad 9 PCB is authoritative.
Minimal P1 and revision D remain separate projects.

Minimum assembly is still **U1 plus C1 (4.7 µF) and C2 (100 nF)**, with external
regulated 3.3 V and SWD wires. Headers are optional. The module's 82 hidden LGA
pads need controlled reflow/hot-plate assembly. All other SMD parts remain
0805 or SOT-23; there are no smaller passive packages in this revision.

Optional USB uses the same through-hole Same Sky UP2-AH-1-TH USB-A male plug,
regulator, protection device and two extra capacitors. Fit the whole USB group,
bridge JP1 and disconnect external 3.3 V when powering through USB. Install the
USB bootloader through SWD first; the built firmware then provides USB serial
GPIO/ADC commands and USB application updates. Use **P2 firmware and pinouts**.
The USB plug extends beyond the board; 31.5 × 27.5 mm describes the PCB itself.

- [Assembly, pinouts and JLCPCB settings](hardware/README.md)
- [Gerber ZIP](fabrication/nora-minimal-P2-gerbers.zip)
- [Top stencil layer](fabrication/gerbers/nora-minimal-F_Paste.gtp)
- [Assembly drawing](preview/assembly.png)
- [Schematic](preview/nora-minimal.svg)
- [Built USB firmware and installation](firmware/README.md)
- [Pico/SWD wiring](programming/README.md)
- [BOM](hardware/BOM.csv) and [validation](verification.md)

Open `nora-minimal.kicad_pro` in KiCad 9. Libraries are project-relative. Run
`make check` or `make fabrication` for CAD validation/exports; use
`make firmware-setup`, `make firmware`, `make firmware-check` for firmware.
Read the hardware/programming guides before making power connections.

The new J3 has **six pins**: 3V3, GND, P0.24, P1.06, P0.20 and P0.07/AIN3.
J2 retains its original five-pin SWD pinout. No on-board LED/button is needed;
RESET_N is on J2 and P0.20 can drive an external LED through a resistor.
GPIO functions such as UART/I2C are firmware choices; this build uses USB for
its console and leaves all four GPIOs as floating inputs until commanded.

The compact layout retains more than 10 mm ground beyond the module's three
non-antenna sides, the antenna keepout, a continuous back ground plane, and
at least two vias in each front ground island. Clearance is at least 0.155 mm
and copper-to-edge clearance at least 0.4 mm. These also accommodate the stated
6 mil spacing / 15 mil edge rules of OSH Park's two-layer service; review its
upload/DFM preview and total price before ordering. No supplier quote is included.

CAD checks and firmware builds/static checks pass. **No assembled P2 board,
Pico programming session, USB link/update, ADC measurement or RF performance
has been physically tested.** The native PCB is authoritative; operation scripts
under the ignored build directory are not a regeneration source.
