#!/usr/bin/env bash
# Sends a Telegram message on Claude Code Notification/Stop events.
# Requires: curl, jq, TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in the environment.
# Usage: telegram-notify.sh <Notification|Stop>, hook input JSON on stdin.

EVENT="$1"

if ! command -v curl &>/dev/null || ! command -v jq &>/dev/null; then
  exit 0
fi

if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ]; then
  exit 0
fi

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')
PROJECT=$(basename "${CWD:-unknown}")

if [ "$EVENT" = "Notification" ]; then
  MESSAGE=$(echo "$INPUT" | jq -r '.message // "needs your input"')
  TEXT="[$PROJECT] $MESSAGE"
else
  TEXT="[$PROJECT] Claude finished"
fi

curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
  --data-urlencode "text=${TEXT}" \
  > /dev/null 2>&1 || true
