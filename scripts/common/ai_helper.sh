#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXERCISE="$(basename "$(dirname "${1:-}")")"
exec bash "$ROOT/cstudy.sh" ai "$EXERCISE"
