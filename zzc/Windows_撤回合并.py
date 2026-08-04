#!/usr/bin/env python3
"""Windows/Pixi entry point for the shared XMJD6 ZZZC rollback core."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("Linux_撤回合并.py")), run_name="__main__")
