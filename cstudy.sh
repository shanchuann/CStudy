#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$ROOT/cstudy.py" "$@"
fi
if command -v python >/dev/null 2>&1; then
  exec python "$ROOT/cstudy.py" "$@"
fi
echo "CStudy requires Python 3.9+ (python3 or python) in PATH." >&2
exit 127
