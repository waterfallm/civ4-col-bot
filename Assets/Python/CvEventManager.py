"""
CvEventManager.py  —  civ4-col-bot entry point
===============================================
Override of Civ IV Colonization's CvEventManager that hooks the bot into the
game's event loop.

Installation
------------
1. Copy this file (and the ``bot/`` package next to it) into your mod's
   ``Assets/Python/`` directory:

       Mods/<YourMod>/Assets/Python/CvEventManager.py
       Mods/<YourMod>/Assets/Python/bot/__init__.py
       Mods/<YourMod>/Assets/Python/bot/turn.py

2. If your mod already has a ``CvEventManager.py``, merge the relevant
   sections (see the comments marked "BOT HOOK") instead of replacing the
   file outright.

3. Place ``config.yaml`` in a location accessible at runtime and set the
   path in ``_CONFIG_PATH`` below.

4. Launch the game, load your mod, and the bot will start running
   automatically on each of your turns.

Notes
-----
* Civ IV loads this file fresh each game session; there is no need to restart
  the game after editing it (a new game / load suffices).
* The original ``CvEventManager`` class lives in the game's built-in Python
  path.  We import it as ``_OriginalCvEventManager`` and delegate all events
  to it so existing mod behaviour is preserved.
"""

import logging
import os

# ---------------------------------------------------------------------------
# Load config (YAML) --------------------------------------------------------
# ---------------------------------------------------------------------------
# Adjust this path if you put config.yaml somewhere else.
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")

_bot_enabled = True   # safe default if config cannot be loaded
_log_level = "INFO"

try:
    import yaml  # PyYAML is not bundled with Civ IV; fall back gracefully
    with open(_CONFIG_PATH, "r") as _f:
        _cfg = yaml.safe_load(_f) or {}
    _bot_enabled = bool(_cfg.get("bot_enabled", True))
    _log_level = str(_cfg.get("log_level", "INFO")).upper()
except Exception:  # noqa: BLE001
    pass  # Use safe defaults defined above

# ---------------------------------------------------------------------------
# Logging setup -------------------------------------------------------------
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, _log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
_log = logging.getLogger("civ4bot.event_manager")

# ---------------------------------------------------------------------------
# Import bot modules --------------------------------------------------------
# ---------------------------------------------------------------------------
from bot.turn import next_turn  # noqa: E402

# ---------------------------------------------------------------------------
# Import the original CvEventManager so we can delegate to it ---------------
# ---------------------------------------------------------------------------
# Civ IV ships its own CvEventManager in the Python path.  We rename our
# import so there is no conflict with this class.
try:
    import CvEventManager as _base_module  # type: ignore[import]
    _OriginalCvEventManager = _base_module.CvEventManager
except (ImportError, AttributeError):
    # Outside the game (e.g. during development / testing), or when a circular
    # import occurs because this file itself is named CvEventManager.py,
    # provide a minimal no-op base class so this file is still importable.
    class _OriginalCvEventManager:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

        def onEndPlayerTurn(self, argsList):
            pass


# ---------------------------------------------------------------------------
# Bot's CvEventManager override ---------------------------------------------
# ---------------------------------------------------------------------------

class CvEventManager(_OriginalCvEventManager):
    """Drop-in replacement for Civ IV's CvEventManager.

    Inherits all vanilla/mod event handlers and adds bot logic on top.
    """

    def __init__(self, *args, **kwargs):
        super(CvEventManager, self).__init__(*args, **kwargs)
        _log.info(
            "civ4-col-bot CvEventManager initialised (bot_enabled=%s).",
            _bot_enabled,
        )

    # BOT HOOK ---------------------------------------------------------------
    def onEndPlayerTurn(self, argsList):
        """Called by the game at the end of each player's turn.

        We use this event to trigger the bot's End Turn action so the game
        advances automatically while the bot is active.

        ``argsList`` is ``(iGameTurn, iPlayer)`` as provided by the engine.
        """
        # Always delegate to the parent first so existing mod logic runs.
        super(CvEventManager, self).onEndPlayerTurn(argsList)

        if not _bot_enabled:
            _log.debug("Bot is disabled — skipping next_turn.")
            return

        game_turn, player_id = argsList[0], argsList[1]
        _log.debug(
            "onEndPlayerTurn: game_turn=%s, player_id=%s", game_turn, player_id
        )

        # BOT HOOK: trigger the bot's next-turn logic.
        next_turn()
