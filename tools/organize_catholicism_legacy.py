#!/usr/bin/env python3
"""Add stable section dividers to the legacy Catholic dictionary rows."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.build_catholicism_expansion import START_MARKER as EXPANSION_START_MARKER


ROOT = Path(__file__).resolve().parents[1]
TARGET_NAME = "xmjd6.catholicism.dict.yaml"
START_MARKER = "# 2026-08-04 既有天主教词库分类 ==========================================="
END_MARKER = "# ============================ 既有词库分类结束 ============================"
DESCRIPTION = "# 保留原有词条、编码和候选顺序，仅按既有来源块添加分类分隔线。"
SECTIONS = (
    ("一文", "圣经辞汇、人物、地名、制度与名物"),
    ("艾俾欧尼派", "教理、神学、哲学、教会史与宗教研究"),
    ("圣秩", "圣事、礼仪、祷文与敬礼"),
)


def section_heading(title: str) -> str:
    return f"# -------------------- {title} --------------------"


def strip_owned_comments(lines: list[str]) -> list[str]:
    owned = {START_MARKER, END_MARKER, DESCRIPTION}
    owned.update(section_heading(title) for _, title in SECTIONS)
    return [line for line in lines if line not in owned]


def organize_dictionary_text(text: str) -> str:
    lines = strip_owned_comments(text.replace("\r\n", "\n").splitlines())
    try:
        expansion_index = lines.index(EXPANSION_START_MARKER)
        data_marker_index = lines.index("...")
    except ValueError as exc:
        raise ValueError("Catholic dictionary markers are incomplete") from exc
    if data_marker_index >= expansion_index:
        raise ValueError("dictionary data marker must precede the expansion section")

    prefix = lines[: data_marker_index + 1]
    legacy_rows = [
        line
        for line in lines[data_marker_index + 1 : expansion_index]
        if line.strip()
    ]
    expansion = lines[expansion_index:]

    anchors = {word: title for word, title in SECTIONS}
    found: set[str] = set()
    organized = prefix + ["", START_MARKER, DESCRIPTION]
    for line in legacy_rows:
        word = line.split("\t", 1)[0]
        title = anchors.get(word)
        if title is not None:
            organized.extend(("", section_heading(title)))
            found.add(word)
        organized.append(line)

    missing = [word for word, _ in SECTIONS if word not in found]
    if missing:
        raise ValueError(f"missing legacy section anchor(s): {', '.join(missing)}")

    organized.extend(("", END_MARKER, ""))
    organized.extend(expansion)
    return "\n".join(organized).rstrip() + "\n"


def expected_dictionary_text(root: Path = ROOT) -> str:
    target = root / TARGET_NAME
    return organize_dictionary_text(target.read_text(encoding="utf-8-sig"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true", help="write the section dividers")
    action.add_argument("--check", action="store_true", help="check that dividers are current")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = ROOT / TARGET_NAME
    expected = expected_dictionary_text(ROOT)
    if args.check:
        actual = target.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        if actual != expected:
            print(f"{TARGET_NAME} legacy sections are stale; run with --write.", file=sys.stderr)
            return 1
    else:
        target.write_text(expected, encoding="utf-8", newline="\n")
    print("Catholicism legacy sections: 3 categorized blocks, dictionary rows preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
