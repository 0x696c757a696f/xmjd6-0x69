#!/usr/bin/env python3
"""Remove byte-identical duplicate rows from top-level Rime dictionaries."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def dedupe(path: Path) -> int:
    output: list[bytes] = []
    seen: set[bytes] = set()
    in_data = False
    removed = 0
    for line in path.read_bytes().splitlines(keepends=True):
        content = line.rstrip(b"\r\n")
        if not in_data:
            output.append(line)
            if content.strip() == b"...":
                in_data = True
            continue
        if not content.strip() or content.lstrip().startswith(b"#") or b"\t" not in content:
            output.append(line)
            continue
        if content in seen:
            removed += 1
            continue
        seen.add(content)
        output.append(line)
    if removed:
        path.write_bytes(b"".join(output))
    return removed


def main() -> int:
    total = 0
    for path in sorted(ROOT.glob("*.dict.yaml")):
        removed = dedupe(path)
        if removed:
            print(f"{path.name}: removed {removed} exact duplicate row(s)")
            total += removed
    print(f"Removed {total} exact duplicate row(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
