#!/usr/bin/env python3
"""Build the curated, collision-free Christian traditions dictionary."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.build_catholicism_expansion import PREFERRED_PHONETIC_PREFIXES
from tools.xmjd6_codes import (
    code_candidates,
    choose_code,
    iter_dictionary_rows,
    load_character_code_options,
    load_character_codes,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "tools/christian_traditions_2026.txt"
VERSION = "2026-08-04"
TARGET_SPECS = (
    (
        "新教：",
        "xmjd6.protestantism.dict.yaml",
        "xmjd6.protestantism",
        "新教专有词汇",
    ),
    (
        "东正教：",
        "xmjd6.orthodoxy.dict.yaml",
        "xmjd6.orthodoxy",
        "东正教专有词汇",
    ),
    (
        "东方正统教会：",
        "xmjd6.oriental.dict.yaml",
        "xmjd6.oriental",
        "东方正统教会专有词汇",
    ),
    (
        "东方亚述教会：",
        "xmjd6.assyrian.dict.yaml",
        "xmjd6.assyrian",
        "东方亚述教会与东方教会专有词汇",
    ),
)
PREFERRED_PREFIXES = {
    **PREFERRED_PHONETIC_PREFIXES,
    "兹": "zk",  # zī（盖兹）
    "卡": "ks",  # kǎ（卡托利科斯、哈奇卡尔等译名）
    "堡": "bz",  # bǎo（海德堡）
    "奇": "qk",  # qí（哈奇卡尔）
    "屏": "pg",  # píng（圣像屏）
    "石": "ek",  # shí
    "长": "qp",  # zhǎng（长老）
    "革": "ge",  # gé（改革）
    "万": "wf",  # wàn
    "乐": "yh",  # yuè（圣乐）
    "便": "bm",  # biàn（便雅悯）
    "其": "qk",  # qí
    "南": "nf",  # nán
    "参": "en",  # shēn（参孙）
    "坏": "hg",  # huài
    "契": "qk",  # qì
    "姆": "mj",  # mǔ
    "彻": "je",  # chè
    "擘": "bl",  # bò（擘饼）
    "更": "gr",  # gēng（更新）
    "查": "fs",  # chá（查理）
    "番": "pf",  # pān（西番雅）
    "约": "yh",  # yuē（约柜）
    "角": "jc",  # jiǎo（角油）
    "调": "dc",  # diào（八调经）
    "谷": "gj",  # gǔ（哈巴谷）
    "重": "wy",  # chóng（四重）
}

# These three canonical Chinese Union Version book names cannot be represented
# collision-free under the standard JianDao 6 formulas. The two 前/后 pairs
# have identical first three and last characters; 雅各书 has every legal suffix
# occupied by fixed local vocabulary. Keep only these reviewed final-code cases.
FORCED_WORD_CODES = {
    "哥林多后书": "gldevv",
    "帖撒罗尼迦后书": "tsleii",
    "雅各书": "ygevua",
}


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


def coding_word(word: str) -> str:
    """Remove display punctuation that does not participate in JianDao codes."""
    return word.replace("·", "")


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
        encoded_word = coding_word(word)
        positions = (
            range(len(encoded_word))
            if len(encoded_word) <= 3
            else (0, 1, 2, len(encoded_word) - 1)
        )
        for position in positions:
            character = encoded_word[position]
            prefixes = {code[:2] for code in code_options.get(character, ())}
            relevant = prefixes if len(word) == 2 else {prefix[0] for prefix in prefixes}
            if len(relevant) > 1 and character not in PREFERRED_PREFIXES:
                missing[character].add(word)
    if missing:
        details = "; ".join(
            f"{character}: {', '.join(sorted(words))}"
            for character, words in sorted(missing.items())
        )
        raise ValueError(f"ambiguous pronunciations require a preferred code: {details}")


def build_entries(root: Path = ROOT) -> BuildResult:
    generated_names = {spec[1] for spec in TARGET_SPECS}
    dictionary_paths = [
        path for path in sorted(root.glob("*.dict.yaml")) if path.name not in generated_names
    ]
    fixed_dictionary_paths = [
        path for path in dictionary_paths if path.name != "xmjd6.ice.dict.yaml"
    ]
    manifest_rows = load_manifest(root / MANIFEST_NAME)
    code_options = load_character_code_options(root / "xmjd6.danzi.dict.yaml")
    validate_phonetic_selections(manifest_rows, code_options)
    character_codes = load_character_codes(
        root / "xmjd6.danzi.dict.yaml", PREFERRED_PREFIXES
    )

    # ICE is regenerated after local dictionaries and can move a lower-priority
    # row to a longer legal code. A reviewed term that exists only in ICE is
    # deliberately migrated into its stable specialty dictionary; the next ICE
    # rebuild then removes the upstream duplicate.
    existing_words = {
        word
        for path in fixed_dictionary_paths
        for word, _ in iter_dictionary_rows(path)
    }
    occupied: dict[str, set[str]] = defaultdict(set)
    for path in fixed_dictionary_paths:
        for word, code in iter_dictionary_rows(path):
            occupied[code].add(word)

    entries: list[Entry] = []
    skipped_existing: list[str] = []
    skipped_no_free_code: list[str] = []
    for category, word in manifest_rows:
        if word in existing_words:
            skipped_existing.append(word)
            continue
        try:
            code = choose_code(coding_word(word), character_codes, occupied)
        except ValueError:
            code = None
        if code is None and word in FORCED_WORD_CODES:
            forced_code = FORCED_WORD_CODES[word]
            if forced_code not in code_candidates(coding_word(word), character_codes):
                raise ValueError(f"forced code {forced_code!r} is invalid for {word!r}")
            code = forced_code
        if code is None:
            skipped_no_free_code.append(word)
            continue
        entries.append(Entry(category, word, code))
        occupied[code].add(word)

    return BuildResult(
        entries=tuple(entries),
        skipped_existing=tuple(skipped_existing),
        skipped_no_free_code=tuple(skipped_no_free_code),
    )


def render_dictionary(
    result: BuildResult, category_prefix: str, dictionary_name: str, title: str
) -> str:
    lines = [
        "# Rime dictionary",
        "# encoding: utf-8",
        "#",
        f"# {title}",
        "# 收录经审核的传统专有词；新教词库另含《和合本》标准译语。",
        "---",
        f"name: {dictionary_name}",
        f'version: "{VERSION}"',
        "sort: original",
        "use_preset_vocabulary: false",
        "columns:",
        "  - text",
        "  - code",
        "...",
        "",
        "# 编码由 tools/build_christian_traditions.py 按键道六码规则生成。",
        "# 逐码避开固定本地词典；ICE 随后重建并为专题词让出合法码。",
        "# 固定词典中无空闲合法码的词不收录；三卷《和合本》书名为审核例外。",
        "# 审核清单：tools/christian_traditions_2026.txt",
    ]
    current_category: str | None = None
    for entry in result.entries:
        if not entry.category.startswith(category_prefix):
            continue
        if entry.category != current_category:
            lines.extend(("", f"# -------------------- {entry.category} --------------------"))
            current_category = entry.category
        lines.append(f"{entry.word}\t{entry.code}")
    return "\n".join(lines) + "\n"


def expected_dictionary_texts(root: Path = ROOT) -> tuple[dict[Path, str], BuildResult]:
    result = build_entries(root)
    texts = {
        root / filename: render_dictionary(result, category_prefix, dictionary_name, title)
        for category_prefix, filename, dictionary_name, title in TARGET_SPECS
    }
    return texts, result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expected, result = expected_dictionary_texts(ROOT)
    if args.check:
        stale = [
            path.name
            for path, text in expected.items()
            if not path.is_file()
            or path.read_text(encoding="utf-8-sig").replace("\r\n", "\n") != text
        ]
        if stale:
            print(
                "Christian tradition dictionaries are stale: " + ", ".join(stale),
                file=sys.stderr,
            )
            return 1
    else:
        for path, text in expected.items():
            path.write_text(text, encoding="utf-8", newline="\n")

    print(
        f"Christian traditions: {len(result.entries)} added, "
        f"{len(result.skipped_existing)} existing, "
        f"{len(result.skipped_no_free_code)} without a free legal code."
    )
    if result.skipped_no_free_code:
        print("Skipped without free code: " + ", ".join(result.skipped_no_free_code))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
