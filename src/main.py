"""
src.main
========
FastAPI application entry point for civ4-col-bot.

Run with::

    uvicorn src.main:app --reload

"""

import logging

from fastapi import FastAPI

from src.api import routes
from src.config import config
from src.game.state import GameState

log = logging.getLogger("civ4bot.main")

app = FastAPI(
    title="civ4-col-bot API",
    description="Remote control API for the Civ IV Colonization bot.",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# Initialise game state from config and attach it to app.state so that route
# dependencies can retrieve it via request.app.state.game_state.
# ---------------------------------------------------------------------------
app.state.game_state = GameState(bot_enabled=config.get("bot_enabled", True))

app.include_router(routes.router)

log.info(
    "civ4-col-bot API server ready — bot_enabled=%s",
    app.state.game_state.bot_enabled,
)
