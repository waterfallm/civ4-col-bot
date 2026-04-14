#!/bin/bash
# Trigger next turn on the Civ IV bot
# Map this to a Steam Deck button via Steam Input

BOT_URL="${CIV4BOT_URL:-http://civ4bot.local}"

RESPONSE=$(curl -s -X POST "${BOT_URL}/next-turn")

if [ $? -ne 0 ]; then
    notify-send "Civ IV Bot" "❌ Failed to reach bot at ${BOT_URL}" --icon=dialog-error
    exit 1
fi

notify-send "Civ IV Bot" "⏭️ ${RESPONSE}" --icon=input-gaming
