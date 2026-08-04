#!/usr/bin/env python3
"""Update VERSION and all top-level Rime version fields together."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^(\s*(?:config_)?version:\s*)[\"']?\d{4}-\d{2}-\d{2}[\"']?", re.MULTILINE)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("date", nargs="?", default=dt.date.today().isoformat())
    args = parser.parse_args()
    try:
        dt.date.fromisoformat(args.date)
    except ValueError as exc:
        parser.error(str(exc))

    (ROOT / "VERSION").write_text(args.date + "\n", encoding="utf-8")
    changed = 0
    for path in sorted(ROOT.glob("*.yaml")):
        original = path.read_text(encoding="utf-8-sig")
        updated, count = VERSION_RE.subn(lambda match: f'{match.group(1)}"{args.date}"', original)
        if count and updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    print(f"Updated VERSION and {changed} YAML file(s) to {args.date}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
