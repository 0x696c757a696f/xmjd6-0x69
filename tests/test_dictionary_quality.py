from __future__ import annotations

import unittest
from pathlib import Path

from tools import clean_dictionary_quality as quality


ROOT = Path(__file__).resolve().parents[1]


class DictionaryQualityTests(unittest.TestCase):
    def test_declared_replacements_follow_dictionary_rules(self) -> None:
        quality.validate_replacements(ROOT)

    def test_repairs_corruption_and_removes_abusive_rows(self) -> None:
        source = (
            "---\n...\n"
            "淡啦\ttflsa.碳蜡\ttflsv\n"
            "不成其为\tbjqwvvv\n"
            "傻逼\tesbk\n"
            "阴道炎\tydy\n"
        )

        cleaned, replacements, removals = quality.clean_text(
            Path("xmjd6.cizu.dict.yaml"), source
        )

        self.assertIn("淡啦\tdflsa\n碳蜡\ttflsv", cleaned)
        self.assertIn("不成其为\tbjqwvv", cleaned)
        self.assertNotIn("傻逼", cleaned)
        self.assertIn("阴道炎\tydy", cleaned)
        self.assertEqual(replacements, 2)
        self.assertEqual(removals, 1)

    def test_preserves_valid_place_and_sensitive_technical_terms(self) -> None:
        self.assertFalse(quality.is_rejected("密支那", "mfns"))
        self.assertFalse(quality.is_rejected("强奸罪", "qjz"))
        self.assertFalse(quality.is_rejected("阴道炎", "ydy"))
        self.assertTrue(quality.is_rejected("支那人", "fnr"))
        self.assertTrue(quality.is_rejected("肏鬼", "czg"))

    def test_danzi_is_outside_cleanup_scope(self) -> None:
        self.assertNotIn("xmjd6.danzi.dict.yaml", quality.TARGET_NAMES)
        self.assertNotIn("xmjd6.danzi.dict.yaml", quality.ROW_REPLACEMENTS)
        self.assertNotIn("xmjd6.danzi.dict.yaml", quality.ROW_REMOVALS)

    def test_repository_is_already_clean(self) -> None:
        remaining = [result.path.name for result in quality.process(ROOT) if result.changed]
        self.assertEqual(remaining, [])


if __name__ == "__main__":
    unittest.main()
