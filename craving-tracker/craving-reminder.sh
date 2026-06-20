#!/usr/bin/env bash
#
# craving-reminder.sh — fire a desktop notification nudging you to check in,
# and (optionally) print today's rewiring stats. Designed for cron / launchd.
#
# Usage:
#   ./craving-reminder.sh            # just the nudge
#   ./craving-reminder.sh digest     # nudge + this week's stats in the message
#
# It auto-detects a notifier: macOS osascript, Linux notify-send, or termux.
# Falls back to stdout so it still works from a plain cron mailer.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-python3}"
TITLE="Rewire check-in"
BODY="Any cravings today? Each one you log is a pathway rebuilt. Run: craving"

if [[ "${1:-}" == "digest" ]]; then
  STATS="$("$PY" "$HERE/craving.py" stats 2>/dev/null | sed -n '3,8p' | sed 's/^[[:space:]]*//')"
  [[ -n "$STATS" ]] && BODY="$STATS"
fi

notify() {
  if command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"$BODY\" with title \"$TITLE\""
  elif command -v termux-notification >/dev/null 2>&1; then
    termux-notification --title "$TITLE" --content "$BODY"
  elif command -v notify-send >/dev/null 2>&1; then
    notify-send "$TITLE" "$BODY"
  else
    printf '\n%s\n%s\n\n' "$TITLE" "$BODY"
  fi
}

notify
