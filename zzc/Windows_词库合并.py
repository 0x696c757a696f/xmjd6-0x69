#!/usr/bin/env python3
"""Windows/Pixi entry point for the shared xmjd6 ZZZC merge core."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("Linux_词库合并.py")), run_name="__main__")
