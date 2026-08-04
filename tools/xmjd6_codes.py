#!/usr/bin/env python3
"""Generate standard JianDao 6 word codes and choose low-collision variants."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path


def iter_dictionary_rows(path: Path) -> Iterable[tuple[str, str]]:
    in_data = False
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip() == "...":
            in_data = True
            continue
        if not in_data or not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) >= 2 and fields[0] and fields[1]:
            yield fields[0], fields[1]


def load_character_code_options(path: Path) -> dict[str, tuple[str, ...]]:
    candidates: dict[str, list[str]] = defaultdict(list)
    for text, code in iter_dictionary_rows(path):
        if len(text) == 1 and len(code) >= 3:
            candidates[text].append(code)
    return {character: tuple(codes) for character, codes in candidates.items()}


def load_character_codes(
    path: Path,
    preferred_prefixes: Mapping[str, str] | None = None,
) -> dict[str, str]:
    candidates = load_character_code_options(path)
    preferred_prefixes = preferred_prefixes or {}
    selected: dict[str, str] = {}
    for character, codes in candidates.items():
        prefix = preferred_prefixes.get(character)
        matching = codes if prefix is None else [code for code in codes if code.startswith(prefix)]
        if not matching:
            raise ValueError(f"no code for {character!r} starts with preferred prefix {prefix!r}")
        selected[character] = max(matching, key=len)
    return selected


def code_candidates(word: str, character_codes: Mapping[str, str]) -> list[str]:
    if len(word) < 2:
        raise ValueError("word codes require at least two characters")
    try:
        full_codes = [character_codes[character] for character in word]
    except KeyError as exc:
        raise ValueError(f"missing single-character code for {exc.args[0]!r}") from exc

    return code_candidates_from_full_codes(full_codes)


def code_candidates_from_full_codes(full_codes: Iterable[str]) -> list[str]:
    """Generate word codes from position-specific full single-character codes."""
    full_codes = list(full_codes)
    if len(full_codes) < 2:
        raise ValueError("word codes require at least two character codes")
    if any(len(code) < 3 for code in full_codes):
        raise ValueError("full single-character codes require at least three keys")

    if len(full_codes) == 2:
        base = full_codes[0][:2] + full_codes[1][:2]
    elif len(full_codes) == 3:
        base = "".join(code[0] for code in full_codes)
    else:
        base = "".join(code[0] for code in full_codes[:3]) + full_codes[-1][0]

    if len(full_codes) == 2:
        auxiliary = [full_codes[0][2], full_codes[1][2]]
    elif len(full_codes) == 3:
        auxiliary = [code[2] for code in full_codes]
    else:
        auxiliary = [full_codes[0][2], full_codes[1][2]]

    candidates = [base]
    for length in range(1, min(len(auxiliary), 6 - len(base)) + 1):
        candidates.append(base + "".join(auxiliary[:length]))
    return candidates


def choose_code(
    word: str,
    character_codes: Mapping[str, str],
    occupied: Mapping[str, set[str]],
) -> str | None:
    for code in code_candidates(word, character_codes):
        other_words = occupied.get(code, set()) - {word}
        if not other_words:
            return code
    return None


def load_occupied_codes(paths: Iterable[Path]) -> dict[str, set[str]]:
    occupied: dict[str, set[str]] = defaultdict(set)
    for path in paths:
        for word, code in iter_dictionary_rows(path):
            occupied[code].add(word)
    return dict(occupied)
