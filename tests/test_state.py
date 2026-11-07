import pytest

from simbridge.runtime.state import InvalidTransition, SessionState, SessionStateMachine


def test_happy_path_transitions_to_ai_ready() -> None:
    machine = SessionStateMachine()
    sequence = (
        SessionState.PHONE_PAIRED,
        SessionState.PHONE_CONNECTED,
        SessionState.HFP_AVAILABLE,
        SessionState.CALL_ACTIVE,
        SessionState.AUDIO_BRIDGED,
        SessionState.AI_READY,
    )
    for state in sequence:
        assert machine.transition(state) is state
    assert machine.state is SessionState.AI_READY


def test_invalid_transition_is_rejected() -> None:
    machine = SessionStateMachine()
    with pytest.raises(InvalidTransition):
        machine.transition(SessionState.AI_READY)


def test_error_requires_explicit_reset_path() -> None:
    machine = SessionStateMachine()
    machine.transition(SessionState.ERROR)
    with pytest.raises(InvalidTransition):
        machine.transition(SessionState.PHONE_CONNECTED)
    assert machine.transition(SessionState.DISCONNECTED) is SessionState.DISCONNECTED


def test_repeated_state_is_idempotent() -> None:
    machine = SessionStateMachine()
    assert machine.transition(SessionState.DISCONNECTED) is SessionState.DISCONNECTED
