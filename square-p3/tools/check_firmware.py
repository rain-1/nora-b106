"""Check that the unchanged, validated P1 firmware matches the P3 electrical design."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
p1 = root.parent / 'minimal-p1'
fw = p1 / 'firmware'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
current = json.loads((root / 'design.json').read_text())
previous = json.loads((p1 / 'design.json').read_text())
parts = {ref: nets for ref, nets in current['parts'].items() if ref not in {'H1', 'H2', 'H3', 'H4', 'SW1', 'R1', 'R2', 'J1'}}
assert current['parts']['SW1'] == {'1': 'RESET_N', '2': 'GND'}, 'Reset button wiring changed'
assert parts == {ref: nets for ref, nets in previous['parts'].items() if ref != 'J1'}, 'P3/P1 electrical parts or net mapping changed'
usb = {**{n: 'GND' for n in ['A1', 'B12', 'A12', 'B1', 'S1']},
       **{n: 'VBUS' for n in ['A4', 'B9', 'A9', 'B4']},
       'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_DP', 'B6': 'USB_DP',
       'A7': 'USB_DM', 'B7': 'USB_DM'}
assert current['parts']['J1'] == usb, 'USB-C pin mapping changed'
assert current['parts']['R1'] == {'1': 'CC1', '2': 'GND'}
assert current['parts']['R2'] == {'1': 'CC2', '2': 'GND'}
assert current['gpio_header'] == previous['gpio_header'], 'P3/P1 J3 pinout mismatch'
assert current['module'] == previous['module'], 'Module pin mapping changed'
manifest = json.loads((fw / 'dist/manifest.json').read_text())
for folder, key in [(fw, 'source_sha256'), (fw / 'dist', 'sha256')]:
    for name, expected in manifest[key].items():
        assert hashlib.sha256((folder / name).read_bytes()).hexdigest() == expected, name
validation = json.loads((fw / 'dist/validation.json').read_text())
expected = [current['gpio_header'][str(n)].split('_')[0] for n in range(3, 15)]
assert validation['result'] == 'passed' and validation['gpio_header'] == expected
subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(fw / 'tests'), '-v'], check=True)
report = {
    'result': 'passed',
    'hardware_tested': False,
    'firmware': '../minimal-p1/firmware',
    'app_version': manifest['app_version'],
    'gpio_header': current['gpio_header'],
    'factory_hex_sha256': manifest['sha256']['nora-factory.hex'],
    'usb_update_sha256': manifest['sha256']['nora-app.signed.bin'],
    'checks': ['Core circuit, module assignments and headers match P1; USB-C mapping and CC pull-downs verified',
               'All shared firmware sources and artifacts match the validated P1 manifest',
               'Resolved twelve-GPIO mapping matches the validated image report',
               'Eight host uploader tests passed'],
}
if args.output:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
print('P3/P1 firmware compatibility, source/image hashes and uploader tests passed.')
