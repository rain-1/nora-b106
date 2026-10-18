"""Check the Debian KiCad environment without modifying a design."""

import importlib
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    failures = []
    for name in ("kicad", "kicad-cli", "eeschema", "pcbnew"):
        executable = shutil.which(name)
        print(f"{'OK' if executable else 'MISSING'}: {name}: {executable or 'not on PATH'}")
        if not executable:
            failures.append(name)

    cli = shutil.which("kicad-cli")
    if cli:
        result = subprocess.run([cli, "version"], capture_output=True, text=True)
        print(f"KiCad version: {(result.stdout or result.stderr).strip()}")
        if result.returncode:
            failures.append("kicad-cli version")

    print(f"Python: {sys.executable}")
    try:
        pcbnew = importlib.import_module("pcbnew")
        print(f"OK: Python board API: {pcbnew.GetBuildVersion()}")
    except (ImportError, OSError) as error:
        print(f"MISSING: Python board API: {error}")
        failures.append("Python pcbnew module")

    for name in ("symbols", "footprints", "template"):
        directory = Path("/usr/share/kicad") / name
        present = directory.is_dir() and any(directory.iterdir())
        print(f"{'OK' if present else 'MISSING'}: {directory}")
        if not present:
            failures.append(str(directory))

    if failures:
        print("\nInstall the Debian packages listed in README.md, then rerun make doctor.")
        return 1
    print("\nKiCad CLI, board scripting, and standard libraries are ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
