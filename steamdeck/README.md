# Steam Deck Integration

Trigger Civ IV bot actions from Steam Deck back paddles (L4/R4/L5/R5) via Steam Input.

## Prerequisites

- Steam Deck in **Desktop Mode** (or Gaming Mode with Decky/custom button mapping)
- The civ4bot API server running on your Pi cluster at `civ4bot.local`
- `curl` installed (available by default on SteamOS)
- `libnotify` for desktop notifications (`notify-send`)

---

## 1. Copy scripts to the Steam Deck

Transfer the scripts from this directory to your Steam Deck:

```bash
# From your PC (replace with your Steam Deck's IP)
scp trigger_next_turn.sh toggle_bot.sh check_status.sh deck@steamdeck.local:~/civ4bot/
```

Or clone the repo directly on the Steam Deck:

```bash
# On the Steam Deck (Desktop Mode terminal)
git clone https://github.com/waterfallm/civ4-col-bot.git ~/civ4-col-bot
cd ~/civ4-col-bot/steamdeck
```

## 2. Make scripts executable

```bash
chmod +x ~/civ4bot/trigger_next_turn.sh
chmod +x ~/civ4bot/toggle_bot.sh
chmod +x ~/civ4bot/check_status.sh
```

---

## 3. Set up `civ4bot.local` DNS

The scripts point to `http://civ4bot.local` by default. You need to resolve this hostname on the Steam Deck.

### Option A: mDNS / Avahi (recommended)

If your Pi cluster broadcasts mDNS (most k3s setups do), this should just work. Verify with:

```bash
ping civ4bot.local
```

If it doesn't resolve, install Avahi on the Steam Deck:

```bash
sudo pacman -S avahi nss-mdns
sudo systemctl enable --now avahi-daemon
```

### Option B: `/etc/hosts` (simplest)

Add a static entry pointing to your Pi's IP address:

```bash
# Find your Pi's IP first
sudo sh -c 'echo "192.168.1.100  civ4bot.local" >> /etc/hosts'
```

Replace `192.168.1.100` with the actual IP of your k3s node.

### Option C: Override via environment variable

All scripts respect the `CIV4BOT_URL` environment variable:

```bash
export CIV4BOT_URL=http://192.168.1.100
~/civ4bot/trigger_next_turn.sh
```

---

## 4. Add scripts to Steam as non-Steam games

1. Open **Steam** in Desktop Mode
2. Click **Add a Game** → **Add a Non-Steam Game...**
3. Click **Browse** and navigate to `~/civ4bot/trigger_next_turn.sh`
4. Click **Add Selected Programs**
5. Repeat for `toggle_bot.sh` and `check_status.sh`
6. (Optional) Set a custom icon for each shortcut

---

## 5. Map back paddles via Steam Input

1. Open **Steam** → Library → find your Civ IV game (or the script shortcuts)
2. Click the **Controller** icon → **Edit Layout**
3. Navigate to **Back Grip Buttons**
4. Assign each paddle to **Run Command**:

| Paddle | Script | Action |
|--------|--------|--------|
| **L4** | `trigger_next_turn.sh` | Trigger next turn |
| **R4** | `check_status.sh` | Check bot status |
| **L5** | `toggle_bot.sh` | Toggle bot on/off |
| **R5** | *(your choice)* | *(e.g., another bot action)* |

Alternatively, use **Keyboard Shortcut** mode and bind a hotkey that triggers the script via a `.desktop` launcher.

---

## 6. Quick test

While in Desktop Mode, open a terminal and run:

```bash
# Check bot is reachable
~/civ4bot/check_status.sh

# Trigger a turn manually
~/civ4bot/trigger_next_turn.sh

# Toggle the bot off, then on
~/civ4bot/toggle_bot.sh
~/civ4bot/toggle_bot.sh
```

---

## Troubleshooting

### ❌ "Failed to reach bot" notification

1. **Check network**: Is the Steam Deck on the same Wi-Fi as the Pi cluster?
   ```bash
   ping civ4bot.local
   ```
2. **Check DNS**: Try accessing by IP directly:
   ```bash
   export CIV4BOT_URL=http://192.168.1.100
   ~/civ4bot/check_status.sh
   ```
3. **Check the pod**: On the Pi cluster:
   ```bash
   kubectl get pods -n civ4bot
   kubectl logs deployment/civ4bot -n civ4bot
   ```

### ❌ `notify-send` not found

Install `libnotify`:

```bash
sudo pacman -S libnotify
```

### ❌ Scripts not running in Gaming Mode

In Gaming Mode, scripts need to be launched as Steam shortcuts. Make sure you've added them as non-Steam games (see step 4 above). For button mapping to work in Gaming Mode, use Steam Input's **Run Command** action.

### ❌ DNS resolves but API returns errors

Check the bot's health endpoint directly:

```bash
curl http://civ4bot.local/healthz
# Expected: {"status": "ok"}

curl http://civ4bot.local/status
# Expected: {"turn": 0, "bot_enabled": true, ...}
```

If health check fails, restart the deployment:

```bash
# On the Pi cluster
kubectl rollout restart deployment/civ4bot -n civ4bot
```
