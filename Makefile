PROJECT ?= nora-b106-board
SCHEMATIC ?= $(PROJECT).kicad_sch
BOARD ?= $(PROJECT).kicad_pcb
KICAD_CLI ?= kicad-cli
PYTHON ?= /usr/bin/python3
IPC_PYTHON ?= .venv/bin/python

.PHONY: help doctor ipc-status erc drc check schematic-svg pcb-svg preview fabrication

help:
	@printf '%s\n' 'make doctor         Check KiCad, Python board API, and libraries' 'make ipc-status     Inspect the PCB open in KiCad via the live API' 'make check          Run schematic ERC and board DRC' 'make fabrication    Validate parity and regenerate the JLCPCB Gerber ZIP' 'make preview        Export schematic and board SVGs to build/' 'Override PROJECT, SCHEMATIC, or BOARD for other file names.'

doctor:
	$(PYTHON) tools/kicad-doctor.py

ipc-status:
	$(IPC_PYTHON) tools/kicad_ipc.py

erc:
	@test -f "$(SCHEMATIC)" || { printf 'Missing schematic: %s\n' "$(SCHEMATIC)"; exit 1; }
	mkdir -p build/reports
	$(KICAD_CLI) sch erc --exit-code-violations --format json --output build/reports/erc.json "$(SCHEMATIC)"

drc:
	@test -f "$(BOARD)" || { printf 'Missing board: %s\n' "$(BOARD)"; exit 1; }
	mkdir -p build/reports
	$(KICAD_CLI) pcb drc --exit-code-violations --format json --output build/reports/drc.json "$(BOARD)"

check: erc drc

schematic-svg:
	@test -f "$(SCHEMATIC)" || { printf 'Missing schematic: %s\n' "$(SCHEMATIC)"; exit 1; }
	mkdir -p build/preview/schematic
	$(KICAD_CLI) sch export svg --output build/preview/schematic/ "$(SCHEMATIC)"

pcb-svg:
	@test -f "$(BOARD)" || { printf 'Missing board: %s\n' "$(BOARD)"; exit 1; }
	mkdir -p build/preview/pcb
	$(KICAD_CLI) pcb export svg --mode-multi --layers F.Cu,B.Cu,F.Silkscreen,B.Silkscreen,Edge.Cuts --output build/preview/pcb/ "$(BOARD)"

preview: schematic-svg pcb-svg

fabrication:
	$(PYTHON) tools/export_fabrication.py
