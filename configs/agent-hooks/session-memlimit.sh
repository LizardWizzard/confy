#!/usr/bin/env bash
# Move a codex/claude CLI session (+ already-spawned children) into a
# memory-limited cgroup, so a runaway child process gets OOM-killed inside the
# session's own group instead of dragging the whole box down (kernel OOM
# otherwise shoots the fattest victim - e.g. the 45G strata engine, 2026-11-23).
# Usage: session-memlimit.sh <client-name> [target-pid] [max] [high] [swapmax]
#   client-name  cgroup suffix under app.slice (codex, claude, ...)
#   target-pid   for standalone testing; default: climb from $PPID to the CLI
# Fails silently (exit 0) - a broken limit must never block a session start.
# Verify with: cat /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/app.slice/<name>-limit/cgroup.procs
set -u
name="${1:-cli}"; want_pid="${2:-}"; max="${3:-}"; high="${4:-}"; swap="${5:-}"

# Auto budget by SESSION MODEL (dr's request): sessions on local models get 5G
# (the engine legitimately holds ~45G), remote-provider sessions get 10G.
# Detection order: hook stdin .model -> codex rollout session_meta
# (provenance.model, looked up by session_id) -> claude transcript "model"
# fields -> ANTHROPIC/OPENAI base URL on loopback -> default remote.
# Explicit args 3-5 override. Re-fires (resume, new session) just rewrite
# memory.max in the existing cgroup in place.
is_local_model() {
  case "${1:-}" in
    *flashnext*|*inkling*|*-local*|*llama*) return 0 ;;
    *) return 1 ;;
  esac
}

local_mode=""
input=$(cat 2>/dev/null)
m=$(printf '%s' "$input" | jq -r '.model // empty' 2>/dev/null)
sid=$(printf '%s' "$input" | jq -r '.session_id // empty' 2>/dev/null)
tp=$(printf '%s' "$input" | jq -r '.transcript_path // empty' 2>/dev/null)

# codex: the rollout file written at session start records the model
if [ -z "$m" ] && [ -n "$sid" ]; then
  f=$(command ls -t ~/.codex/sessions/*/*/*/rollout-*"$sid".jsonl 2>/dev/null | head -1)
  [ -n "$f" ] && m=$(head -1 "$f" | jq -r '.payload.base_instructions.provenance.model // .payload.provenance.model // empty' 2>/dev/null)
fi
# claude: transcript lines carry message.model
if [ -z "$m" ] && [ -n "$tp" ] && [ -r "$tp" ]; then
  m=$(grep -m1 -o '"model": *"[^"]*"' "$tp" 2>/dev/null | sed 's/.*"model": *"//;s/"//')
fi
# either harness launched with a loopback provider base URL = local mode
if [ -z "$m" ]; then
  case "${ANTHROPIC_BASE_URL:-}${OPENAI_BASE_URL:-}" in
    *127.0.0.1*|*localhost*) local_mode=1 ;;
  esac
fi

if [ -z "$max" ]; then
  if [ -z "$local_mode" ] && is_local_model "$m"; then local_mode=1; fi
  if [ "$local_mode" = 1 ]; then max=5G; high=4G; swap=1G
  else max=10G; high=8G; swap=2G; fi
fi

# The user's own slice, so the limit follows the uid instead of assuming 1000.
uid=$(id -u 2>/dev/null) || exit 0
CG="/sys/fs/cgroup/user.slice/user-${uid}.slice/user@${uid}.service/app.slice/${name}-limit"
mkdir -p "$CG" 2>/dev/null || exit 0
echo "$max" > "$CG/memory.max" 2>/dev/null || exit 0
echo "$high" > "$CG/memory.high" 2>/dev/null
echo "$swap" > "$CG/memory.swap.max" 2>/dev/null

# Find the CLI process: the given pid, or climb from $PPID through shell
# wrappers (hooks are spawned as bash -c children of the CLI).
pid="$want_pid"
if [ -z "$pid" ]; then
  pid="$PPID"
  for _ in 1 2 3 4 5; do
    comm=$(cat "/proc/$pid/comm" 2>/dev/null) || break
    case "$comm" in
      codex|claude) break ;;
      bash|sh|zsh|dash) pid=$(awk '{print $4}' "/proc/$pid/stat" 2>/dev/null) ;;
      *) break ;;
    esac
    [ -n "$pid" ] && [ "$pid" -gt 1 ] 2>/dev/null || break
  done
fi
[ -n "$pid" ] && [ "$pid" -gt 1 ] 2>/dev/null || exit 0

# Move the CLI and every existing descendant (MCP servers may already be up).
collect() { echo "$1"; for c in $(pgrep -P "$1" 2>/dev/null); do collect "$c"; done; }
for p in $(collect "$pid" | sort -u); do
  echo "$p" > "$CG/cgroup.procs" 2>/dev/null
done
exit 0
