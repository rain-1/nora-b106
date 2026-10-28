# NORA-B106 board workspace

**Latest design: [Dragon P3.1](square-p3/README.md), 38 × 49.5 mm, twelve GPIOs,
SWD and centred optional through-hole USB-A.** This rectangular update keeps
1.6 mm thickness and fits within a 50 × 50 mm tier. It adds an optional reset
button, two bottom M2 holes, a white cyber dragon and the Codex / Backplane
credit. Minimum assembly remains the module and two capacitors.
Use its [current Gerber ZIP](square-p3/fabrication/nora-dragon-P3_1-gerbers.zip),
[ordering/pinout guide](square-p3/hardware/README.md) and
[small-stencil guidance](square-p3/hardware/STENCIL.md).
It keeps P1's exact electrical pinout and uses the existing P1 USB firmware;
see the [programming guide](square-p3/programming/README.md) and
[dragon preview](square-p3/preview/back-artwork.png).
CAD and static firmware compatibility checks pass; hardware remains untested.
Run `make -C square-p3 fabrication` for validation and exports.

**Latest compact design: [Compact P2](minimal-p2/README.md), 31.5 × 27.5 mm,
four GPIOs, SWD and optional through-hole USB-A.** This uses 35% less PCB area
than Minimal P1, with the same minimum assembly of the module and two capacitors.
Use its [Gerber ZIP](minimal-p2/fabrication/nora-minimal-P2-gerbers.zip),
[pinout/ordering guide](minimal-p2/hardware/README.md) and
[matching built USB firmware](minimal-p2/firmware/README.md).
Its six-pin GPIO header differs from both earlier designs. The USB bootloader
needs an initial SWD installation. CAD and firmware checks pass; hardware is
physically untested. Run `make -C minimal-p2 fabrication` for its validation and
exports. Earlier projects below are retained separately.

Revision D is a 36 x 36 mm two-layer NORA-B106 breakout for self assembly.
It exposes SWD, twelve GPIOs, optional USB-C power/data, an LED, and reset.

- [Assembly options, pinouts, and JLCPCB settings](hardware/README.md)
- [Pico programmer wiring and first tests](programming/README.md)
- [Parts list with SWD-only / USB population choices](hardware/BOM.csv)
- [Bare-PCB Gerber ZIP](fabrication/nora-b106-breakout-revD-gerbers.zip)
- [Assembly drawing](fabrication/preview/assembly-top.png)
- [Schematic preview](fabrication/preview/nora-b106-board.png)

CAD validation passed with zero ERC, DRC, unconnected-item, or schematic-parity
issues. The hardware and programmer connection have not been physically tested.
Revision D groups all twelve GPIOs plus 3V3/GND on a single 14-pin header
along the right edge, with SWD on the left. J3 has a new pinout; see the wiring
guide. The module ground-plane improvements are retained. Use the revision D Gerbers; earlier
revisions are retained in Git history. Debian 13's packaged OpenOCD is too old for the Pico route;
the programming guide provides a newer source build and an offline check.
For the lowest part count, start with the SWD-only population and power it from
a Pico's 3V3 OUT, following the wiring guide. The USB population uses its own
regulator; do not connect Pico 3V3 in that configuration.

## Minimal P1: new Backplane-designed board and USB firmware

[Minimal P1](minimal-p1/README.md) is a separate 36.5 × 36.5 mm design with a
minimum SWD population of the module and two capacitors, twelve unloaded GPIOs,
and an optional through-hole USB-A plug. Its **1.6 mm thickness and J3 pinout
are different from revision D**. All ordering, pinout and firmware instructions
for it are under `minimal-p1/`; do not mix its files with revision D.

The P1 project opens in KiCad 9. Built MCUboot USB recovery and USB serial
GPIO/ADC test firmware, including an initial SWD factory image and subsequent
USB update image, are in [minimal-p1/firmware](minimal-p1/firmware/README.md).
The USB bootloader must first be installed via SWD. CAD checks, firmware builds
and static checks pass; neither board nor USB/SWD has been physically tested.

```
make -C minimal-p1 check
make -C minimal-p1 firmware-setup
make -C minimal-p1 firmware
```

## Install on this machine

This workspace targets Debian 13's KiCad 9 packages. Run in your terminal:

```sh
sudo apt update
sudo apt install kicad kicad-symbols kicad-footprints kicad-templates
make doctor
```

The `kicad` package includes the GUI applications, `kicad-cli`, and the Python
`pcbnew` board API. Use `/usr/bin/python3` for board scripts so Debian's Python
modules are available. Optional 3D component models can be installed with
`sudo apt install kicad-packages3d`.

## Project workflow

Open `nora-b106-board.kicad_pro` in KiCad 9 to review the schematic and routed PCB. Keep `.kicad_pro`, `.kicad_sch`,
`.kicad_pcb`, custom symbols, custom footprints, and library tables together.
Reference project libraries through `${KIPRJMOD}` so they remain portable.

```sh
make doctor          # Verify the installed tools and libraries
make ipc-status      # Inspect the PCB currently open in the editor
make check           # Schematic ERC and board DRC; violations fail the command
make preview         # Schematic and PCB layer SVGs for inspection
```

Reports go into `build/reports/` and SVGs into `build/preview/`. These generated
files and KiCad's local UI state are ignored by Git. The Git repository is
hosted at https://github.com/rain-1/nora-b106.

The default filenames are `nora-b106-board.kicad_sch` and
`nora-b106-board.kicad_pcb`. Override them when necessary:

```sh
make check SCHEMATIC=hardware/main.kicad_sch BOARD=hardware/main.kicad_pcb
```

I can edit native project files, use Python for PCB changes, inspect exports,
and run checks through the CLI. For direct file edits, close the relevant editor
first and reopen afterward so unsaved GUI state does not overwrite changes.
Electrical connectivity, footprint pin mappings, RF layout, and manufacturing
constraints still need review against the component datasheets; ERC and DRC
alone do not establish that a design is correct.

## Live PCB connection and agent skill

The official IPC API is enabled in this machine's KiCad 9 preferences. The
previous configuration is backed up at
`~/.config/kicad/9.0/kicad_common.json.before-live-api`. Missing standard symbol
and footprint library tables were initialized from KiCad's bundled tables.

The local `.venv` contains `kicad-python==0.4.0`, tested against the installed
KiCad 9.0.2. Its API definitions report version 9.0.3 and its compatibility check
passes. Newer API methods may still require a newer KiCad release. To recreate
this environment:

```sh
uv venv --python /usr/bin/python3 --system-site-packages .venv
uv pip install --python .venv/bin/python -r requirements-kicad.txt
```

Open the intended PCB in KiCad, then run `make ipc-status`. This reads the board
path, footprints, and item counts without changing the design. For a specific
board or socket:

```sh
.venv/bin/python tools/kicad_ipc.py --board /path/to/board.kicad_pcb
.venv/bin/python tools/kicad_ipc.py --socket /tmp/kicad/api.sock
```

Live edit scripts can import `connect_board` from `tools.kicad_ipc`. Supply the
expected board path before editing; the helper rejects a different open file.
Multiple sockets require an explicit choice. Use the board's commit API for
undoable changes and save before running file-based exports or checks. KiCad 9
IPC supports the PCB editor, not the schematic editor. Modal dialogs can block
API requests; close them before retrying.

The project skill lives at `.agents/skills/nora-kicad/SKILL.md` and is linked
into this machine's Codex skills directory. It can be invoked as `$nora-kicad`
and is scoped to work in this workspace. No third-party MCP server is needed.

Integration was verified on the disposable board under
`build/integration-smoke/`: API discovery, board-path checks, staged edit
rollback, an undoable footprint move, saving, independent file reload, DRC,
and SVG exports. This board is a tooling test, not the NORA-B106 design.

Command reference: [KiCad 9 CLI documentation](https://docs.kicad.org/9.0/en/cli/cli.html).
