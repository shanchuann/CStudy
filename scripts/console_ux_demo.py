#!/usr/bin/env python3
"""Compatibility entry point: the implementation moved to console_ux.py.

The renderer and animation helpers are imported by cstudy.py, so they live at
the repository root. This shim keeps the earlier invocation working:

  python scripts/console_ux_demo.py [--render FILE.md] [--no-anim] [--force]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import console_ux  # noqa: E402  (import after sys.path setup)

if __name__ == "__main__":
    raise SystemExit(console_ux.main(sys.argv[1:]))
