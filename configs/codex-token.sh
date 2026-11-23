#!/bin/sh
# Prints a provider API token from the Secret Service keyring, for codex
# [model_providers.<id>.auth] which expects the token on stdout.
# Usage: token.sh <service> <account>
#   e.g. token.sh zai codex          (ZAI provider)
#        token.sh aitunnel codex     (deepseek provider)
# Tokens are migrated into the keyring by setup.py; nothing is stored in env
# or on disk in plaintext.
set -eu
[ $# -eq 2 ] || { echo "usage: $0 <service> <account>" >&2; exit 1; }
exec secret-tool lookup service "$1" account "$2"
