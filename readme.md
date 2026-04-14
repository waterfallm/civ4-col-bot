# civ4-col-bot

A rule-based bot for playing **Civilization IV: Colonization** (modded), with a remote API server and Steam Deck button integration.

## Architecture

```
┌──────────────┐    HTTP POST     ┌─────────────────────┐     ┌──────────────┐
│  Steam Deck  │ ───────────────► │  Pi Cluster (k3s)   │     │  Gaming PC   │
│  Button Press│  /next-turn      │  civ4bot.local       │ ──► │  Civ IV Game │
│  (Wi-Fi)     │                  │  FastAPI Pod         │     │              │
└──────────────┘                  └─────────────────────┘     └──────────────┘
```

## What is this?

`civ4-col-bot` has two layers:

1. **In-game hook** — hooks into Civ IV Colonization's Python scripting system (`CvEventManager`) to automate decisions inside the game process.
2. **Remote API server** — a FastAPI server running on a Raspberry Pi k3s cluster, exposing HTTP endpoints so you can trigger bot actions from any device on the same network (including a Steam Deck back-paddle button).

## Project structure

```
Assets/Python/          ← Drop into your mod's Assets/Python directory
├── CvEventManager.py   ← Override that hooks the bot into the game event loop
└── bot/
    ├── __init__.py
    └── turn.py         ← next_turn() and future turn-management logic
src/                    ← FastAPI server
├── main.py             ← Application entry point
├── config.py           ← Config loader
├── api/
│   └── routes.py       ← HTTP endpoints (/next-turn, /status, /healthz, …)
└── game/
    ├── actions.py      ← Bot actions (next_turn, etc.)
    └── state.py        ← Thread-safe GameState
k8s/                    ← Kubernetes manifests for k3s on Raspberry Pi
steamdeck/              ← Shell scripts for Steam Deck button triggers
config.json             ← Bot settings (bot_enabled, server, logging)
Dockerfile              ← Multi-stage ARM64 Docker image
deploy.sh               ← One-command build + deploy to k3s
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/next-turn` | Trigger next turn (returns `{"status":"ok","turn":<n>}`) |
| `GET`  | `/status` | Bot state snapshot |
| `POST` | `/bot/enable` | Enable the bot |
| `POST` | `/bot/disable` | Disable the bot |
| `GET`  | `/healthz` | Kubernetes liveness/readiness probe |

## Quick start — local development

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload

# Trigger a turn
curl -X POST http://localhost:8000/next-turn

# Check status
curl http://localhost:8000/status
```

## Deployment to k3s on Raspberry Pi (ARM64)

### Prerequisites

- Raspberry Pi cluster running k3s (with Traefik ingress — the default)
- Docker installed on the Pi
- `kubectl` configured to reach the cluster

### One-command deploy

Run this on the Pi (or from a machine with Docker/kubectl pointing at the Pi):

```bash
chmod +x deploy.sh
./deploy.sh
```

This will:
1. Build the ARM64 Docker image locally (`civ4bot:latest`)
2. Apply all Kubernetes manifests in `k8s/`
3. Wait for the rollout to complete

### Manual deploy steps

```bash
# Build ARM64 image
docker build -t civ4bot:latest .

# Apply manifests
kubectl apply -f k8s/

# Verify
kubectl get pods -n civ4bot
curl http://civ4bot.local/healthz
```

### Updating config without rebuilding

Edit `k8s/configmap.yaml` and reapply:

```bash
kubectl apply -f k8s/configmap.yaml
kubectl rollout restart deployment/civ4bot -n civ4bot
```

## Steam Deck button setup

See [`steamdeck/README.md`](steamdeck/README.md) for the full guide, including:

- How to copy scripts to the Steam Deck
- How to set up `civ4bot.local` DNS (mDNS or `/etc/hosts`)
- How to add scripts as non-Steam games
- How to map back paddles (L4/R4/L5/R5) via Steam Input
- Troubleshooting

### Quick summary

```bash
# On the Steam Deck (Desktop Mode)
chmod +x steamdeck/*.sh

# Test connectivity
steamdeck/check_status.sh

# Trigger a turn manually
steamdeck/trigger_next_turn.sh
```

## In-game mod installation

1. Copy `Assets/Python/` into your mod's `Assets/Python/` directory.
2. Edit `config.json` to set `bot_enabled: true`.
3. Launch Civ IV Colonization with your mod — the bot hooks into the event loop automatically.

> **Note:** If your mod already has a `CvEventManager.py`, merge the relevant sections rather than replacing the file.

## Requirements

- Python 3.11+ (API server)
- Civilization IV: Colonization with Python modding support (in-game hook)
- Docker + kubectl (deployment)

## Configuration

See `config.json`:

```json
{
  "bot_enabled": true,
  "server": { "host": "0.0.0.0", "port": 8000 },
  "logging": { "level": "INFO" }
}
```

## Running tests

```bash
pip install -r requirements.txt
pytest
```

## Roadmap

- [x] Project scaffold and `next_turn` function
- [x] FastAPI remote API server
- [x] k3s Kubernetes deployment (ARM64 Raspberry Pi)
- [x] Steam Deck button integration
- [ ] Rule engine for production, exploration, and diplomacy decisions
- [ ] City management logic
- [ ] Trade and economics rules
