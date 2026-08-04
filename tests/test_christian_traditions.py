from __future__ import annotations

import sys
import unittest
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_christian_traditions import (
    FORCED_WORD_CODES,
    PREFERRED_PREFIXES,
    TARGET_SPECS,
    build_entries,
    coding_word,
    expected_dictionary_texts,
    load_manifest,
)
from tools.xmjd6_codes import code_candidates, iter_dictionary_rows, load_character_codes


class ChristianTraditionDictionaryTests(unittest.TestCase):
    def test_generated_dictionaries_are_current_and_separate(self) -> None:
        expected, _ = expected_dictionary_texts(ROOT)
        self.assertEqual(
            {path.name for path in expected},
            {
                "xmjd6.protestantism.dict.yaml",
                "xmjd6.orthodoxy.dict.yaml",
                "xmjd6.oriental.dict.yaml",
                "xmjd6.assyrian.dict.yaml",
            },
        )
        for path, text in expected.items():
            self.assertEqual(path.read_text(encoding="utf-8-sig"), text)

    def test_each_tradition_has_distinctive_terms(self) -> None:
        rows = {
            filename: {word for word, _ in iter_dictionary_rows(ROOT / filename)}
            for _, filename, _, _ in TARGET_SPECS
        }
        self.assertTrue({"五个唯独", "奥格斯堡信纲"} <= rows["xmjd6.protestantism.dict.yaml"])
        self.assertTrue({"金口若望礼仪", "圣像屏"} <= rows["xmjd6.orthodoxy.dict.yaml"])
        self.assertTrue(
            {"东方正统教会", "台瓦西多"} <= rows["xmjd6.oriental.dict.yaml"]
        )
        self.assertTrue(
            {"东方亚述教会", "阿代和马里礼仪", "圣酵圣事"}
            <= rows["xmjd6.assyrian.dict.yaml"]
        )

    def test_generic_christian_words_and_inaccurate_label_are_excluded(self) -> None:
        manifest_words = {
            word
            for _, word in load_manifest(ROOT / "tools/christian_traditions_2026.txt")
        }
        self.assertTrue(
            {"祷告", "圣经", "教会", "基督徒", "牧师", "神父", "礼拜"}.isdisjoint(
                manifest_words
            )
        )
        # “一性论”不是东方正统教会所接受的自称；保留更准确的合性论术语。
        self.assertNotIn("一性论", manifest_words)

    def test_every_generated_code_is_legal_and_has_only_reviewed_collisions(self) -> None:
        character_codes = load_character_codes(
            ROOT / "xmjd6.danzi.dict.yaml", PREFERRED_PREFIXES
        )
        all_words_by_code: dict[str, set[str]] = defaultdict(set)
        for path in ROOT.glob("*.dict.yaml"):
            for word, code in iter_dictionary_rows(path):
                all_words_by_code[code].add(word)

        for _, filename, _, _ in TARGET_SPECS:
            for word, code in iter_dictionary_rows(ROOT / filename):
                self.assertIn(code, code_candidates(coding_word(word), character_codes), word)
                other_words = all_words_by_code[code] - {word}
                if code in set(FORCED_WORD_CODES.values()):
                    self.assertTrue(other_words, (word, code))
                else:
                    self.assertEqual(other_words, set(), (word, code))

        colliding_specialty_codes = {
            code
            for _, filename, _, _ in TARGET_SPECS
            for word, code in iter_dictionary_rows(ROOT / filename)
            if all_words_by_code[code] - {word}
        }
        self.assertEqual(colliding_specialty_codes, set(FORCED_WORD_CODES.values()))
        for word, code in FORCED_WORD_CODES.items():
            self.assertIn(
                (word, code),
                set(iter_dictionary_rows(ROOT / "xmjd6.protestantism.dict.yaml")),
            )

    def test_multi_part_personal_names_use_a_middle_dot(self) -> None:
        protestant_words = {
            word
            for word, _ in iter_dictionary_rows(ROOT / "xmjd6.protestantism.dict.yaml")
        }
        self.assertTrue({"马丁·路德", "约翰·加尔文"} <= protestant_words)
        self.assertTrue({"马丁路德", "约翰加尔文"}.isdisjoint(protestant_words))

    def test_fixed_dictionary_conflicts_are_skipped(self) -> None:
        result = build_entries(ROOT)
        generated_names = {spec[1] for spec in TARGET_SPECS}
        occupied: dict[str, set[str]] = defaultdict(set)
        for path in ROOT.glob("*.dict.yaml"):
            if path.name in generated_names or path.name == "xmjd6.ice.dict.yaml":
                continue
            for word, code in iter_dictionary_rows(path):
                occupied[code].add(word)
        character_codes = load_character_codes(
            ROOT / "xmjd6.danzi.dict.yaml", PREFERRED_PREFIXES
        )
        for entry in result.entries:
            occupied[entry.code].add(entry.word)
        for word in result.skipped_no_free_code:
            self.assertTrue(
                all(
                    occupied.get(code)
                    for code in code_candidates(coding_word(word), character_codes)
                ),
                word,
            )

    def test_protestant_bible_terms_follow_the_chinese_union_version(self) -> None:
        manifest_words = {
            word
            for _, word in load_manifest(ROOT / "tools/christian_traditions_2026.txt")
        }
        self.assertTrue(
            {
                "和合本",
                "和合本修订版",
                "马太福音",
                "约翰福音",
                "使徒行传",
                "启示录",
                "耶利米书",
                "彼得前书",
                "哥林多后书",
                "帖撒罗尼迦后书",
                "雅各书",
            }
            <= manifest_words
        )
        self.assertTrue(
            {"玛窦福音", "若望福音", "宗徒大事录", "默示录", "耶肋米亚"}.isdisjoint(
                manifest_words
            )
        )

    def test_release_and_import_lists_include_all_four_dictionaries(self) -> None:
        extended = (ROOT / "xmjd6.extended.dict.yaml").read_text(encoding="utf-8")
        release = (ROOT / ".github/workflows/create-release.yml").read_text(
            encoding="utf-8"
        )
        for _, filename, dictionary_name, _ in TARGET_SPECS:
            self.assertIn(f"  - {dictionary_name}", extended)
            self.assertIn(filename, release)
            self.assertIn(filename.removesuffix(".dict.yaml") + ".txt", release)


if __name__ == "__main__":
    unittest.main()
