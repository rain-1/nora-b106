.PHONY: check fabrication ground-check
check:
	python3 tools/fabricate.py --check
fabrication:
	python3 tools/fabricate.py
ground-check:
	/usr/bin/python3 tools/check_module_ground.py
	/usr/bin/python3 tools/audit_design.py

.PHONY: firmware firmware-setup firmware-check
firmware-setup:
	python3 firmware/tools/setup.py
	python3 firmware/tools/install_mcumgr.py
firmware:
	python3 firmware/tools/build.py
firmware-check:
	build/firmware/venv/bin/python firmware/tools/validate_build.py
	python3 -m unittest discover -s firmware/tests -v
