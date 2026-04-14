#!/bin/bash
# Toggle the Civ IV bot on/off
# Map this to a Steam Deck button via Steam Input

BOT_URL="${CIV4BOT_URL:-http://civ4bot.local}"

# Check current status
STATUS=$(curl -s "${BOT_URL}/status")

if [ $? -ne 0 ]; then
    notify-send "Civ IV Bot" "❌ Failed to reach bot at ${BOT_URL}" --icon=dialog-error
    exit 1
fi

# Toggle based on current state
BOT_ENABLED=$(echo "${STATUS}" | grep -o '"bot_enabled":[^,}]*' | cut -d: -f2 | tr -d ' ')

if [ "${BOT_ENABLED}" = "true" ]; then
    RESPONSE=$(curl -s -X POST "${BOT_URL}/bot/disable")
    notify-send "Civ IV Bot" "🔴 Bot disabled" --icon=input-gaming
else
    RESPONSE=$(curl -s -X POST "${BOT_URL}/bot/enable")
    notify-send "Civ IV Bot" "🟢 Bot enabled" --icon=input-gaming
fi
