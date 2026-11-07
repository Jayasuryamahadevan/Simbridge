# SimBridge

**A local, bidirectional cellular-call audio bridge for Linux.**

SimBridge connects an Android phone's existing SIM call audio to an AI speech application through a Linux computer. The phone remains responsible for the cellular call. Linux handles the Bluetooth hands-free audio path and exposes a stable audio interface to applications.

## Project status

The initial software foundation is implemented. Actual cellular-call audio is not bridged yet.

- [x] Project structure and Python package
- [x] Read-only Linux, BlueZ and PipeWire diagnostics
- [x] Bluetooth controller and known-device inspection
- [x] HFP/HSP profile inspection from PipeWire card data
- [x] Canonical PCM frame contract and bounded frame buffer
- [x] Explicit call/audio readiness state machine
- [x] Unit tests and GitHub Actions CI
- [ ] Verify Android Bluetooth HFP/HSP compatibility
- [ ] Bidirectional PipeWire audio backend
- [ ] Disconnect recovery and long-running stability tests
- [ ] AI adapter (including Gnani)

## Design principles

- Local-first: no telephony provider, cloud relay, or extra phone number.
- Reuse Linux BlueZ and PipeWire; do not implement Bluetooth profiles ourselves.
- Read-only diagnostics first. No automatic dialing, answering, recording, pairing, or connection changes.
- Keep the media path low-latency and bounded. Drop stale audio instead of replaying it.
- No network listener in the core application.
- AI integrations must not control call state by default.

## Requirements

- Linux with BlueZ, PipeWire, and WirePlumber.
- An Android phone that exposes the Bluetooth Hands-Free Profile (HFP) to the Linux host.
- Python 3.11 or newer.

Bluetooth pairing alone does not prove that HFP call audio is available. Profile inspection reports what PipeWire advertises; an actual test call is still required to verify the phone, negotiated profile, and bidirectional audio.

## Quick start

```bash
git clone https://github.com/Jayasuryamahadevan/Simbridge.git
cd Simbridge
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
simbridge doctor
```

The doctor command is read-only. It checks operating-system details and detects tools/services relevant to BlueZ and PipeWire. It does not pair devices or modify system configuration.

## CLI

```bash
simbridge doctor
simbridge doctor --json
simbridge status
simbridge bluetooth devices
simbridge bluetooth controller
simbridge bluetooth profiles
simbridge audio devices
```

## Development

```bash
pytest
```

## Audio contract

The planned application-facing format is signed 16-bit little-endian PCM, mono, 16 kHz, in 20 ms frames (640 bytes per frame). This is an internal normalized format—not a claim that Bluetooth natively negotiates 16 kHz. The future media backend must inspect the negotiated HFP codec and resample where required.

## Safety and privacy

SimBridge does not capture or persist call audio. Current commands are read-only and there is no network listener. See [SECURITY.md](SECURITY.md) for reporting issues.

## License

MIT. See [LICENSE](LICENSE).
