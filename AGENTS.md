# NORA-B106 breakout

Read `hardware/README.md` before electrical/layout changes and
`programming/README.md` before suggesting a power or programmer connection.

The delivered routed native PCB is authoritative. `tools/generate_board.py`
records the initial schematic/placement/preroutes; running it over the finished
PCB discards routing. It requires `--overwrite` for that reason. Make focused
native-file or live IPC edits for board changes, preserving unrelated content.

Use `make check` for ERC/DRC and `make fabrication` for the complete validation
including schematic parity and bare-board exports. Save live edits first.
The order settings are 2 layers, 36 x 36 mm, 0.8 mm FR4, 1 oz copper.
There are SWD-only and USB population variants with different power wiring.
No assembled hardware or Pico programming session has been physically tested.
