"""Read-only BlueZ inspection helpers.

Pairing, connecting and profile changes are intentionally not implemented in
this first milestone. Those operations will require explicit user actions.
"""

from simbridge.diagnostics import CommandResult, run_probe


def list_devices() -> CommandResult:
    return run_probe(("bluetoothctl", "devices"))


def show_controller() -> CommandResult:
    return run_probe(("bluetoothctl", "show"))
