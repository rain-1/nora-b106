#!/usr/bin/env python3
"""Linux UART terminal/smoke test using only Python's standard library."""
import argparse
import os
import select
import sys
import termios
import time
import tty


def read_until(fd, expected, timeout):
    output = b""
    deadline = time.monotonic() + timeout
    while expected not in output:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError(f"Timed out waiting for {expected!r}; got {output!r}")
        if select.select([fd], [], [], remaining)[0]:
            chunk = os.read(fd, 4096)
            if not chunk:
                raise RuntimeError("Serial device disconnected")
            output += chunk
    sys.stdout.buffer.write(output)
    sys.stdout.buffer.flush()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", help="Pico UART device, preferably /dev/serial/by-id/...")
    parser.add_argument("--test", action="store_true", help="Exercise console commands")
    parser.add_argument("--wait-startup", action="store_true", help="Wait up to 60 s for firmware startup")
    args = parser.parse_args()
    fd = os.open(args.port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    original = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        settings = termios.tcgetattr(fd)
        settings[4] = settings[5] = termios.B115200
        settings[2] |= termios.CLOCAL | termios.CREAD
        settings[2] &= ~termios.CRTSCTS
        termios.tcsetattr(fd, termios.TCSANOW, settings)
        if args.wait_startup:
            read_until(fd, b"nora> ", 60)
        if args.test:
            # A power cycle or previous terminal can leave a partial command
            # or latched line error. Terminate it before checking fresh replies.
            os.write(fd, b"\r\n")
            time.sleep(0.1)
            # Commands are sent as normal full lines, without artificial pacing.
            cases = [
                (b"help", b"help  info  on  off  blink"),
                (b"info", b"ID 3804d25d-e462b092"),
                (b"on", b"LED on"),
                (b"off", b"LED off"),
                (b"unknown", b"Unknown command"),
                (b"x" * 40, b"Input overflow/error"),
                (b"blink", b"LED blinking"),
            ]
            for command, expected in cases:
                termios.tcflush(fd, termios.TCIFLUSH)
                os.write(fd, command + b"\r\n")
                output = read_until(fd, b"nora> ", 3)
                if expected not in output:
                    raise RuntimeError(f"Unexpected reply to {command!r}: {output!r}")
            print("PASS: UART commands, device identity, LED modes, invalid/long input")
        else:
            print("115200 8N1. Type help then Enter. Ctrl-C exits. Local line editing enabled.", flush=True)
            while True:
                ready, _, _ = select.select([fd, sys.stdin], [], [])
                if fd in ready:
                    chunk = os.read(fd, 4096)
                    if not chunk:
                        break
                    sys.stdout.buffer.write(chunk)
                    sys.stdout.buffer.flush()
                if sys.stdin in ready:
                    line = sys.stdin.readline()
                    if not line:
                        break
                    os.write(fd, line.encode())
    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, original)
        os.close(fd)


if __name__ == "__main__":
    main()
