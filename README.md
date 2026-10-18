# NORA-B106 board workspace

Revision C is a 36 x 36 mm two-layer NORA-B106 breakout for self assembly.
It exposes SWD, twelve GPIOs, optional USB-C power/data, an LED, and reset.

- [Assembly options, pinouts, and JLCPCB settings](hardware/README.md)
- [Pico programmer wiring and first tests](programming/README.md)
- [Parts list with SWD-only / USB population choices](hardware/BOM.csv)
- [Bare-PCB Gerber ZIP](fabrication/nora-b106-breakout-revC-gerbers.zip)
- [Assembly drawing](fabrication/preview/assembly-top.png)
- [Schematic preview](fabrication/preview/nora-b106-board.png)

CAD validation passed with zero ERC, DRC, unconnected-item, or schematic-parity
issues. The hardware and programmer connection have not been physically tested.
Revision C adds six GPIOs on optional J4/J5 while retaining revision B's module
ground-plane improvements. Use the revision C Gerbers; earlier revisions are
retained in Git history. Debian 13's packaged OpenOCD is too old for the Pico route;
the programming guide provides a newer source build and an offline check.
For the lowest part count, start with the SWD-only population and power it from
a Pico's 3V3 OUT, following the wiring guide. The USB population uses its own
regulator; do not connect Pico 3V3 in that configuration.

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
