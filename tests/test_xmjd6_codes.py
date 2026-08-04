from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Xmjd6CodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from tools.xmjd6_codes import load_character_codes

        cls.character_codes = load_character_codes(
            ROOT / "xmjd6.danzi.dict.yaml", {"召": "fz"}
        )

    def test_generates_standard_two_three_and_multi_character_codes(self) -> None:
        from tools.xmjd6_codes import code_candidates

        self.assertEqual(code_candidates("爱德", self.character_codes)[0], "xhde")
        self.assertEqual(code_candidates("慕道班", self.character_codes)[:2], ["mdb", "mdbi"])
        self.assertEqual(code_candidates("大公教会", self.character_codes)[0], "dgjh")

    def test_uses_each_character_first_stroke_for_extended_codes(self) -> None:
        from tools.xmjd6_codes import code_candidates

        self.assertEqual(
            code_candidates("赞主曲", self.character_codes),
            ["zqq", "zqqu", "zqquo", "zqquoi"],
        )
        self.assertEqual(
            code_candidates("婚姻圣召", self.character_codes),
            ["hyef", "hyefa", "hyefaa"],
        )

    def test_uses_first_character_auxiliary_codes_to_avoid_collision(self) -> None:
        from tools.xmjd6_codes import choose_code

        occupied = {"mdb": {"别的词"}}
        self.assertEqual(choose_code("慕道班", self.character_codes, occupied), "mdbi")


if __name__ == "__main__":
    unittest.main()
