.PHONY: check fabrication ground-check firmware-check
check:
	python3 tools/fabricate.py --check
fabrication:
	python3 tools/fabricate.py
ground-check:
	/usr/bin/python3 tools/check_module_ground.py
	/usr/bin/python3 tools/audit_design.py
firmware-check:
	python3 tools/check_firmware.py
