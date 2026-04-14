"""
src.game.actions
================
Game actions that the bot can trigger.

At the moment only ``next_turn`` is implemented.  Future actions (move unit,
found city, trade route, etc.) will be added here as additional functions.
"""

import logging
import time
from datetime import datetime, timezone

from src.game.state import GameState

log = logging.getLogger("civ4bot.actions")

# Simulated processing delay (seconds).  Replace with real game communication
# once the Civ IV integration layer is in place.
_PROCESSING_DELAY = 0.1


def next_turn(state: GameState) -> dict:
    """Trigger the 'next turn' action.

    Guards
    ------
    * Fails if the bot is disabled.
    * Fails if a turn is already being processed (prevents double-triggers).

    Side effects
    ------------
    * Increments ``state.turn``.
    * Sets ``state.processing`` for the duration of processing.
    * Calls ``state.record_action``.

    Returns
    -------
    dict
        ``{"success": True, "turn": <new turn number>, "timestamp": <iso str>}``
        on success, or ``{"success": False, "reason": <str>}`` on failure.
    """
    timestamp = datetime.now(tz=timezone.utc).isoformat()
    log.info("next_turn triggered at %s", timestamp)

    if not state.bot_enabled:
        reason = "Bot is disabled."
        log.warning("next_turn rejected: %s", reason)
        return {"success": False, "reason": reason}

    with state.acquire_processing() as acquired:
        if not acquired:
            reason = "Already processing a turn."
            log.warning("next_turn rejected: %s", reason)
            return {"success": False, "reason": reason}

        log.info("Processing next turn (current turn=%d)…", state.turn)

        # ----------------------------------------------------------------
        # TODO: Replace this stub with actual Civ IV communication once the
        # integration layer is ready (e.g. named pipe, memory write, etc.).
        # ----------------------------------------------------------------
        time.sleep(_PROCESSING_DELAY)

        new_turn = state.increment_turn()

    state.record_action(f"next_turn → turn {new_turn}")
    log.info("next_turn complete. New turn=%d", new_turn)
    return {"success": True, "turn": new_turn, "timestamp": timestamp}

