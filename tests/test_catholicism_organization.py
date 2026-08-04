from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "xmjd6.catholicism.dict.yaml"


class CatholicismOrganizationTests(unittest.TestCase):
    def test_organization_preserves_every_dictionary_row(self) -> None:
        from tools.build_catholicism_expansion import iter_rows_from_text
        from tools.organize_catholicism_legacy import organize_dictionary_text

        original = TARGET.read_text(encoding="utf-8-sig")
        organized = organize_dictionary_text(original)

        self.assertEqual(
            list(iter_rows_from_text(organized)),
            list(iter_rows_from_text(original)),
        )

    def test_committed_dictionary_has_all_legacy_section_dividers(self) -> None:
        from tools.organize_catholicism_legacy import expected_dictionary_text

        actual = TARGET.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        self.assertEqual(actual, expected_dictionary_text(ROOT))
        for heading in (
            "圣经辞汇、人物、地名、制度与名物",
            "教理、神学、哲学、教会史与宗教研究",
            "圣事、礼仪、祷文与敬礼",
        ):
            self.assertIn(f"# -------------------- {heading} --------------------", actual)


if __name__ == "__main__":
    unittest.main()
