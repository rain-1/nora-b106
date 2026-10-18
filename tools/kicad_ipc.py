"""Read live PCB status, or connect board scripts to an explicitly chosen file."""

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

from kipy import KiCad


def connect_board(expected_path, socket_path=None):
    """Return (KiCad, Board); require the expected file path before making edits.

    Pass None only for read-only discovery. A second editor requires an explicit
    socket choice rather than silently selecting the first open board.
    """
    socket_path = socket_path or os.environ.get("KICAD_API_SOCKET")
    if not socket_path:
        sockets = sorted((Path(tempfile.gettempdir()) / "kicad").glob("api*.sock"))
        if len(sockets) > 1:
            raise RuntimeError("Multiple KiCad sockets; select one with --socket: "
                               + ", ".join(map(str, sockets)))
        if sockets:
            socket_path = str(sockets[0])
    if socket_path and not socket_path.startswith("ipc://"):
        socket_path = "ipc://" + socket_path
    client = KiCad(socket_path=socket_path, timeout_ms=2000)
    client.ping()
    client.check_version()
    board = client.get_board()
    document = board.document
    actual_path = (Path(document.project.path) / document.board_filename).resolve()
    if expected_path is not None and actual_path != Path(expected_path).resolve():
        raise RuntimeError(f"Expected {Path(expected_path).resolve()}, but the editor has {actual_path}")
    return client, board


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, help="Require this PCB to be open")
    parser.add_argument("--socket", help="Explicit IPC socket path or ipc:// URL")
    args = parser.parse_args()
    try:
        client, board = connect_board(args.board, args.socket)
        document = board.document
        result = {
            "kicad_version": str(client.get_version()),
            "bindings_api_version": str(client.get_api_version()),
            "board": str((Path(document.project.path) / document.board_filename).resolve()),
            "tracks": len(board.get_tracks()),
            "vias": len(board.get_vias()),
            "shapes": len(board.get_shapes()),
            "footprints": [
                {"reference": fp.reference_field.text.value,
                 "x_mm": fp.position.x / 1_000_000,
                 "y_mm": fp.position.y / 1_000_000}
                for fp in board.get_footprints()
            ],
        }
    except Exception as error:
        print(f"KiCad IPC: {type(error).__name__}: {error}", file=sys.stderr)
        print("Open a PCB with the API server enabled; close modal dialogs before retrying.", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
