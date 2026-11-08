#!/usr/bin/env python3
"""Exercise the real Pico UART connection to Dragon BLE firmware."""
import argparse
import re
import sys
import time

import serial


def check_output(data):
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()
    clean = re.sub(rb"\x1b\[[0-?]*[ -/]*[@-~]", b"", data)
    if b"<err>" in clean or b"ERROR:" in clean:
        raise RuntimeError(f"Firmware reported an error: {clean!r}")
    return clean


def receive(port, expected, timeout=5):
    data = b""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        chunk = port.read(max(1, port.in_waiting))
        if chunk:
            data += chunk
            check_output(chunk)
            clean = re.sub(rb"\x1b\[[0-?]*[ -/]*[@-~]", b"", data)
            if b"<err>" in clean or b"ERROR:" in clean:
                raise RuntimeError(f"Firmware reported an error: {clean!r}")
            if expected in clean:
                return clean
    raise RuntimeError(f"Expected {expected!r}; received {data!r}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port")
    parser.add_argument("--wait-startup", action="store_true")
    args = parser.parse_args()
    with serial.Serial(args.port, 115200, timeout=0.1) as port:
        if args.wait_startup:
            receive(port, b"Advertising as ", timeout=60)
            time.sleep(0.2)
        port.write(b"\r\n")
        time.sleep(0.2)
        check_output(port.read(port.in_waiting))
        port.reset_input_buffer()
        for command, expected in [
            ("info", b"advertising: active"),
            ("interval 500", b"LED interval=500 ms"),
            ("on", b"LED on"),
            ("state", b"LED mode=1 lit=1 interval=500 ms"),
            ("off", b"LED off"),
            ("state", b"LED mode=0 lit=0 interval=500 ms"),
            ("interval 100", b"LED interval=100 ms"),
            ("state", b"LED mode=0 lit=0 interval=100 ms"),
            ("interval 49", b"Interval must be 50..5000 ms"),
            ("interval 5001", b"Interval must be 50..5000 ms"),
            ("state", b"LED mode=0 lit=0 interval=100 ms"),
            ("interval 500", b"LED interval=500 ms"),
            ("blink", b"LED blinking"),
        ]:
            port.write(command.encode() + b"\r")
            receive(port, expected)
            time.sleep(0.1)
        print("\nPASS: BLE reports active advertising; UART info and LED commands passed.")


if __name__ == "__main__":
    main()
