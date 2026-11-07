import pytest

from simbridge.audio.buffer import FrameBuffer
from simbridge.audio.format import AudioFrame, AudioFormat, PCM16_MONO_16K_20MS


def make_frame(sequence: int) -> AudioFrame:
    return AudioFrame(
        payload=bytes(PCM16_MONO_16K_20MS.bytes_per_frame),
        sequence=sequence,
    )


def test_canonical_frame_size() -> None:
    assert PCM16_MONO_16K_20MS.samples_per_channel == 320
    assert PCM16_MONO_16K_20MS.bytes_per_frame == 640


def test_audio_frame_rejects_wrong_payload_size() -> None:
    with pytest.raises(ValueError, match="Expected 640 bytes"):
        AudioFrame(payload=b"too short", sequence=0)


def test_audio_format_rejects_invalid_s16le_width() -> None:
    with pytest.raises(ValueError, match="2-byte"):
        AudioFormat(16000, 1, 4, 20)


def test_buffer_drops_oldest_frame_when_full() -> None:
    buffer = FrameBuffer(max_frames=2)
    buffer.push(make_frame(0))
    buffer.push(make_frame(1))
    buffer.push(make_frame(2))

    assert len(buffer) == 2
    assert buffer.dropped_frames == 1
    assert buffer.pop().sequence == 1
    assert buffer.pop().sequence == 2
    assert buffer.pop() is None


def test_buffer_requires_positive_capacity() -> None:
    with pytest.raises(ValueError):
        FrameBuffer(max_frames=0)
