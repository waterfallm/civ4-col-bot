"""
src.api.routes
==============
FastAPI route definitions for the civ4-col-bot API.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from src.game import actions
from src.game.state import GameState

log = logging.getLogger("civ4bot.routes")

router = APIRouter()

# ---------------------------------------------------------------------------
# Shared game state — injected at app startup via app.state (see main.py).
# Routes access it via the module-level reference set in main.py.
# ---------------------------------------------------------------------------
_state: GameState = None  # type: ignore[assignment]


def set_state(state: GameState) -> None:
    """Wire a GameState instance into the routes module."""
    global _state
    _state = state


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/next-turn")
def post_next_turn():
    """Trigger the 'next turn' action.

    Returns
    -------
    JSON
        ``{"status": "ok", "turn": <int>, "timestamp": <iso str>}`` on success.

    Raises
    ------
    HTTPException 409
        If the bot is disabled or a turn is already being processed.
    """
    result = actions.next_turn(_state)
    if not result["success"]:
        raise HTTPException(status_code=409, detail=result["reason"])
    return {
        "status": "ok",
        "turn": result["turn"],
        "timestamp": result["timestamp"],
    }


@router.get("/status")
def get_status():
    """Return the current bot status.

    Returns
    -------
    JSON
        Snapshot of the current GameState.
    """
    return _state.to_dict()


@router.post("/bot/enable")
def post_bot_enable():
    """Enable the bot."""
    _state.enable()
    log.info("Bot enabled via API at %s", datetime.now(tz=timezone.utc).isoformat())
    return {"status": "ok", "bot_enabled": True}


@router.post("/bot/disable")
def post_bot_disable():
    """Disable the bot."""
    _state.disable()
    log.info("Bot disabled via API at %s", datetime.now(tz=timezone.utc).isoformat())
    return {"status": "ok", "bot_enabled": False}
