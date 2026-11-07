"""Read-only host and audio-stack diagnostics."""

from __future__ import annotations

import platform
import shutil
import subprocess
from dataclasses import asdict, dataclass
from typing import Sequence

OUTPUT_LIMIT = 4_000
DEFAULT_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True, slots=True)
class CommandResult:
    command: tuple[str, ...]
    available: bool
    exit_code: int | None
    output: str
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.available and self.exit_code == 0 and self.error is None


def run_probe(
    command: Sequence[str],
    *,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> CommandResult:
    """Run a bounded diagnostic command without a shell."""
    args = tuple(str(part) for part in command)
    if not args:
        raise ValueError("A diagnostic command cannot be empty")

    executable = shutil.which(args[0])
    if executable is None:
        return CommandResult(args, False, None, "", f"{args[0]} was not found on PATH")

    try:
        completed = subprocess.run(
            (executable, *args[1:]),
            check=False,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return CommandResult(
            args, True, None, "", f"Command timed out after {timeout:g} seconds"
        )
    except OSError as exc:
        return CommandResult(args, True, None, "", f"{type(exc).__name__}: {exc}")

    output = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()
    if not output and stderr:
        output = stderr
    if len(output) > OUTPUT_LIMIT:
        output = output[:OUTPUT_LIMIT] + "\n… output truncated …"

    return CommandResult(args, True, completed.returncode, output)


def _os_summary() -> dict[str, str]:
    details = {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }
    if hasattr(platform, "freedesktop_os_release"):
        try:
            release = platform.freedesktop_os_release()
        except OSError:
            release = {}
        if release.get("PRETTY_NAME"):
            details["distribution"] = release["PRETTY_NAME"]
        if release.get("VERSION_ID"):
            details["distribution_version"] = release["VERSION_ID"]
    return details


def collect_diagnostics() -> dict[str, object]:
    """Collect local host, BlueZ and PipeWire facts without changing the host."""
    probes = (
        ("bluetoothctl_version", ("bluetoothctl", "--version")),
        ("bluetooth_controller", ("bluetoothctl", "show")),
        ("paired_bluetooth_devices", ("bluetoothctl", "devices")),
        ("pipewire_version", ("pipewire", "--version")),
        ("wireplumber_version", ("wireplumber", "--version")),
        ("wpctl_version", ("wpctl", "--version")),
        ("pipewire_graph", ("wpctl", "status")),
        ("pulse_compatible_cards", ("pactl", "list", "cards", "short")),
        ("bluetooth_service", ("systemctl", "is-active", "bluetooth.service")),
        ("pipewire_service", ("systemctl", "--user", "is-active", "pipewire.service")),
        ("wireplumber_service", ("systemctl", "--user", "is-active", "wireplumber.service")),
    )
    checks = {name: asdict(run_probe(command)) for name, command in probes}
    required_tools = ("bluetoothctl", "wpctl", "systemctl")
    missing_tools = [tool for tool in required_tools if shutil.which(tool) is None]
    is_linux = platform.system() == "Linux"

    return {
        "os": _os_summary(),
        "is_linux": is_linux,
        "required_tools_missing": missing_tools,
        "checks": checks,
        "host_tools_ready": is_linux and not missing_tools,
        "hfp_verified": False,
        "notes": [
            "Installed tools do not prove Bluetooth HFP call audio is available.",
            "A real test call is required to verify the phone, negotiated profile, and bidirectional audio.",
            "This report is read-only; it does not pair, connect, dial, answer, record, or alter services.",
        ],
    }


def format_diagnostics(report: dict[str, object]) -> str:
    os_info = report["os"]
    assert isinstance(os_info, dict)
    lines = [
        "SimBridge doctor",
        "================",
        f"OS: {os_info.get('distribution', os_info.get('system', 'unknown'))}",
        f"Kernel: {os_info.get('release', 'unknown')} ({os_info.get('machine', 'unknown')})",
        f"Python: {os_info.get('python', 'unknown')}",
        "",
        "Host readiness:",
        f"  {'PASS' if report['host_tools_ready'] else 'CHECK'}  Required Linux tools",
    ]
    if report["required_tools_missing"]:
        lines.append(f"        Missing: {', '.join(report['required_tools_missing'])}")

    checks = report["checks"]
    assert isinstance(checks, dict)
    labels = {
        "bluetoothctl_version": "BlueZ CLI",
        "bluetooth_controller": "Bluetooth controller",
        "paired_bluetooth_devices": "Known Bluetooth devices",
        "pipewire_version": "PipeWire",
        "wireplumber_version": "WirePlumber",
        "wpctl_version": "PipeWire control CLI",
        "pipewire_graph": "Audio graph",
        "pulse_compatible_cards": "Audio cards",
        "bluetooth_service": "Bluetooth service",
        "pipewire_service": "PipeWire user service",
        "wireplumber_service": "WirePlumber user service",
    }
    lines.extend(["", "Detected components:"])
    for key, label in labels.items():
        item = checks[key]
        available = bool(item["available"])
        output = str(item["output"]).splitlines()
        first_line = output[0] if output else (item["error"] or "No response")
        lines.append(f"  {'FOUND' if available else 'MISSING':7} {label}: {first_line[:180]}")

    lines.extend([
        "",
        "HFP call audio: NOT VERIFIED",
        "Pairing and installed tools are insufficient evidence. Verify with a real cellular call.",
        "",
        "No system configuration was changed.",
    ])
    return "\n".join(lines)
