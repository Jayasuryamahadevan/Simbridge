# SimBridge architecture

## Goal

Bridge an Android handset's active cellular-call audio to a Linux application in both directions. The handset and SIM continue to own the cellular call; SimBridge is not a telephony provider.

## Initial topology

```text
Remote caller
    |
Carrier voice network
    |
Android phone + existing SIM
    |
Bluetooth HFP (SCO/eSCO; CVSD or mSBC when negotiated)
    |
BlueZ + PipeWire / WirePlumber
    |
SimBridge media backend
    |                         ^
    | phone -> application    | application -> phone
    v                         |
AI speech pipeline / Gnani adapter
```

The Bluetooth codec and rate are negotiated by the Bluetooth stack. The application-facing format is normalized separately to mono signed 16-bit little-endian PCM at 16 kHz, in 20 ms frames. The backend must inspect the negotiated profile and resample where required; it must not assume that the Bluetooth link itself is 16 kHz.

## Components

- **CLI and doctor:** read-only inventory of Linux, BlueZ, PipeWire, WirePlumber and available audio nodes.
- **Bluetooth inspection:** reports known devices and controller state. Pairing and connection control are not part of the first milestone.
- **Audio contract:** validates fixed-size PCM frames and provides a bounded queue. On overflow, the oldest frame is discarded to avoid accumulating conversational latency.
- **Runtime state machine:** tracks verified readiness stages and rejects impossible transitions.
- **Media backend (next milestone):** creates and supervises PipeWire streams for phone downlink and uplink.
- **AI adapter (later):** consumes downlink frames and returns uplink frames. It cannot control calls or Bluetooth by default.

## State progression

```text
DISCONNECTED -> PHONE_PAIRED -> PHONE_CONNECTED -> HFP_AVAILABLE
                                                   |
                                                   v
CALL_ACTIVE -> AUDIO_BRIDGED -> AI_READY
```

A disconnect returns runtime to the appropriate earlier state. Errors require an explicit reset to DISCONNECTED before a new connection sequence.

## Reliability constraints

1. Keep all queues bounded.
2. Discard stale frames rather than replaying them after a stall.
3. Make stream creation and teardown idempotent.
4. Recover from phone disconnects and PipeWire restarts without creating duplicate streams.
5. Do not restart system audio services automatically.
6. Report profile availability separately from Bluetooth pairing.
7. Do not persist call audio unless a future explicit recording feature is enabled.

## Security constraints

- No HTTP or public network listener in the core.
- No automatic dialing, answering, recording, pairing, or connecting.
- No credentials in logs or diagnostic output.
- Any future local IPC endpoint must use a private Unix-domain socket and restrictive permissions.
- Treat model-generated tool arguments as untrusted input.
