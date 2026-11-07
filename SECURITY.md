# Security policy

## Scope

SimBridge handles access to live telephone audio. Security and privacy defects that expose call content, permit unauthorized call control, or weaken the host security boundary are in scope.

## Reporting

Please report vulnerabilities privately through GitHub's repository security reporting feature when enabled. Do not publish call recordings, phone numbers, access tokens, or personal data in an issue.

## Current security posture

The initial release is intentionally read-only:

- No network listener.
- No call-control commands.
- No audio recording or persistence.
- Diagnostic subprocesses use fixed argument arrays, never a shell.
- Diagnostic commands have timeouts and bounded output.

These safeguards are not a substitute for a security review of future audio and IPC components.
