from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


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


class RepositoryValidationTests(unittest.TestCase):
    def test_falls_back_to_lupa_when_luac_cannot_execute(self) -> None:
        from tools import validate_repo

        errors: list[str] = []
        with (
            patch.object(validate_repo.shutil, "which", return_value="luac.EXE"),
            patch.object(validate_repo.subprocess, "run", side_effect=PermissionError(5)),
            patch.object(
                validate_repo,
                "validate_lua_with_lupa",
                return_value="Lupa/Lua 5.5",
                create=True,
            ) as fallback,
        ):
            runtime = validate_repo.validate_lua_syntax(errors)

        self.assertEqual(runtime, "Lupa/Lua 5.5")
        self.assertEqual(errors, [])
        fallback.assert_called_once_with(errors)


if __name__ == "__main__":
    unittest.main()
