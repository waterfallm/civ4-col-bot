# civ4-col-bot

A rule-based bot for playing **Civilization IV: Colonization** (modded), controlled via a lightweight **REST API** so any remote process can drive the game.

## What is this?

`civ4-col-bot` exposes an HTTP API (built with [FastAPI](https://fastapi.tiangolo.com/)) that lets you control the Civ IV Colonization game from a **remote process** — no direct hooking into Civ IV's Python internals required.  The API server manages game state and triggers in-game actions.  Later it will communicate with the game process via named pipes, memory reading, or the game's own Python interface.

## Project structure

```
civ4-col-bot/
├── readme.md              ← This file
├── .gitignore
├── requirements.txt       ← Python dependencies
├── config.json            ← Bot configuration (host, port, logging, bot toggle)
├── src/
│   ├── main.py            ← FastAPI app entry point
│   ├── config.py          ← Config loader (reads config.json)
│   ├── api/
│   │   └── routes.py      ← API route definitions
│   └── game/
│       ├── state.py       ← GameState class
│       └── actions.py     ← next_turn() and future game actions
└── tests/
    └── test_next_turn.py  ← pytest tests
```

The `Assets/Python/` directory contains the legacy in-process Civ IV hook (from the earlier prototype) and is kept for reference.

## Installation

```bash
pip install -r requirements.txt
```

## Running the server

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`.  Interactive docs are at `http://localhost:8000/docs`.

## Configuration

Edit `config.json` to change the server address, port, or logging level:

```json
{
  "bot_enabled": true,
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "logging": {
    "level": "INFO"
  }
}
```

## API endpoints

### `GET /status`
Returns the current bot status.

```bash
curl http://localhost:8000/status
```

Example response:
```json
{
  "bot_enabled": true,
  "turn": 3,
  "last_action": "next_turn → turn 3",
  "last_action_time": "2024-01-01T12:00:00+00:00",
  "processing": false
}
```

---

### `POST /next-turn`
Triggers the "next turn" action.  Increments the turn counter and (in future) communicates with the game process.

```bash
curl -X POST http://localhost:8000/next-turn
```

Example response:
```json
{
  "status": "ok",
  "turn": 4,
  "timestamp": "2024-01-01T12:00:05+00:00"
}
```

Returns HTTP **409** if the bot is disabled or a turn is already processing.

---

### `POST /bot/enable`
Enable the bot.

```bash
curl -X POST http://localhost:8000/bot/enable
```

---

### `POST /bot/disable`
Disable the bot.

```bash
curl -X POST http://localhost:8000/bot/disable
```

## Running tests

```bash
pytest tests/ -v
```

## Roadmap

- [x] FastAPI server scaffold with `/next-turn`, `/status`, `/bot/enable`, `/bot/disable`
- [x] GameState class with turn counter, enable/disable, and double-trigger protection
- [x] pytest suite for next_turn logic
- [ ] Actual Civ IV game integration (named pipe / memory / Python interface)
- [ ] Rule engine for production, exploration, and diplomacy decisions
- [ ] City management and trade route logic
