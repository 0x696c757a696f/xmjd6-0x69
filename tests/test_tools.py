from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
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
    def test_explicit_lua_component_namespace_resolves_module_path(self) -> None:
        from tools import validate_repo

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "lua" / "xmjd6").mkdir(parents=True)
            (root / "lua" / "xmjd6" / "filter.lua").write_text(
                "return {}\n", encoding="utf-8"
            )
            (root / "xmjd6.schema.yaml").write_text(
                "filters:\n  - lua_filter@*xmjd6/filter@filter_namespace\n",
                encoding="utf-8",
            )
            errors: list[str] = []

            with patch.object(validate_repo, "ROOT", root):
                validate_repo.validate_module_references(errors)

        self.assertEqual(errors, [])

    def test_main_schema_gives_opencc_filter_a_stable_namespace(self) -> None:
        root = Path(__file__).resolve().parents[1]
        schema = (root / "xmjd6.schema.yaml").read_text(encoding="utf-8")

        self.assertIn(
            "lua_filter@*xmjd6/xmjd6_opencc_filter@xmjd6_opencc_filter",
            schema,
        )

    def test_modular_ascii_handler_owns_uppercase_and_shift_behavior(self) -> None:
        root = Path(__file__).resolve().parents[1]
        schema = (root / "xmjd6.schema.yaml").read_text(encoding="utf-8")
        custom = (root / "xmjd6.custom.yaml").read_text(encoding="utf-8")

        self.assertNotIn("uppercase:", schema)
        self.assertIn("Shift_L: commit_code", schema)
        self.assertIn("Shift_R: commit_code", schema)
        self.assertIn("Shift_L: commit_code", custom)
        self.assertIn("Shift_R: commit_code", custom)

    def test_zzc_merge_targets_the_xmjd6_cizu_dictionary(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "zzc" / "Linux_词库合并.py"
        spec = importlib.util.spec_from_file_location("xmjd6_zzc_merge_test", script)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader if spec else None)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)

        self.assertEqual(
            module.target_dict_name_options("xmjd6"),
            [["xmjd6.cizu.dict.yaml"], ["xmjd6.fjcy.dict.yaml"]],
        )
        with self.assertRaisesRegex(ValueError, "expected xmjd6"):
            module.target_dict_name_options("other")
        with self.assertRaisesRegex(ValueError, "expected xmjd6"):
            module.target_dict_name_options("xmjd7")

    def test_zzc_merge_integrates_numbered_xmjd6_operation_files(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        dictionary_header = """# Rime dictionary
---
name: {name}
version: "2026-08-04"
sort: by_weight
...
"""
        operation_header = """# Rime dictionary
# encoding: utf-8
---
name: xmjd6.zzc
version: "2026-08-04"
sort: by_weight
use_preset_vocabulary: false
columns:
  - text
  - code
...
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            zzc_dir = root / "zzc"
            zzc_dir.mkdir()
            shutil.copy2(repository / "zzc" / "Linux_词库合并.py", zzc_dir)
            (root / "xmjd6.cizu.dict.yaml").write_text(
                dictionary_header.format(name="xmjd6.cizu"), encoding="utf-8"
            )
            (root / "xmjd6.fjcy.dict.yaml").write_text(
                dictionary_header.format(name="xmjd6.fjcy"), encoding="utf-8"
            )
            (root / "xmjd6.zzc.dict(1).yaml").write_text(
                operation_header + "100\tadd\t测试自造词\tcszc\t+\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(zzc_dir / "Linux_词库合并.py")],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            self.assertEqual(
                result.returncode,
                0,
                (result.stdout or "") + (result.stderr or ""),
            )
            merged = (root / "xmjd6.cizu.dict.yaml").read_text(encoding="utf-8")
            self.assertIn("测试自造词\tcszc", merged)
            self.assertFalse((root / "xmjd6.zzc.dict(1).yaml").exists())
            self.assertEqual(
                (root / "xmjd6.zzc.dict.yaml").read_text(encoding="utf-8"),
                operation_header,
            )

    def test_detects_generated_dictionary_drift(self) -> None:
        from tools import validate_repo

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            tools_dir = root / "tools"
            tools_dir.mkdir()
            (root / "generated.dict.yaml").write_text("changed\n", encoding="utf-8")
            (tools_dir / "upstream_dictionaries.lock.json").write_text(
                '{"generated":{"generated.dict.yaml":{"sha256":"expected"}}}\n',
                encoding="utf-8",
            )
            errors: list[str] = []

            with patch.object(validate_repo, "ROOT", root):
                validate_repo.validate_generated_dictionaries(errors)

        self.assertEqual(
            errors,
            ["generated.dict.yaml: content differs from upstream dictionary lock"],
        )

    def test_scheduled_code_check_has_no_local_absolute_path(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github" / "workflows" / "check-txjx-upstream.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("tools/check_txjx_upstream.py", workflow)
        self.assertNotIn("D:\\", workflow)
        self.assertNotIn("D:/", workflow)

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
