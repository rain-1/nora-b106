---
name: nora-kicad
description: Edit, inspect, and validate KiCad schematics and PCB layouts in the nora-b106-board workspace using its CLI, Python board API, and live IPC connection.
---

# KiCad in this workspace

Use the project Makefile and `tools/` helpers. The verified toolchain is Debian
KiCad 9.0.2 with `/usr/bin/python3` for the `pcbnew` file API and `.venv/bin/python`
for the official `kicad-python==0.4.0` live API bindings. Run commands from the
workspace root. Run `make doctor` when the toolchain is uncertain.

## Choose the editing path

- For an open PCB, prefer live IPC so edits appear in the editor and can be
  grouped in its undo history. `make ipc-status` discovers the open board.
- Before live writes, import `connect_board` from `tools.kicad_ipc` and pass the
  intended PCB's full or workspace-relative path. It rejects a different open
  board. When multiple API sockets exist, choose one explicitly after checking
  its reported board; do not guess.
- Group related live edits with `board.begin_commit()`, `board.push_commit()`,
  and `board.drop_commit()` on failure. In KiCad 9, `update_items()` returns
  staged changes; `get_footprints()` can still return the old board until
  `push_commit()`. Check the update response, then read modified items back
  after pushing to confirm the result. Use `board.save()` when the task calls
  for persisting the changes.
- For a closed PCB, use `pcbnew.LoadBoard` / `pcbnew.SaveBoard` with system Python.
  Check for KiCad lock files and open editors before external writes; an editor
  holding an old copy can overwrite file edits. Do not treat an IPC timeout as
  evidence that the file is closed.
- KiCad 9's IPC API does not edit schematics. Make focused native-file edits or
  use an existing generator, preserve UUIDs and hierarchy, and reopen afterward.
  Respect whether the project treats a generator or the native file as source.

## Check the result

Run `make erc`, `make drc`, and `make preview` as appropriate to the changed
artifact. Override `SCHEMATIC` / `BOARD` for other filenames. Reports are JSON
under `build/reports/`; previews are SVGs under `build/preview/`. Export on-disk
files only after intended live edits have been saved. Inspect rendered previews
visually when changing appearance, placement, or routing; convert SVG to PNG if
the image viewer requires it. Report remaining violations without silently
adding exclusions.

For the NORA-B106 design, verify pin assignments, land pattern, power and decoupling,
antenna placement/keepouts, and module integration requirements against the
selected variant's manufacturer documents before relying on them. ERC and DRC
do not establish those properties. Keep custom libraries project-relative using
`${KIPRJMOD}`. Preserve unrelated project settings and board content.

## API reference

Read `tools/kicad_ipc.py` for connection details. A small live-edit script launched
from the workspace root can start with:

```python
from tools.kicad_ipc import connect_board
client, board = connect_board("nora-b106-board.kicad_pcb")
```

Do not copy APIs from the latest development documentation without checking that
they exist in KiCad 9.0.2 and the installed bindings. Inspect installed methods
or consult the versioned [0.4.0 documentation](https://docs.kicad.org/kicad-python-0.4.0/).
