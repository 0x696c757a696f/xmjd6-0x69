from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path


class FetchOpenCCTests(unittest.TestCase):
    def test_extracts_only_opencc_data_into_namespaced_directory(self) -> None:
        from tools.fetch_opencc import extract_opencc_archive

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive = root / "opencc.zip"
            destination = root / "opencc" / "xmjd6"
            destination.mkdir(parents=True)
            (destination / "local.lua").write_text("return {}\n", encoding="utf-8")
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("opencc/s2tg.json", "{}")
                bundle.writestr("opencc/STGCharacters.ocd2", b"ocd2")
                bundle.writestr("README.md", "ignored")

            extracted = extract_opencc_archive(archive, destination)

            self.assertEqual(extracted, 2)
            self.assertEqual((destination / "s2tg.json").read_text(encoding="utf-8"), "{}")
            self.assertEqual((destination / "STGCharacters.ocd2").read_bytes(), b"ocd2")
            self.assertTrue((destination / "local.lua").is_file())
            self.assertFalse((destination / "opencc").exists())

    def test_rejects_archive_path_traversal(self) -> None:
        from tools.fetch_opencc import extract_opencc_archive

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive = root / "opencc.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("opencc/../../escaped.json", "{}")

            with self.assertRaises(ValueError):
                extract_opencc_archive(archive, root / "opencc" / "xmjd6")


if __name__ == "__main__":
    unittest.main()
