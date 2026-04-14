"""
src.api.routes
==============
FastAPI route definitions for the civ4-col-bot API.
"""

import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from src.game import actions
from src.game.state import GameState

log = logging.getLogger("civ4bot.routes")

router = APIRouter()


# ---------------------------------------------------------------------------
# Dependency: resolve the shared GameState stored in app.state
# ---------------------------------------------------------------------------


def get_game_state(request: Request) -> GameState:
    """FastAPI dependency that retrieves the GameState from app.state."""
    return request.app.state.game_state


GameStateDep = Annotated[GameState, Depends(get_game_state)]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/next-turn")
def post_next_turn(state: GameStateDep):
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
    result = actions.next_turn(state)
    if not result["success"]:
        raise HTTPException(status_code=409, detail=result["reason"])
    return {
        "status": "ok",
        "turn": result["turn"],
        "timestamp": result["timestamp"],
    }


@router.get("/status")
def get_status(state: GameStateDep):
    """Return the current bot status.

    Returns
    -------
    JSON
        Snapshot of the current GameState.
    """
    return state.to_dict()


@router.post("/bot/enable")
def post_bot_enable(state: GameStateDep):
    """Enable the bot."""
    state.enable()
    log.info("Bot enabled via API at %s", datetime.now(tz=timezone.utc).isoformat())
    return {"status": "ok", "bot_enabled": True}


@router.post("/bot/disable")
def post_bot_disable(state: GameStateDep):
    """Disable the bot."""
    state.disable()
    log.info("Bot disabled via API at %s", datetime.now(tz=timezone.utc).isoformat())
    return {"status": "ok", "bot_enabled": False}
