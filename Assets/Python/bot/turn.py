"""
bot.turn
========
Turn-management helpers for civ4-col-bot.

The Civ IV Python API is available at module level when this file runs inside
the game process.  For unit-testing outside the game the CyGame / ControlTypes
stubs defined at the bottom of this module are used automatically.
"""

import logging

log = logging.getLogger("civ4bot.turn")


def next_turn():
    """Trigger the 'End Turn' action in Civ IV Colonization.

    This function calls ``CyGame().doControl(ControlTypes.CONTROL_ENDTURN)``,
    which is the standard Civ IV Python API equivalent of pressing the
    *End Turn* button.

    Guards
    ------
    * Checks that it is currently the active (human) player's turn before
      issuing the command, so the bot never accidentally ends the turn during
      an AI phase.

    Side effects
    ------------
    Advances the game to the next turn for the active player.
    """
    try:
        game = CyGame()
        active_player = game.getActivePlayer()
        player = gc.getPlayer(active_player)

        # Guard: only end the turn when it is the active player's turn.
        if not game.isMPOption(MultiplayerOptionTypes.MPOPTION_SIMULTANEOUS_TURNS):
            # Single-player or sequential multiplayer — check whose turn it is.
            if game.getActiveTeam() != player.getTeam():
                log.warning(
                    "next_turn called but it is not the active player's turn — skipping."
                )
                return

        log.info("Bot triggering End Turn for player %s.", active_player)
        game.doControl(ControlTypes.CONTROL_ENDTURN)
        log.debug("End Turn command issued successfully.")

    except Exception as exc:  # pragma: no cover — only reachable inside the game
        log.error("next_turn encountered an error: %s", exc)
        raise


# ---------------------------------------------------------------------------
# Lightweight stubs so this module can be imported and tested outside the
# Civ IV game process (where the built-in CyGame / ControlTypes do not exist).
# ---------------------------------------------------------------------------

try:
    # These names are injected into Python's global namespace by the game engine.
    CyGame  # noqa: F821
    ControlTypes  # noqa: F821
    MultiplayerOptionTypes  # noqa: F821
    gc  # noqa: F821
except NameError:
    import types

    class _FakeControlTypes:
        CONTROL_ENDTURN = 14  # Matches the value in Civ IV's ControlTypes enum

    class _FakeMultiplayerOptionTypes:
        MPOPTION_SIMULTANEOUS_TURNS = 0

    class _FakeTeam:
        def __init__(self, team_id):
            self._team_id = team_id

        def getTeam(self):
            return self._team_id

    class _FakeCyGame:
        def getActivePlayer(self):
            return 0

        def getActiveTeam(self):
            return 0

        def isMPOption(self, option):
            return False

        def doControl(self, control_type):
            log.debug("(stub) doControl called with control_type=%s", control_type)

    class _FakeGC:
        def getPlayer(self, player_id):
            return _FakeTeam(player_id)

    ControlTypes = _FakeControlTypes()
    MultiplayerOptionTypes = _FakeMultiplayerOptionTypes()
    gc = _FakeGC()

    def CyGame():  # noqa: N802 — matches the Civ IV global function name
        return _FakeCyGame()
