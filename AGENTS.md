# NORA-B106 breakout

Read `hardware/README.md` before electrical/layout changes and
`programming/README.md` before suggesting a power or programmer connection.

The delivered routed native PCB is authoritative. `tools/generate_board.py`
records the initial schematic/placement/preroutes; running it over the finished
PCB discards routing. It requires `--overwrite` for that reason. Make focused
native-file or live IPC edits for board changes, preserving unrelated content.

Use `make check` for ERC/DRC and `make fabrication` for the complete validation
including schematic parity and bare-board exports. Save live edits first.
Revision B reserves B.Cu beneath U1 for ground and protects the antenna ground
row with a track keepout. `make ground-check` also checks signal clearances
against the module body and requires two vias in every top ground island.
Revision D retains those constraints and consolidates twelve GPIOs plus
3V3/GND onto one right-edge 1x14 header J3. Its pinout changed from revision C;
use hardware/README.md. J2 SWD remains on the left with its original pinout.
The order settings are 2 layers, 36 x 36 mm, 0.8 mm FR4, 1 oz copper.
There are SWD-only and USB population variants with different power wiring.
No assembled hardware or Pico programming session has been physically tested.

Minimal P1 is a separate project under `minimal-p1/`. Its working PCB/schematic
are KiCad 9; the original Backplane 10.99 files under `backplane-source/` are
reference snapshots. Read that project's README and hardware/programming guides
before changes. Use `make -C minimal-p1 check` or `fabrication` for its CAD,
and `make -C minimal-p1 firmware` / `firmware-check` for firmware. It uses
36.5 x 36.5 mm, 1.6 mm FR4 and a different J3 pinout from revision D.

Compact P2 is a separate smaller project under `minimal-p2/`, derived from P1.
Read its hardware/programming guides before changes. Its routed native KiCad 9
PCB is authoritative; do not rerun the initial operation scripts in build/.
Use `make -C minimal-p2 check` / `fabrication` and `firmware` / `firmware-check`.
Order settings are 2 layers, 31.5 x 27.5 mm, 1.6 mm FR4, 1 oz copper. It retains
the ground and RF constraints. J2 remains the five-pin SWD header; J3 is now
six pins: 3V3, GND, P0.24, P1.06, P0.20, P0.07/AIN3. Use P2 firmware only;
USB IDs and the development signing key differ from P1. Hardware remains untested.

Current Dragon P3.1 is under `square-p3/`, 38 x 49.5 mm, 1.6 mm FR4, 2 layers,
1 oz; the former square P3 is in Git history. It has twelve GPIOs and P1's exact
J2/J3 electrical pinout. It deliberately
uses the unchanged firmware under `minimal-p1/firmware/`; do not use P2 firmware.
Read P3's hardware/programming guides before edits. Its routed native KiCad 9
PCB is authoritative. `make -C square-p3 fabrication` checks ERC, DRC/parity,
ground/RF/82-pad geometry, mounting holes and shared-firmware compatibility,
runs the eight uploader tests, then exports Gerbers/paste/both drill files.
`firmware-check` checks the shared P1 artifacts without rebuilding them. H1/H2
are board-only optional M2 holes at the bottom. SW1 is an optional through-hole
reset switch, marked DNP; omitting it leaves the minimum assembly unchanged.
USB is centred at x=19 mm. The grouped cyber dragon and signature are back
silkscreen only, with no decorative mask openings or copper. Artwork source,
vectors and prompt are under artwork/. The RF/ground keepouts are retained.
Hardware remains untested.
