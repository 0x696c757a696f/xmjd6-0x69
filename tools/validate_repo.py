#!/usr/bin/env python3
"""Validate the repository before packaging or deploying the Rime schema."""

from __future__ import annotations

import json
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by dependency setup
    raise SystemExit("PyYAML is required: python -m pip install PyYAML") from exc


ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^\s*(?:config_)?version:\s*[\"']?(\d{4}-\d{2}-\d{2})", re.MULTILINE)
REQUIRE_RE = re.compile(r"\brequire\s*\(\s*[\"']([^\"']+)[\"']\s*\)")
COMPONENT_RE = re.compile(r"lua_(?:processor|translator|filter)@\*([^\s#]+)")


def add_error(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT).as_posix()}: {message}")


def validate_layout(errors: list[str]) -> None:
    for path in (ROOT / "lua").rglob("*.lua"):
        if path.relative_to(ROOT / "lua").parts[0] != "xmjd6":
            add_error(errors, path, "Lua source must live below lua/xmjd6/")
    for path in (ROOT / "opencc").rglob("*"):
        if path.is_file() and path.relative_to(ROOT / "opencc").parts[0] != "xmjd6":
            add_error(errors, path, "OpenCC data must live below opencc/xmjd6/")


def validate_versions(errors: list[str]) -> None:
    expected = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", expected):
        errors.append("VERSION: expected YYYY-MM-DD")
        return
    for path in sorted(ROOT.glob("*.yaml")):
        for found in VERSION_RE.findall(path.read_text(encoding="utf-8-sig")):
            if found != expected:
                add_error(errors, path, f"version {found!r} does not match VERSION {expected!r}")


def validate_yaml_and_json(errors: list[str]) -> None:
    config_paths = list(ROOT.glob("*.yaml")) + list((ROOT / ".github" / "workflows").glob("*.yml"))
    for path in sorted(config_paths):
        if path.name.endswith(".dict.yaml"):
            continue
        try:
            yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        except yaml.YAMLError as exc:
            add_error(errors, path, f"invalid YAML: {exc}")
    for path in sorted((ROOT / "opencc").rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            add_error(errors, path, f"invalid JSON: {exc}")


def dict_header(path: Path, errors: list[str]) -> tuple[dict, int | None]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    marker = next((index for index, line in enumerate(lines) if line.strip() == "..."), None)
    header_lines = lines if marker is None else lines[:marker]
    try:
        header = yaml.safe_load("\n".join(header_lines)) or {}
    except yaml.YAMLError as exc:
        add_error(errors, path, f"invalid dictionary header: {exc}")
        return {}, marker
    if not isinstance(header, dict):
        add_error(errors, path, "dictionary header must be a mapping")
        return {}, marker
    return header, marker


def validate_dictionaries(errors: list[str]) -> None:
    for path in sorted(ROOT.glob("*.dict.yaml")):
        header, marker = dict_header(path, errors)
        imports = header.get("import_tables", [])
        if isinstance(imports, list):
            for table in imports:
                imported = ROOT / f"{table}.dict.yaml"
                if not imported.is_file():
                    add_error(errors, path, f"missing imported dictionary {imported.name}")
        if marker is None:
            continue
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        seen_rows: dict[str, int] = {}
        duplicate_rows: list[tuple[int, int]] = []
        for line_number, line in enumerate(lines[marker + 1 :], marker + 2):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if "\t" not in line:
                add_error(errors, path, f"line {line_number} is not tab-separated dictionary data")
                continue
            if line in seen_rows:
                duplicate_rows.append((line_number, seen_rows[line]))
            else:
                seen_rows[line] = line_number
        if duplicate_rows:
            duplicate_line, original_line = duplicate_rows[0]
            add_error(
                errors,
                path,
                f"{len(duplicate_rows)} exact duplicate row(s); line {duplicate_line} repeats line {original_line}",
            )


def validate_module_references(errors: list[str]) -> None:
    for path in sorted((ROOT / "lua").rglob("*.lua")):
        text = path.read_text(encoding="utf-8-sig")
        for module in REQUIRE_RE.findall(text):
            if not module.startswith("xmjd6"):
                continue
            target = ROOT / "lua" / Path(*module.split("."))
            target = target.with_suffix(".lua")
            if not target.is_file():
                add_error(errors, path, f"require({module!r}) does not resolve to {target.relative_to(ROOT)}")
    for path in sorted(ROOT.glob("*.yaml")):
        text = path.read_text(encoding="utf-8-sig")
        for module in COMPONENT_RE.findall(text):
            target = ROOT / "lua" / (module.replace(".", "/") + ".lua")
            if not target.is_file():
                add_error(errors, path, f"Lua component {module!r} does not resolve to {target.relative_to(ROOT)}")


def validate_lua_with_lupa(errors: list[str]) -> str:
    files = sorted((ROOT / "lua").rglob("*.lua")) + sorted((ROOT / "opencc").rglob("*.lua"))
    try:
        from lupa import LuaRuntime
    except ImportError:
        errors.append("Lua compiler not found; install Lua 5.4 (or Lupa for local validation)")
        return "unavailable"

    runtime = LuaRuntime(unpack_returned_tuples=True)
    loader = runtime.eval("function(path) local f, err = loadfile(path); return f ~= nil, err end")
    for path in files:
        ok, message = loader(str(path))
        if not ok:
            add_error(errors, path, str(message))
    return "Lupa/Lua " + str(runtime.eval("_VERSION"))


def validate_lua_syntax(errors: list[str]) -> str:
    files = sorted((ROOT / "lua").rglob("*.lua")) + sorted((ROOT / "opencc").rglob("*.lua"))
    compiler = shutil.which("luac5.4") or shutil.which("luac")
    if compiler:
        try:
            for path in files:
                result = subprocess.run(
                    [compiler, "-p", str(path)], capture_output=True, text=True
                )
                if result.returncode:
                    add_error(errors, path, (result.stderr or result.stdout).strip())
        except OSError:
            pass
        else:
            return Path(compiler).name

    return validate_lua_with_lupa(errors)


def validate_python_syntax(errors: list[str]) -> None:
    for directory in (ROOT / "tools", ROOT / "tests"):
        for path in sorted(directory.rglob("*.py")):
            try:
                compile(path.read_text(encoding="utf-8-sig"), str(path), "exec")
            except (SyntaxError, UnicodeDecodeError) as exc:
                add_error(errors, path, f"invalid Python: {exc}")


def validate_generated_dictionaries(errors: list[str]) -> None:
    lock_path = ROOT / "tools" / "upstream_dictionaries.lock.json"
    if not lock_path.is_file():
        return
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    for filename, metadata in lock.get("generated", {}).items():
        path = ROOT / filename
        if not path.is_file():
            add_error(errors, lock_path, f"missing generated dictionary {filename}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != metadata.get("sha256"):
            add_error(errors, path, "content differs from upstream dictionary lock")


def main() -> int:
    errors: list[str] = []
    validate_layout(errors)
    validate_versions(errors)
    validate_yaml_and_json(errors)
    validate_dictionaries(errors)
    validate_module_references(errors)
    validate_python_syntax(errors)
    validate_generated_dictionaries(errors)
    lua_runtime = validate_lua_syntax(errors)

    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validation passed (Lua: {lua_runtime}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
