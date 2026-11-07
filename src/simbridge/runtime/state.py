"""Explicit call and audio readiness state machine."""

from __future__ import annotations

from enum import StrEnum


class SessionState(StrEnum):
    DISCONNECTED = "disconnected"
    PHONE_PAIRED = "phone_paired"
    PHONE_CONNECTED = "phone_connected"
    HFP_AVAILABLE = "hfp_available"
    CALL_ACTIVE = "call_active"
    AUDIO_BRIDGED = "audio_bridged"
    AI_READY = "ai_ready"
    ERROR = "error"


class InvalidTransition(ValueError):
    """Raised when a requested state transition is not permitted."""


_ALLOWED_TRANSITIONS: dict[SessionState, frozenset[SessionState]] = {
    SessionState.DISCONNECTED: frozenset({
        SessionState.PHONE_PAIRED, SessionState.PHONE_CONNECTED, SessionState.ERROR
    }),
    SessionState.PHONE_PAIRED: frozenset({
        SessionState.PHONE_CONNECTED, SessionState.DISCONNECTED, SessionState.ERROR
    }),
    SessionState.PHONE_CONNECTED: frozenset({
        SessionState.HFP_AVAILABLE, SessionState.PHONE_PAIRED,
        SessionState.DISCONNECTED, SessionState.ERROR
    }),
    SessionState.HFP_AVAILABLE: frozenset({
        SessionState.CALL_ACTIVE, SessionState.PHONE_CONNECTED,
        SessionState.DISCONNECTED, SessionState.ERROR
    }),
    SessionState.CALL_ACTIVE: frozenset({
        SessionState.AUDIO_BRIDGED, SessionState.HFP_AVAILABLE,
        SessionState.PHONE_CONNECTED, SessionState.ERROR
    }),
    SessionState.AUDIO_BRIDGED: frozenset({
        SessionState.AI_READY, SessionState.CALL_ACTIVE,
        SessionState.HFP_AVAILABLE, SessionState.ERROR
    }),
    SessionState.AI_READY: frozenset({
        SessionState.AUDIO_BRIDGED, SessionState.CALL_ACTIVE,
        SessionState.HFP_AVAILABLE, SessionState.ERROR
    }),
    SessionState.ERROR: frozenset({SessionState.DISCONNECTED}),
}


class SessionStateMachine:
    """In-memory state tracker; it does not initiate phone or audio operations."""

    def __init__(self) -> None:
        self._state = SessionState.DISCONNECTED

    @property
    def state(self) -> SessionState:
        return self._state

    def transition(self, target: SessionState) -> SessionState:
        if target == self._state:
            return self._state
        if target not in _ALLOWED_TRANSITIONS[self._state]:
            raise InvalidTransition(
                f"Cannot transition from {self._state.value} to {target.value}"
            )
        self._state = target
        return self._state

    def reset(self) -> SessionState:
        self._state = SessionState.DISCONNECTED
        return self._state
