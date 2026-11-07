# SimBridge

**A local, bidirectional cellular-call audio bridge for Linux.**

SimBridge is being built to connect an Android phone's existing SIM call audio to local or remote AI speech systems through a Linux computer. The phone remains responsible for the cellular call. Linux handles the Bluetooth hands-free audio path and exposes a stable audio interface to applications.

## Project status

Early development. The first milestone is environment discovery and Bluetooth HFP compatibility—not AI integration.

- [x] Project initialized
- [ ] Linux environment diagnostics
- [ ] Verify Android Bluetooth HFP/HSP compatibility
- [ ] Bidirectional PipeWire audio
- [ ] Reconnect and recovery handling
- [ ] AI adapter (including Gnani)

## Design principles

- Local-first: no telephony provider, cloud relay, or extra phone number.
- Reuse Linux BlueZ and PipeWire; do not implement Bluetooth profiles ourselves.
- Read-only diagnostics first. No automatic dialing, answering, recording, or Bluetooth pairing.
- Keep the media path low-latency and bounded. Drop stale audio instead of replaying it.
- No network listener in the core application.
- AI integrations must not control call state unless explicitly enabled by the user.

## Requirements

- Linux with BlueZ, PipeWire, and WirePlumber.
- An Android phone that exposes the Bluetooth Hands-Free Profile (HFP) to the Linux host.
- Python 3.11 or newer.

Bluetooth pairing alone does not prove that HFP call audio is available. SimBridge's doctor command reports local capabilities; an actual test call is required to verify the phone, Bluetooth stack, and audio profile together.

## Quick start

Clone the repository and install the project in editable mode:

```bash
git clone https://github.com/Jayasuryamahadevan/Simbridge.git
cd Simbridge
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
simbridge doctor
```

The doctor command is read-only. It checks operating-system details and detects tools/services relevant to BlueZ and PipeWire. It does not pair devices or modify system configuration.

## Development

```bash
pytest
simbridge --help
simbridge bluetooth devices
simbridge audio devices
```

## Audio contract

The planned application-facing format is signed 16-bit little-endian PCM, mono, 16 kHz, in 20 ms frames. This is an internal normalized format—not a claim that the Bluetooth link natively negotiates 16 kHz. The implementation must inspect the negotiated HFP codec and resample where required.

## Safety and privacy

SimBridge does not capture or persist call audio by default. Diagnostics must avoid printing credentials or personal call content. See [SECURITY.md](SECURITY.md) for reporting issues.

## License

MIT. See [LICENSE](LICENSE).
