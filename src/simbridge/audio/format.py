"""Canonical PCM frame definitions used by audio adapters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AudioFormat:
    sample_rate_hz: int
    channels: int
    sample_width_bytes: int
    frame_duration_ms: int
    encoding: str = "s16le"

    def __post_init__(self) -> None:
        if self.sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be positive")
        if self.channels <= 0:
            raise ValueError("channels must be positive")
        if self.sample_width_bytes <= 0:
            raise ValueError("sample_width_bytes must be positive")
        if self.frame_duration_ms <= 0:
            raise ValueError("frame_duration_ms must be positive")
        if self.encoding == "s16le" and self.sample_width_bytes != 2:
            raise ValueError("s16le requires a 2-byte sample width")

    @property
    def samples_per_channel(self) -> int:
        numerator = self.sample_rate_hz * self.frame_duration_ms
        if numerator % 1000:
            raise ValueError("Frame duration does not produce an integer sample count")
        return numerator // 1000

    @property
    def bytes_per_frame(self) -> int:
        return self.samples_per_channel * self.channels * self.sample_width_bytes


PCM16_MONO_16K_20MS = AudioFormat(
    sample_rate_hz=16_000,
    channels=1,
    sample_width_bytes=2,
    frame_duration_ms=20,
)


@dataclass(frozen=True, slots=True)
class AudioFrame:
    payload: bytes
    sequence: int
    audio_format: AudioFormat = PCM16_MONO_16K_20MS
    timestamp_ns: int | None = None

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if len(self.payload) != self.audio_format.bytes_per_frame:
            raise ValueError(
                f"Expected {self.audio_format.bytes_per_frame} bytes, got {len(self.payload)}"
            )
        if self.timestamp_ns is not None and self.timestamp_ns < 0:
            raise ValueError("timestamp_ns must be non-negative")
