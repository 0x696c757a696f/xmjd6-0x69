#!/usr/bin/env python3
"""Compare the integrated rime-txjx commit with its current upstream ref."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "tools" / "upstream_code.lock.json"


def remote_commit(repository: str, ref: str) -> str:
    result = subprocess.run(
        ["git", "ls-remote", repository, ref],
        check=True,
        capture_output=True,
        text=True,
    )
    rows = [line.split() for line in result.stdout.splitlines() if line.strip()]
    if len(rows) != 1 or len(rows[0]) < 2:
        raise RuntimeError(f"cannot resolve {ref} from {repository}")
    return rows[0][0]


def build_report() -> dict[str, object]:
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    source = lock["upstreams"]["rime-txjx"]
    current = remote_commit(source["repository"], source["ref"])
    integrated = source["commit"]
    return {
        "repository": source["repository"],
        "ref": source["ref"],
        "integrated_commit": integrated,
        "current_commit": current,
        "update_available": current != integrated,
        "source_paths": source["source_paths"],
        "integration": source["integration"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument(
        "--fail-on-update",
        action="store_true",
        help="return exit code 10 when upstream has moved",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build_report()
    except (OSError, subprocess.CalledProcessError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
        print(f"rime-txjx check failed: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif report["update_available"]:
        print(
            "rime-txjx has changed: "
            f"{report['integrated_commit']} -> {report['current_commit']}"
        )
        print("Review and adapt the locked source paths; do not overwrite XMJD6 patches blindly.")
    else:
        print(f"rime-txjx is current at {report['integrated_commit']}")
    return 10 if args.fail_on_update and report["update_available"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
