from __future__ import annotations

import fnmatch
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
    def test_generated_xmjd6_user_text_database_is_not_distributed(self) -> None:
        root = Path(__file__).resolve().parents[1]

        self.assertFalse((root / "xmjd6_user.txt").exists())
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", "--no-index", "xmjd6_user.txt"],
            cwd=root,
            check=False,
        )
        self.assertEqual(ignored.returncode, 0)

    def test_plum_recipe_installs_every_rime_runtime_file(self) -> None:
        root = Path(__file__).resolve().parents[1]
        recipe = (root / "recipe.yaml").read_text(encoding="utf-8")
        install_block = recipe.split("install_files: >-", 1)[1].split(
            "patch_files:", 1
        )[0]
        patterns = install_block.split()

        runtime_files = [
            *root.glob("*.yaml"),
            *(root / "lua" / "xmjd6").rglob("*.lua"),
            *(root / "opencc" / "xmjd6").rglob("*.lua"),
        ]
        runtime_names = {
            path.relative_to(root).as_posix()
            for path in runtime_files
            if path.name != "recipe.yaml" and not path.name.endswith(".custom.yaml")
        }
        installed_names = {
            name
            for name in runtime_names
            if any(fnmatch.fnmatchcase(name, pattern) for pattern in patterns)
        }

        self.assertEqual(installed_names, runtime_names)
        self.assertFalse(
            any(fnmatch.fnmatchcase("recipe.yaml", pattern) for pattern in patterns)
        )
        for custom_name in (
            "default.custom.yaml",
            "squirrel.custom.yaml",
            "weasel.custom.yaml",
            "xmjd6.custom.yaml",
        ):
            self.assertFalse(
                any(fnmatch.fnmatchcase(custom_name, pattern) for pattern in patterns),
                custom_name,
            )
        self.assertIn("patch_files:", recipe)
        self.assertIn("default.custom.yaml:", recipe)
        self.assertIn("- schema: xmjd6", recipe)

    def test_main_schema_exposes_explicit_switch_defaults_for_rimetool(self) -> None:
        root = Path(__file__).resolve().parents[1]
        schema = (root / "xmjd6.schema.yaml").read_text(encoding="utf-8")
        expected_defaults = {
            "ascii_mode": 0,
            "jffh": 0,
            "completion": 1,
            "emoji_cn": 1,
            "direct_symbols": 1,
            "smarttwo": 0,
            "jisuanqi": 1,
            "auto_fallback": 0,
            "sbb_hint": 1,
            "mars": 0,
            "full_shape": 0,
        }

        for name, reset in expected_defaults.items():
            self.assertIn(
                f"- name: {name}",
                schema,
            )
            switch_block = schema.split(f"- name: {name}", 1)[1].split("- name:", 1)[0]
            self.assertIn(f"reset: {reset}", switch_block, name)

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

    @unittest.skipUnless(sys.platform == "win32", "committed EXE is Windows-only")
    def test_windows_merge_executable_runs_current_xmjd6_behavior(self) -> None:
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
            shutil.copy2(repository / "zzc" / "Win_词库合并.exe", zzc_dir)
            (root / "xmjd6.cizu.dict.yaml").write_text(
                dictionary_header.format(name="xmjd6.cizu"), encoding="utf-8"
            )
            (root / "xmjd6.fjcy.dict.yaml").write_text(
                dictionary_header.format(name="xmjd6.fjcy"), encoding="utf-8"
            )
            (root / "xmjd6.zzc.dict(1).yaml").write_text(
                operation_header + "100\tadd\tEXE当前逻辑\texedq\t+\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [str(zzc_dir / "Win_词库合并.exe")],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
                check=False,
            )

            self.assertEqual(
                result.returncode,
                0,
                (result.stdout or "") + (result.stderr or ""),
            )
            merged = (root / "xmjd6.cizu.dict.yaml").read_text(encoding="utf-8")
            self.assertIn("EXE当前逻辑\texedq", merged)
            self.assertFalse((root / "xmjd6.zzc.dict(1).yaml").exists())
            self.assertTrue((root / "xmjd6.zzc.dict.yaml").is_file())

    @unittest.skipUnless(sys.platform == "win32", "committed EXE is Windows-only")
    def test_windows_rollback_executable_restores_latest_merge(self) -> None:
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
            for executable in ("Win_词库合并.exe", "Win_撤回合并.exe"):
                shutil.copy2(repository / "zzc" / executable, zzc_dir)
            original_cizu = dictionary_header.format(name="xmjd6.cizu") + "原词\tycw\n"
            (root / "xmjd6.cizu.dict.yaml").write_text(original_cizu, encoding="utf-8")
            (root / "xmjd6.fjcy.dict.yaml").write_text(
                dictionary_header.format(name="xmjd6.fjcy"), encoding="utf-8"
            )
            original_ops = operation_header + "100\tadd\t待撤回词\tdcht\t+\n"
            (root / "xmjd6.zzc.dict.yaml").write_text(original_ops, encoding="utf-8")

            merge = subprocess.run(
                [str(zzc_dir / "Win_词库合并.exe")],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
                check=False,
            )
            self.assertEqual(merge.returncode, 0, (merge.stdout or "") + (merge.stderr or ""))
            self.assertIn(
                "待撤回词\tdcht",
                (root / "xmjd6.cizu.dict.yaml").read_text(encoding="utf-8"),
            )

            rollback = subprocess.run(
                [str(zzc_dir / "Win_撤回合并.exe")],
                cwd=root,
                input="1\nYES\n",
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
                check=False,
            )

            self.assertEqual(
                rollback.returncode,
                0,
                (rollback.stdout or "") + (rollback.stderr or ""),
            )
            self.assertEqual(
                (root / "xmjd6.cizu.dict.yaml").read_text(encoding="utf-8"),
                original_cizu,
            )
            self.assertEqual(
                (root / "xmjd6.zzc.dict.yaml").read_text(encoding="utf-8"),
                original_ops,
            )

    def test_committed_windows_executables_match_sources_and_lock(self) -> None:
        from tools.build_zzc_windows_exe import validate_committed_outputs

        self.assertEqual(validate_committed_outputs(), [])

    def test_windows_executables_are_binary_git_assets(self) -> None:
        root = Path(__file__).resolve().parents[1]
        attributes = (root / ".gitattributes").read_text(encoding="utf-8")

        self.assertRegex(attributes, r"(?m)^\*\.exe\s+binary\s*$")

    def test_package_and_release_run_windows_executable_checks(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflows = root / ".github" / "workflows"
        for name in ("package-main.yml", "create-release.yml"):
            workflow = (workflows / name).read_text(encoding="utf-8")
            self.assertIn("windows-latest", workflow, name)
            self.assertIn("test_windows_merge_executable_runs_current_xmjd6_behavior", workflow, name)
            self.assertIn("test_windows_rollback_executable_restores_latest_merge", workflow, name)
            self.assertIn("test_committed_windows_executables_match_sources_and_lock", workflow, name)
            self.assertIn("python-version: '3.14.6'", workflow, name)
            self.assertIn("pyinstaller==6.21.0", workflow, name)
            self.assertIn("python tools/build_zzc_windows_exe.py", workflow, name)
            self.assertIn("actions/upload-artifact@v7", workflow, name)
            self.assertIn("actions/download-artifact@v7", workflow, name)
            self.assertIn("name: zzc-windows-executables", workflow, name)

    def test_every_python_workflow_forces_utf8_io(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflows = root / ".github" / "workflows"

        for path in workflows.glob("*.yml"):
            workflow = path.read_text(encoding="utf-8")
            if "actions/setup-python@" not in workflow:
                continue
            self.assertIn('PYTHONUTF8: "1"', workflow, path.name)
            self.assertIn('PYTHONIOENCODING: "utf-8"', workflow, path.name)

    def test_windows_executable_builder_reconfigures_stdio_to_utf8(self) -> None:
        root = Path(__file__).resolve().parents[1]
        code = """
import sys
sys.stdout.reconfigure(encoding="cp1252", errors="strict")
sys.stderr.reconfigure(encoding="cp1252", errors="strict")
from tools.build_zzc_windows_exe import configure_utf8_stdio
configure_utf8_stdio()
print("Win_词库合并.exe")
print("Win_撤回合并.exe", file=sys.stderr)
"""

        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=root,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertEqual(result.stdout.decode("utf-8").strip(), "Win_词库合并.exe")
        self.assertEqual(result.stderr.decode("utf-8").strip(), "Win_撤回合并.exe")

    def test_bundled_zzc_sources_reconfigure_stdio_to_utf8(self) -> None:
        root = Path(__file__).resolve().parents[1]
        scripts = (
            root / "zzc" / "Linux_词库合并.py",
            root / "zzc" / "Linux_撤回合并.py",
        )
        code = """
import importlib.util
import sys
sys.stdout.reconfigure(encoding="cp1252", errors="strict")
sys.stderr.reconfigure(encoding="cp1252", errors="strict")
for index, path in enumerate(sys.argv[1:]):
    spec = importlib.util.spec_from_file_location(f"zzc_utf8_{index}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.configure_utf8_stdio()
print("合并完成")
print("撤回完成", file=sys.stderr)
"""

        result = subprocess.run(
            [sys.executable, "-c", code, *(str(path) for path in scripts)],
            cwd=root,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertEqual(result.stdout.decode("utf-8").strip(), "合并完成")
        self.assertEqual(result.stderr.decode("utf-8").strip(), "撤回完成")

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

    def test_workflows_use_native_node24_actions(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflows = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((root / ".github" / "workflows").glob("*.yml"))
        )

        self.assertNotIn("FORCE_JAVASCRIPT_ACTIONS_TO_NODE24", workflows)
        for deprecated in (
            "actions/checkout@v4",
            "actions/setup-python@v5",
            "actions/upload-artifact@v4",
            "actions/github-script@v8",
        ):
            self.assertNotIn(deprecated, workflows)
        for native_node24 in (
            "actions/checkout@v6",
            "actions/setup-python@v6",
            "actions/upload-artifact@v7",
            "actions/github-script@v9",
        ):
            self.assertIn(native_node24, workflows)

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
