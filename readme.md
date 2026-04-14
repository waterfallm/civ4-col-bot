# civ4-col-bot

A rule-based bot for playing **Civilization IV: Colonization** (modded), built on top of Civ IV's Python modding interface.

## What is this?

`civ4-col-bot` hooks into Civ IV Colonization's built-in Python scripting system (`CvEventManager` / `CvGameInterface`) to automate in-game decisions according to a set of user-defined rules. The bot runs inside the game process itself — no external process required.

## Project structure

```
Assets/Python/          ← Drop this into your mod's Assets/Python directory
├── CvEventManager.py   ← Override that hooks the bot into the game event loop
└── bot/
    ├── __init__.py
    └── turn.py         ← next_turn() and future turn-management logic
config.yaml             ← Bot settings (enable/disable, future rule parameters)
```

## Installation

1. Copy the contents of `Assets/Python/` into your mod's `Assets/Python/` directory (e.g. `Mods/<YourMod>/Assets/Python/`).
2. Edit `config.yaml` to enable the bot (`bot_enabled: true`) and set any other options.
3. Launch Civ IV Colonization and load your mod — the bot will automatically hook into the game's event loop.

> **Note:** If your mod already has a `CvEventManager.py`, merge the relevant sections rather than replacing the file outright.

## Requirements

- Civilization IV: Colonization (with Python modding support)
- Python 2.x (as shipped with Civ IV)

## Configuration

See `config.yaml` for all available settings. The key toggle is:

```yaml
bot_enabled: true   # Set to false to disable the bot entirely
```

## Roadmap

- [x] Project scaffold and `next_turn` function
- [ ] Rule engine for production, exploration, and diplomacy decisions
- [ ] City management logic
- [ ] Trade and economics rules
