#!/usr/bin/env python3
"""Build the curated, low-collision Catholic terminology expansion."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.xmjd6_codes import (
    code_candidates,
    choose_code,
    load_character_code_options,
    load_character_codes,
)


ROOT = Path(__file__).resolve().parents[1]
TARGET_NAME = "xmjd6.catholicism.dict.yaml"
MANIFEST_NAME = "tools/catholicism_expansion_2026.txt"
START_MARKER = "# 2026-08-04 天主教词汇扩建 ==============================================="
END_MARKER = "# ============================ 天主教词汇扩建结束 ============================"

# These characters have more than one pronunciation or JianDao fly-key spelling.
# The selected prefix is the reading used by the Catholic terminology manifest.
PREFERRED_PHONETIC_PREFIXES = {
    "不": "bj",  # bù
    "丁": "dg",  # dīng
    "仇": "wd",  # chóu
    "传": "wt",  # chuán
    "会": "hb",  # huì
    "区": "ql",  # qū
    "合": "he",  # hé
    "召": "fz",  # zhào; F is the primary key, Q is its fly key
    "大": "ds",  # dà
    "哲": "fe",  # zhé; F is the primary key, Q is its fly key
    "折": "fe",  # zhé
    "提": "tk",  # tí
    "无": "wj",  # wú
    "末": "ml",  # mò
    "日": "rk",  # rì
    "斋": "fh",  # zhāi
    "期": "qk",  # qī
    "柜": "gb",  # guì
    "朝": "jz",  # cháo; J is the primary key, W is its fly key
    "省": "er",  # shěng
    "祭": "jk",  # jì
    "色": "se",  # sè
    "匙": "wk",  # chí
    "者": "fe",  # zhě
    "著": "qj",  # zhù
    "解": "jd",  # jiě
    "许": "xl",  # xǔ
    "行": "xg",  # xíng
    "超": "jz",  # chāo
    "追": "fb",  # zhuī
    "腊": "ls",  # là
    "豁": "hl",  # huò
    "降": "jx",  # jiàng
}

# Keep the conventional five-key code even though an obscure general-dictionary
# entry currently occupies it. This is an intentional, reviewed collision.
FORCED_WORD_CODES = {"婚姻圣召": "hyefa"}


@dataclass(frozen=True)
class Entry:
    category: str
    word: str
    code: str


@dataclass(frozen=True)
class BuildResult:
    entries: tuple[Entry, ...]
    skipped_existing: tuple[str, ...]
    skipped_no_free_code: tuple[str, ...]
    collisions: tuple[tuple[str, str, tuple[str, ...]], ...]
    allowed_collisions: tuple[tuple[str, str, tuple[str, ...]], ...]


def strip_expansion_section(text: str) -> str:
    has_start = START_MARKER in text
    has_end = END_MARKER in text
    if has_start != has_end:
        raise ValueError("Catholicism expansion has only one boundary marker")
    if not has_start:
        return text

    before, remainder = text.split(START_MARKER, 1)
    _, after = remainder.split(END_MARKER, 1)
    return before.rstrip() + after.lstrip("\r\n")


def iter_rows_from_text(text: str):
    in_data = False
    for line in text.splitlines():
        if line.strip() == "...":
            in_data = True
            continue
        if not in_data or not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) >= 2 and fields[0] and fields[1]:
            yield fields[0], fields[1]


def load_manifest(path: Path) -> tuple[tuple[str, str], ...]:
    category: str | None = None
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            category = line[2:].strip()
            continue
        if line.startswith("#"):
            continue
        if category is None:
            raise ValueError(f"{path}:{line_number}: term appears before a category")
        if line in seen:
            raise ValueError(f"{path}:{line_number}: duplicate term {line!r}")
        seen.add(line)
        rows.append((category, line))
    return tuple(rows)


def validate_phonetic_selections(
    manifest_rows: tuple[tuple[str, str], ...],
    code_options: dict[str, tuple[str, ...]],
) -> None:
    missing: dict[str, set[str]] = defaultdict(set)
    for _, word in manifest_rows:
        positions = range(len(word)) if len(word) <= 3 else (0, 1, 2, len(word) - 1)
        for position in positions:
            character = word[position]
            prefixes = {code[:2] for code in code_options.get(character, ())}
            relevant = prefixes if len(word) == 2 else {prefix[0] for prefix in prefixes}
            if len(relevant) > 1 and character not in PREFERRED_PHONETIC_PREFIXES:
                missing[character].add(word)
    if missing:
        details = "; ".join(
            f"{character}: {', '.join(sorted(words))}"
            for character, words in sorted(missing.items())
        )
        raise ValueError(f"ambiguous pronunciations require a preferred code: {details}")


def build_entries(root: Path = ROOT) -> BuildResult:
    # xmjd6.ice is generated after, and deliberately has lower priority than,
    # the curated Catholic dictionary. Letting its broad code coverage reserve
    # codes here would make the curated output unstable on every upstream sync.
    dictionary_paths = [
        path
        for path in sorted(root.glob("*.dict.yaml"))
        if path.name != "xmjd6.ice.dict.yaml"
    ]
    target = root / TARGET_NAME
    manifest_rows = load_manifest(root / MANIFEST_NAME)
    code_options = load_character_code_options(root / "xmjd6.danzi.dict.yaml")
    validate_phonetic_selections(manifest_rows, code_options)
    character_codes = load_character_codes(
        root / "xmjd6.danzi.dict.yaml", PREFERRED_PHONETIC_PREFIXES
    )

    occupied: dict[str, set[str]] = defaultdict(set)
    existing_words: set[str] = set()
    for path in dictionary_paths:
        text = path.read_text(encoding="utf-8-sig")
        if path == target:
            text = strip_expansion_section(text)
        for word, code in iter_rows_from_text(text):
            existing_words.add(word)
            occupied[code].add(word)

    entries: list[Entry] = []
    skipped_existing: list[str] = []
    skipped_no_free_code: list[str] = []
    for category, word in manifest_rows:
        if word in existing_words:
            skipped_existing.append(word)
            continue
        try:
            forced_code = FORCED_WORD_CODES.get(word)
            if forced_code is not None:
                if forced_code not in code_candidates(word, character_codes):
                    raise ValueError(f"forced code {forced_code!r} is not valid for {word!r}")
                code = forced_code
            else:
                code = choose_code(word, character_codes, occupied)
        except ValueError:
            code = None
        if code is None:
            skipped_no_free_code.append(word)
            continue
        entries.append(Entry(category, word, code))
        occupied[code].add(word)

    collisions: list[tuple[str, str, tuple[str, ...]]] = []
    allowed_collisions: list[tuple[str, str, tuple[str, ...]]] = []
    for entry in entries:
        other_words = occupied[entry.code] - {entry.word}
        if other_words:
            collision = (entry.word, entry.code, tuple(sorted(other_words)))
            if FORCED_WORD_CODES.get(entry.word) == entry.code:
                allowed_collisions.append(collision)
            else:
                collisions.append(collision)

    return BuildResult(
        entries=tuple(entries),
        skipped_existing=tuple(skipped_existing),
        skipped_no_free_code=tuple(skipped_no_free_code),
        collisions=tuple(collisions),
        allowed_collisions=tuple(allowed_collisions),
    )


def render_section(entries: tuple[Entry, ...]) -> str:
    lines = [
        START_MARKER,
        "# 按键道六码规则生成；优先避开仓库其他词典占码，人工覆盖项除外。",
        "# 来源清单：tools/catholicism_expansion_2026.txt",
    ]
    current_category: str | None = None
    for entry in entries:
        if entry.category != current_category:
            lines.extend(("", f"# -------------------- {entry.category} --------------------"))
            current_category = entry.category
        lines.append(f"{entry.word}\t{entry.code}")
    lines.extend(("", END_MARKER))
    return "\n".join(lines) + "\n"


def expected_dictionary_text(root: Path = ROOT) -> tuple[str, BuildResult]:
    target = root / TARGET_NAME
    base = strip_expansion_section(target.read_text(encoding="utf-8-sig")).rstrip()
    result = build_entries(root)
    return base + "\n\n" + render_section(result.entries), result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true", help="write the generated section")
    action.add_argument("--check", action="store_true", help="check that the section is current")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expected, result = expected_dictionary_text(ROOT)
    target = ROOT / TARGET_NAME
    if result.collisions:
        print(f"Refusing to write {len(result.collisions)} colliding entries.", file=sys.stderr)
        return 1

    if args.check:
        actual = target.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        if actual != expected:
            print(f"{TARGET_NAME} expansion is stale; run with --write.", file=sys.stderr)
            return 1
    else:
        target.write_text(expected, encoding="utf-8", newline="\n")

    print(
        f"Catholicism expansion: {len(result.entries)} added, "
        f"{len(result.skipped_existing)} existing, "
        f"{len(result.skipped_no_free_code)} without a free code, "
        f"{len(result.allowed_collisions)} reviewed collision."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
