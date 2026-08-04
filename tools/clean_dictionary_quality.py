#!/usr/bin/env python3
"""Clean high-confidence corruption and abusive junk from non-danzi dictionaries."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from itertools import product
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.xmjd6_codes import load_character_code_options


ROOT = Path(__file__).resolve().parents[1]
TARGET_NAMES = (
    "xmjd6.cizu.dict.yaml",
    "xmjd6.fjcy.dict.yaml",
    "pinyin_simp.dict.yaml",
)

ROW_REPLACEMENTS = {
    "xmjd6.cizu.dict.yaml": {
        "不成其为\tbjqwvvv": "不成其为\tbjqwvv",
        "布甲鞋\tbjxvviv": "布甲鞋\tbjxviv",
        "钡盐\tbwyfivv": "钡盐\tbwyfiv",
        "都招\tddfzu2": "都招\tddfzu",
        "搭着\tdsfeio ": "搭着\tdsfeio",
        "这根\tfegnosss": "这根\tfegn",
        "中间调\tfjdiooo": "中间调\tfjdioo",
        "出阁\tjjgeaoa": "出阁\tjjgeao",
        "速听\tsjtgV": "速听\tsjtgv",
        "淡啦\ttflsa.碳蜡\ttflsv": "淡啦\tdflsa\n碳蜡\ttflsv",
        "养恩\typxn~": "养恩\typxn",
        "于死地\tysdvvvv": "于死地\tysdvvv",
        "还不认账\tbhrq": "还不认账\thbrq",
        "不会冷\tbhrvio": "不会冷\tbhlvio",
        "板蓝根颗粒\tblgnv": "板蓝根颗粒\tblglv",
        "脾胃虚弱\tbwxr": "脾胃虚弱\tpwxr",
        "不用挣扎\tbyffv": "不用挣扎\tbyqfv",
    },
    "xmjd6.fjcy.dict.yaml": {
        "基莲\tjklmvii": "基莲\tjklmvi",
    },
    "pinyin_simp.dict.yaml": {
        "袮\tni\t51": "袮\tmi\t51",
        "胊\txu\t1": "胊\tqu\t1",
    },
}

ROW_REMOVALS = {
    "xmjd6.cizu.dict.yaml": {
        "不必这样\tbbfq",
        "练但三等分\tlmdx",
    },
    "pinyin_simp.dict.yaml": {
        "汩\tmi\t12",
        "不\tdun\t3",
        "沐\tshu\t21",
    },
}

# These patterns are unambiguously abusive, obscene, or discriminatory in a
# general-purpose input dictionary. Clinical and legal terms are deliberately
# not included.
REJECTED_SUBSTRINGS = (
    "肏",
    "操你妈",
    "操你大爷",
    "草尼玛",
    "傻逼",
    "煞笔",
    "妈逼",
    "妈屄",
    "鸡巴",
    "几把",
    "妈卖批",
    "你妈的胎盘",
    "支那",
    "黑鬼",
    "日本鬼子",
    "小日本",
    "洋鬼子",
)

REJECTED_EXACT_WORDS = {
    "沙比",
}

# Myitkyina is a valid place name, not the slur caught by the substring rule.
ALLOWLIST = {
    "密支那",
}


@dataclass(frozen=True)
class Result:
    path: Path
    replacements: int
    removals: int
    changed: bool


def valid_word_codes(word: str, options: dict[str, tuple[str, ...]]) -> set[str]:
    """Return every standard 3-6 key code supported by the single-char table."""
    if len(word) < 2 or any(character not in options for character in word):
        return set()

    valid: set[str] = set()
    for full_codes in product(*(options[character] for character in word)):
        if len(word) == 2:
            base = full_codes[0][:2] + full_codes[1][:2]
            auxiliary = (full_codes[0][2], full_codes[1][2])
        elif len(word) == 3:
            base = "".join(code[0] for code in full_codes)
            auxiliary = tuple(code[2] for code in full_codes)
        else:
            base = "".join(code[0] for code in full_codes[:3]) + full_codes[-1][0]
            auxiliary = (full_codes[0][2], full_codes[1][2])
        valid.add(base)
        for length in range(1, min(len(auxiliary), 6 - len(base)) + 1):
            valid.add(base + "".join(auxiliary[:length]))
    return valid


def validate_replacements(root: Path = ROOT) -> None:
    options = load_character_code_options(root / "xmjd6.danzi.dict.yaml")
    errors: list[str] = []
    for filename, replacements in ROW_REPLACEMENTS.items():
        for old_row, new_rows in replacements.items():
            for new_row in new_rows.splitlines():
                word, code, *_ = new_row.split("\t")
                if filename == "pinyin_simp.dict.yaml":
                    if len(word) != len(code.split()):
                        errors.append(
                            f"{filename}: {old_row!r} -> {new_row!r} has mismatched syllables"
                        )
                    continue
                valid = valid_word_codes(word, options)
                if code not in valid:
                    errors.append(
                        f"{filename}: {old_row!r} -> {new_row!r} is not a standard code; "
                        f"candidates={sorted(valid)!r}"
                    )
    if errors:
        raise ValueError("\n".join(errors))


def is_rejected(text: str, code: str) -> bool:
    if text in ALLOWLIST:
        return False
    if text in REJECTED_EXACT_WORDS:
        return True
    if any(pattern in text for pattern in REJECTED_SUBSTRINGS):
        return True

    # Remove obvious pasted meme/abuse paragraphs while preserving intentional
    # classical-text shortcuts such as the existing 出师表 entries.
    if len(text) >= 20 and code == "nmsl":
        return True
    if text.startswith("每日一问：今天超越了吗"):
        return True
    if len(text) >= 20 and "🤙" in text:
        return True
    return False


def clean_text(path: Path, source: str) -> tuple[str, int, int]:
    replacements = ROW_REPLACEMENTS.get(path.name, {})
    row_removals = ROW_REMOVALS.get(path.name, set())
    output: list[str] = []
    replacement_count = 0
    removal_count = 0

    for line in source.splitlines():
        if line in row_removals:
            removal_count += 1
            continue
        replacement = replacements.get(line)
        if replacement is not None:
            output.extend(replacement.splitlines())
            replacement_count += 1
            continue

        fields = line.split("\t")
        if len(fields) >= 2 and is_rejected(fields[0], fields[1]):
            removal_count += 1
            continue
        output.append(line)

    trailing_newline = "\n" if source.endswith("\n") else ""
    return "\n".join(output) + trailing_newline, replacement_count, removal_count


def process(root: Path = ROOT, write: bool = False) -> list[Result]:
    results: list[Result] = []
    for name in TARGET_NAMES:
        path = root / name
        source = path.read_text(encoding="utf-8")
        cleaned, replacements, removals = clean_text(path, source)
        changed = cleaned != source
        if write and changed:
            path.write_text(cleaned, encoding="utf-8", newline="\n")
        results.append(Result(path, replacements, removals, changed))
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="apply the cleanup")
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if a cleanup would still change any target",
    )
    parser.add_argument(
        "--list-rejections",
        action="store_true",
        help="print every row selected by the content filter",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_replacements()
    if args.list_rejections:
        for name in TARGET_NAMES:
            path = ROOT / name
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                fields = line.split("\t")
                if len(fields) >= 2 and is_rejected(fields[0], fields[1]):
                    print(f"{name}:{number}: {line}")
        return 0
    results = process(write=args.write)
    for result in results:
        state = "changed" if result.changed else "clean"
        print(
            f"{result.path.name}: {state}; "
            f"replacements={result.replacements}, removals={result.removals}"
        )
    if args.check and any(result.changed for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
