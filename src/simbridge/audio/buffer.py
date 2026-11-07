"""Thread-safe bounded frame buffer that discards the oldest audio on overflow."""

from __future__ import annotations

from collections import deque
from threading import Lock

from simbridge.audio.format import AudioFrame


class FrameBuffer:
    def __init__(self, max_frames: int = 5) -> None:
        if max_frames <= 0:
            raise ValueError("max_frames must be positive")
        self._frames: deque[AudioFrame] = deque()
        self._max_frames = max_frames
        self._dropped_frames = 0
        self._lock = Lock()

    @property
    def dropped_frames(self) -> int:
        with self._lock:
            return self._dropped_frames

    def __len__(self) -> int:
        with self._lock:
            return len(self._frames)

    def push(self, frame: AudioFrame) -> None:
        with self._lock:
            if len(self._frames) >= self._max_frames:
                self._frames.popleft()
                self._dropped_frames += 1
            self._frames.append(frame)

    def pop(self) -> AudioFrame | None:
        with self._lock:
            return self._frames.popleft() if self._frames else None

    def clear(self) -> None:
        with self._lock:
            self._frames.clear()
