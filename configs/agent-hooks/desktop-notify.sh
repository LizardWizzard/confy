#!/usr/bin/env bash
# Shows a desktop notification on Claude Code Notification/Stop events.
# Writes a kitty OSC 99 notification to Claude's terminal, so the terminal
# (Konsole, kitty) shows it and focuses the right tab when it is clicked.
# Falls back to notify-send when Claude has no terminal.
# Requires: jq; notify-send for the fallback.
# Usage: desktop-notify.sh <Notification|Stop>, hook input JSON on stdin.

EVENT="$1"

if ! command -v jq &>/dev/null; then
  exit 0
fi

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')
PROJECT=$(basename "${CWD:-unknown}")

if [ "$EVENT" = "Notification" ]; then
  MESSAGE=$(echo "$INPUT" | jq -r '.message // "needs your input"')
else
  MESSAGE="Claude finished"
fi
# OSC payload must not contain control characters.
TEXT=$(printf '[%s] %s' "$PROJECT" "$MESSAGE" | tr -d '\000-\037\177')

# Hooks run without a terminal; find the nearest ancestor that has one.
TTY=
PID=$PPID
while [ "${PID:-1}" -gt 1 ]; do
  T=$(ps -o tty= -p "$PID" 2>/dev/null | tr -d ' ')
  if [ -n "$T" ] && [ "$T" != "?" ]; then
    TTY=/dev/$T
    break
  fi
  PID=$(ps -o ppid= -p "$PID" 2>/dev/null | tr -d ' ')
done

# Single chunk with i= and a=focus: Konsole splits multi-chunk notifications
# into separate popups, and only one with both focuses the tab on click.
if [ -n "$TTY" ] && [ -w "$TTY" ]; then
  # A reused id updates the earlier notification instead of showing a new one.
  if printf '\033]99;i=%s:a=focus;%s\033\\' "$(date +%s%N)" "$TEXT" > "$TTY" 2>/dev/null; then
    echo "desktop-notify: sent OSC 99 to $TTY (via pid $PID)" >&2
    exit 0
  fi
fi

echo "desktop-notify: no writable terminal (tty='$TTY'), using notify-send" >&2
if command -v notify-send &>/dev/null; then
  notify-send --app-name="Claude Code" "Claude Code" "$TEXT" > /dev/null 2>&1 || true
fi
