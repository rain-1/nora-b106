#!/usr/bin/env python3
"""Serve only a copied signed-update file on a chosen local interface for one hour."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import re
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--bind', required=True, help='This computer\'s LAN IPv4 address')
parser.add_argument('--port', type=int, default=8765)
parser.add_argument('--version', default='1.0.1')
args = parser.parse_args()
if not re.fullmatch(r'\d{1,3}\.\d{1,3}\.\d{1,5}', args.version):
    parser.error('Version must be major.minor.revision')
filename = 'nora-ota-' + args.version + '.signed.bin'
source = ROOT / 'build/square-p3-ble-ota/dist' / filename
folder = ROOT / 'build/square-p3-ble-ota/phone-download' / args.version
folder.mkdir(parents=True, exist_ok=True)
shutil.copyfile(source, folder / filename)
# Do not serve the key directory, other build artifacts, or the source tree.
handler = partial(SimpleHTTPRequestHandler, directory=str(folder))
with ThreadingHTTPServer((args.bind, args.port), handler) as server:
    server.timeout = 0.5
    deadline = time.monotonic() + 3600
    print(f'Phone download: http://{args.bind}:{args.port}/{filename}', flush=True)
    print('Serving the signed update only; Ctrl-C stops. Automatically stops after one hour.', flush=True)
    try:
        while time.monotonic() < deadline:
            server.handle_request()
    except KeyboardInterrupt:
        pass
