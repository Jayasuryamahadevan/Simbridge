"""Interface expected from a future PipeWire media backend."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from simbridge.audio.format import AudioFormat, AudioFrame


@runtime_checkable
class AudioBackend(Protocol):
    @property
    def input_format(self) -> AudioFormat: ...

    @property
    def output_format(self) -> AudioFormat: ...

    def read_frame(self, timeout: float) -> AudioFrame | None:
        """Return the next phone-to-AI frame, or None when no frame is ready."""
        ...

    def write_frame(self, frame: AudioFrame) -> None:
        """Queue one AI-to-phone frame; implementations must bound their queues."""
        ...

    def close(self) -> None:
        """Release streams and local resources."""
        ...
