from __future__ import annotations

import re
import unittest
from collections import defaultdict
from pathlib import Path

from tools.sync_upstream_dictionaries import (
    GeneratedRow,
    PINYIN_PREFIX_OVERRIDES,
    build_english_rows,
    build_ice_rows,
    load_lock,
    prune_ice_collisions,
    render_danzi,
    verify_generated_hashes,
)
from tools.xmjd6_codes import code_candidates_from_full_codes, iter_dictionary_rows


ROOT = Path(__file__).resolve().parents[1]


def source_text(*rows: str) -> str:
    return "# Rime dictionary\n---\nname: fixture\n...\n" + "\n".join(rows) + "\n"


class UpstreamDictionaryTests(unittest.TestCase):
    def test_position_specific_codes_follow_confirmed_fly_key_rules(self) -> None:
        self.assertEqual(
            code_candidates_from_full_codes(("zfu", "qjo", "qlv")),
            ["zqq", "zqqu", "zqquo", "zqquov"],
        )
        self.assertEqual(
            code_candidates_from_full_codes(("hya", "yba", "ero", "fzu")),
            ["hyef", "hyefa", "hyefaa"],
        )
        self.assertEqual(PINYIN_PREFIX_OVERRIDES["zhao"], "fz")
        self.assertEqual(PINYIN_PREFIX_OVERRIDES["zhe"], "fe")

    def test_rime_ice_conversion_deduplicates_with_local_priority(self) -> None:
        sources = {
            "base": source_text(
                "本地词\tben di ci\t100",
                "新词\txin ci\t90",
                "重复词\tchong fu ci\t80",
                "傻逼\tsha bi\t70",
            ),
            "ext": source_text(
                "新词\txin ci\t999",
                "扩展词\tkuo zhan ci\t60",
            ),
            "others": source_text("扩展词\tkuo zhan ci"),
        }
        character_codes = {
            "新": ("xbv",),
            "词": ("cko",),
            "重": ("wyi",),
            "复": ("fju",),
            "扩": ("klv",),
            "展": ("qfv",),
        }
        prefixes = {
            "xin": "xb",
            "ci": "ck",
            "chong": "wy",
            "fu": "fj",
            "kuo": "kl",
            "zhan": "qf",
        }

        rows, stats = build_ice_rows(
            sources,
            character_codes,
            prefixes,
            {"本地词"},
            defaultdict(set),
        )

        self.assertEqual({row.word for row in rows}, {"新词", "重复词", "扩展词"})
        self.assertEqual(stats["deduplicated_local"], 1)
        self.assertEqual(stats["deduplicated_upstream"], 2)
        self.assertEqual(stats["skipped_rejected"], 1)

    def test_common_homophones_get_shorter_codes_first(self) -> None:
        sources = {
            "base": source_text(
                "新词\txin ci\t100",
                "心辞\txin ci\t10",
            ),
            "ext": source_text(),
            "others": source_text(),
        }
        character_codes = {
            "新": ("xbv",),
            "心": ("xbv",),
            "词": ("cko",),
            "辞": ("cko",),
        }
        rows, _ = build_ice_rows(
            sources,
            character_codes,
            {"xin": "xb", "ci": "ck"},
            set(),
            {"local": {"本地词"}},
        )

        codes = {row.word: row.code for row in rows}
        self.assertEqual(codes["新词"], "xbck")
        self.assertEqual(codes["心辞"], "xbckv")

    def test_collision_pruning_does_not_exceed_local_rate(self) -> None:
        local = {f"l{index}": {f"词{index}"} for index in range(98)}
        local["shared"] = {"甲", "乙"}
        rows = [
            GeneratedRow(f"唯一{index}", f"new{index}", 100, 0, index)
            for index in range(100)
        ]
        rows.extend(
            [
                GeneratedRow("高频", "new0", 90, 0, 100),
                GeneratedRow("低频", "new0", 10, 2, 101),
            ]
        )

        selected, stats = prune_ice_collisions(rows, local)

        self.assertIn("高频", {row.word for row in selected})
        self.assertNotIn("低频", {row.word for row in selected})
        self.assertLessEqual(
            stats["combined_collision_rows"] * stats["local_rows"],
            stats["local_collision_rows"] * stats["combined_rows"],
        )

    def test_danzi_uses_local_name_and_pinned_source(self) -> None:
        lock = load_lock()
        rendered = render_danzi("不\tb\n宾\tbb\n滨\tbbv\n", lock)

        self.assertIn("name: xmjd6.danzi", rendered)
        self.assertIn(lock["sources"]["rime_jiandao"]["commit"], rendered)
        self.assertTrue(rendered.endswith("不\tb\n宾\tbb\n滨\tbbv\n"))

    def test_english_sources_are_namespaced_normalized_and_deduplicated(self) -> None:
        rows, stats = build_english_rows(
            {
                "en": source_text("Hello\tHello", "C++\tC++", "README.md\tREADME.md"),
                "en_ext": source_text("Hello\tHello", "C#\tC#", "纯符号\t+++", "A4\tA4"),
            },
            {"ia"},
        )

        self.assertEqual(
            rows,
            [
                ("Hello", "ihello"),
                ("C++", "icpp"),
                ("README.md", "ireadmemd"),
                ("C#", "icsharp"),
            ],
        )
        self.assertEqual(stats["english_deduplicated_upstream"], 1)
        self.assertEqual(stats["english_skipped_unreachable"], 1)
        self.assertEqual(stats["english_skipped_local_code_collision"], 1)

    def test_generated_files_match_locked_checksums(self) -> None:
        self.assertEqual(verify_generated_hashes(ROOT), [])

    def test_ice_dictionary_is_imported_after_local_wordlists(self) -> None:
        text = (ROOT / "xmjd6.extended.dict.yaml").read_text(encoding="utf-8")
        self.assertIn("  - xmjd6.ice", text)
        self.assertLess(text.index("  - xmjd6.fjcy"), text.index("  - xmjd6.ice"))

    def test_english_dictionary_uses_main_schema_i_namespace(self) -> None:
        extended = (ROOT / "xmjd6.extended.dict.yaml").read_text(encoding="utf-8")
        schema = (ROOT / "xmjd6.schema.yaml").read_text(encoding="utf-8")
        self.assertIn("  - xmjd6.en", extended)
        self.assertIn("xform/^i(.+)$/$1/", schema)
        self.assertIn('prefix: "i"', schema)
        self.assertIn("max_code_length: 64", schema)
        self.assertNotIn("- xmjd6.en", schema)
        self.assertFalse((ROOT / "xmjd6.en.schema.yaml").exists())
        rows = list(iter_dictionary_rows(ROOT / "xmjd6.en.dict.yaml"))
        self.assertGreater(len(rows), 20_000)
        self.assertEqual(len(rows), len(set(rows)))
        self.assertTrue(all(re.fullmatch(r"i[a-z]+", code) for _, code in rows))
        english_codes = {code for _, code in rows}
        local_files = (
            "xmjd6.user.dict.yaml",
            "xmjd6.zzc.dict.yaml",
            "xmjd6.danzi.dict.yaml",
            "xmjd6.cizu.dict.yaml",
            "xmjd6.catholicism.dict.yaml",
            "xmjd6.core.dict.yaml",
            "xmjd6.fjcy.dict.yaml",
            "xmjd6.ice.dict.yaml",
        )
        local_codes = {
            code
            for filename in local_files
            if (ROOT / filename).is_file()
            for _, code in iter_dictionary_rows(ROOT / filename)
        }
        self.assertEqual(english_codes & local_codes, set())

    def test_release_conversion_includes_ice_dictionary(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "create-release.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("xmjd6.ice.dict.yaml", workflow)
        self.assertIn("Rime/xmjd6.ice.txt", workflow)
        self.assertIn("xmjd6.en.dict.yaml", workflow)
        self.assertIn("Rime/xmjd6.en.txt", workflow)

    def test_incremental_updater_compares_pinned_git_commits(self) -> None:
        script = (ROOT / "tools" / "update_upstream_dictionaries.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn('"diff", "--name-only"', script)
        self.assertIn('"--refresh-source"', script)
        self.assertIn("D:\\Dev\\pixi\\bin\\python.exe", script)

    def test_scheduled_sync_opens_a_validated_pull_request(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "sync-upstream-dictionaries.yml"
        ).read_text(encoding="utf-8")
        self.assertIn('cron: "17 4 * * 1"', workflow)
        self.assertIn("update_upstream_dictionaries.ps1", workflow)
        self.assertIn("python tools/validate_repo.py", workflow)
        self.assertIn("gh pr create", workflow)


if __name__ == "__main__":
    unittest.main()
