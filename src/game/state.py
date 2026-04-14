"""
src.game.state
==============
GameState tracks the mutable runtime state of the bot.
"""

import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from threading import Lock
from typing import Generator, Optional

log = logging.getLogger("civ4bot.state")


class GameState:
    """Thread-safe container for the bot's runtime state.

    Attributes
    ----------
    turn : int
        Current turn number, incremented on each successful next_turn call.
    bot_enabled : bool
        Whether the bot is allowed to trigger actions.
    last_action : Optional[str]
        Human-readable description of the last action taken.
    last_action_time : Optional[datetime]
        UTC timestamp of the last action.
    processing : bool
        True while a turn is actively being processed (prevents double-triggers).
    """

    def __init__(self, bot_enabled: bool = True) -> None:
        self.turn: int = 0
        self.bot_enabled: bool = bot_enabled
        self.last_action: Optional[str] = None
        self.last_action_time: Optional[datetime] = None
        self.processing: bool = False
        self._lock: Lock = Lock()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def enable(self) -> None:
        """Enable the bot."""
        with self._lock:
            self.bot_enabled = True
            log.info("Bot enabled.")

    def disable(self) -> None:
        """Disable the bot."""
        with self._lock:
            self.bot_enabled = False
            log.info("Bot disabled.")

    def record_action(self, description: str) -> None:
        """Record the last action with the current UTC timestamp."""
        with self._lock:
            self.last_action = description
            self.last_action_time = datetime.now(tz=timezone.utc)

    @contextmanager
    def acquire_processing(self) -> Generator[bool, None, None]:
        """Context manager that atomically claims the processing slot.

        Yields ``True`` if the slot was successfully acquired (caller should
        proceed) or ``False`` if another turn is already in progress (caller
        should abort).  The slot is always released on exit.

        Usage::

            with state.acquire_processing() as acquired:
                if not acquired:
                    return {"success": False, "reason": "Already processing a turn."}
                ...  # do work
        """
        with self._lock:
            if self.processing:
                acquired = False
            else:
                self.processing = True
                acquired = True
        try:
            yield acquired
        finally:
            if acquired:
                with self._lock:
                    self.processing = False

    def increment_turn(self) -> int:
        """Atomically increment the turn counter and return the new value."""
        with self._lock:
            self.turn += 1
            return self.turn

    def to_dict(self) -> dict:
        """Return a serialisable snapshot of the current state."""
        with self._lock:
            return {
                "bot_enabled": self.bot_enabled,
                "turn": self.turn,
                "last_action": self.last_action,
                "last_action_time": (
                    self.last_action_time.isoformat()
                    if self.last_action_time
                    else None
                ),
                "processing": self.processing,
            }
