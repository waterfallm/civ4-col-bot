"""
tests.test_next_turn
=====================
Basic tests for the next_turn action and the GameState class.
"""

import pytest

from src.game.actions import next_turn
from src.game.state import GameState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_state(**kwargs) -> GameState:
    """Return a fresh GameState, forwarding any keyword overrides."""
    return GameState(**kwargs)


# ---------------------------------------------------------------------------
# GameState.next_turn — happy path
# ---------------------------------------------------------------------------


def test_next_turn_increments_counter():
    """next_turn should increment the turn counter by 1."""
    state = make_state(bot_enabled=True)
    assert state.turn == 0
    result = next_turn(state)
    assert result["success"] is True
    assert result["turn"] == 1
    assert state.turn == 1


def test_next_turn_increments_multiple_times():
    """Successive calls should keep incrementing."""
    state = make_state(bot_enabled=True)
    for expected in range(1, 4):
        result = next_turn(state)
        assert result["success"] is True
        assert result["turn"] == expected


def test_next_turn_returns_timestamp():
    """next_turn result should include a non-empty ISO timestamp."""
    state = make_state(bot_enabled=True)
    result = next_turn(state)
    assert "timestamp" in result
    assert result["timestamp"]


def test_next_turn_records_last_action():
    """next_turn should update state.last_action and last_action_time."""
    state = make_state(bot_enabled=True)
    next_turn(state)
    assert state.last_action is not None
    assert state.last_action_time is not None


# ---------------------------------------------------------------------------
# Guard: bot disabled
# ---------------------------------------------------------------------------


def test_next_turn_fails_when_bot_disabled():
    """next_turn should fail when bot_enabled is False."""
    state = make_state(bot_enabled=False)
    result = next_turn(state)
    assert result["success"] is False
    assert "disabled" in result["reason"].lower()
    assert state.turn == 0


def test_next_turn_does_not_increment_when_disabled():
    """Turn counter must not change if the bot is disabled."""
    state = make_state(bot_enabled=True)
    next_turn(state)          # turn → 1
    state.disable()
    next_turn(state)          # should be rejected
    assert state.turn == 1


# ---------------------------------------------------------------------------
# Guard: double-trigger protection
# ---------------------------------------------------------------------------


def test_next_turn_rejects_while_processing():
    """A second call while processing is already True should be rejected."""
    state = make_state(bot_enabled=True)
    state.processing = True   # Simulate an in-flight request
    result = next_turn(state)
    assert result["success"] is False
    assert "processing" in result["reason"].lower()
    assert state.turn == 0


# ---------------------------------------------------------------------------
# GameState helpers
# ---------------------------------------------------------------------------


def test_game_state_enable_disable():
    """enable/disable should toggle bot_enabled."""
    state = make_state(bot_enabled=False)
    state.enable()
    assert state.bot_enabled is True
    state.disable()
    assert state.bot_enabled is False


def test_game_state_to_dict():
    """to_dict should return a complete serialisable snapshot."""
    state = make_state(bot_enabled=True)
    snapshot = state.to_dict()
    assert snapshot["bot_enabled"] is True
    assert snapshot["turn"] == 0
    assert snapshot["last_action"] is None
    assert snapshot["last_action_time"] is None
    assert snapshot["processing"] is False
