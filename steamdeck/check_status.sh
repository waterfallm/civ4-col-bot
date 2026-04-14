#!/bin/bash
# Check the current status of the Civ IV bot
# Map this to a Steam Deck button via Steam Input

BOT_URL="${CIV4BOT_URL:-http://civ4bot.local}"

RESPONSE=$(curl -s "${BOT_URL}/status")

if [ $? -ne 0 ]; then
    notify-send "Civ IV Bot" "❌ Bot unreachable at ${BOT_URL}" --icon=dialog-error
    exit 1
fi

# Extract key fields for the notification
TURN=$(echo "${RESPONSE}" | grep -o '"turn":[^,}]*' | cut -d: -f2 | tr -d ' ')
BOT_ENABLED=$(echo "${RESPONSE}" | grep -o '"bot_enabled":[^,}]*' | cut -d: -f2 | tr -d ' ')

if [ "${BOT_ENABLED}" = "true" ]; then
    STATUS_ICON="🟢"
    STATUS_TEXT="enabled"
else
    STATUS_ICON="🔴"
    STATUS_TEXT="disabled"
fi

notify-send "Civ IV Bot Status" "${STATUS_ICON} Bot ${STATUS_TEXT} | Turn: ${TURN}" --icon=input-gaming
