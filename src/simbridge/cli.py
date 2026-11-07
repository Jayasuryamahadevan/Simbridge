"""Command-line interface for SimBridge."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from simbridge import __version__
from simbridge.diagnostics import collect_diagnostics, format_diagnostics, run_probe


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="simbridge",
        description="Local Android cellular-call audio bridge for Linux.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser("doctor", help="run read-only host diagnostics")
    doctor.add_argument("--json", action="store_true", help="print machine-readable JSON")

    status = commands.add_parser("status", help="show host and audio-stack readiness")
    status.add_argument("--json", action="store_true", help="print machine-readable JSON")

    bluetooth = commands.add_parser("bluetooth", help="inspect Bluetooth")
    bluetooth_commands = bluetooth.add_subparsers(dest="bluetooth_command", required=True)
    bluetooth_commands.add_parser("devices", help="list known Bluetooth devices")
    bluetooth_commands.add_parser("controller", help="show Bluetooth controller details")

    audio = commands.add_parser("audio", help="inspect the PipeWire audio graph")
    audio_commands = audio.add_subparsers(dest="audio_command", required=True)
    audio_commands.add_parser("devices", help="list PipeWire nodes and audio cards")
    return parser


def _print_probe(title: str, command: tuple[str, ...]) -> int:
    result = run_probe(command)
    print(title)
    print("=" * len(title))
    if not result.available:
        print(result.error or "Required command is unavailable.")
        return 2
    if result.error:
        print(result.error)
        return 1
    print(result.output or "(no output)")
    return 0 if result.exit_code == 0 else 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command in {"doctor", "status"}:
            report = collect_diagnostics()
            print(json.dumps(report, indent=2) if args.json else format_diagnostics(report))
            return 0 if report["host_tools_ready"] else 1

        if args.command == "bluetooth":
            if args.bluetooth_command == "devices":
                return _print_probe("Known Bluetooth devices", ("bluetoothctl", "devices"))
            return _print_probe("Bluetooth controller", ("bluetoothctl", "show"))

        if args.command == "audio":
            graph_code = _print_probe("PipeWire graph", ("wpctl", "status"))
            cards_code = _print_probe("Audio cards", ("pactl", "list", "cards", "short"))
            return max(graph_code, cards_code)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
