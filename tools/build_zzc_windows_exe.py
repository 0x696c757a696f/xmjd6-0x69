#!/usr/bin/env python3
"""Build and verify the committed Windows ZZZC executables."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import shutil
import struct
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = ROOT / "build" / "zzc-windows-exe"
LOCK_PATH = ROOT / "tools" / "zzc_windows_executables.lock.json"
BUILD_DATE = "2026-08-04"
PYTHON_SERIES = (3, 14)
PYINSTALLER_VERSION = "6.21.0"
PE_AMD64 = 0x8664


@dataclass(frozen=True)
class ExecutableTarget:
    source: Path
    output: Path
    description: str


TARGETS = (
    ExecutableTarget(
        ROOT / "zzc" / "Linux_词库合并.py",
        ROOT / "zzc" / "Win_词库合并.exe",
        "xmjd6 ZZZC dictionary merge",
    ),
    ExecutableTarget(
        ROOT / "zzc" / "Linux_撤回合并.py",
        ROOT / "zzc" / "Win_撤回合并.exe",
        "xmjd6 ZZZC merge rollback",
    ),
)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_pe(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise ValueError("missing DOS MZ header")
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if pe_offset + 6 > len(data) or data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise ValueError("missing PE signature")
    machine = struct.unpack_from("<H", data, pe_offset + 4)[0]
    return machine, f"0x{machine:04X}"


def version_resource(target: ExecutableTarget) -> str:
    original_name = target.output.name
    return f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2026, 8, 4, 0),
    prodvers=(2026, 8, 4, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'xmjd6'),
         StringStruct('FileDescription', '{target.description}'),
         StringStruct('FileVersion', '2026.08.04'),
         StringStruct('InternalName', '{target.output.stem}'),
         StringStruct('OriginalFilename', '{original_name}'),
         StringStruct('ProductName', 'xmjd6 ZZZC tools'),
         StringStruct('ProductVersion', '2026.08.04')])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""


def build_executables() -> None:
    if sys.platform != "win32":
        raise RuntimeError("Windows executables must be built on Windows")
    if sys.version_info[:2] != PYTHON_SERIES:
        raise RuntimeError(
            f"expected Python {PYTHON_SERIES[0]}.{PYTHON_SERIES[1]}, "
            f"got {sys.version_info.major}.{sys.version_info.minor}"
        )
    try:
        pyinstaller_version = importlib.metadata.version("pyinstaller")
    except importlib.metadata.PackageNotFoundError as exc:
        raise RuntimeError("PyInstaller is not installed") from exc
    if pyinstaller_version != PYINSTALLER_VERSION:
        raise RuntimeError(
            f"expected PyInstaller {PYINSTALLER_VERSION}, got {pyinstaller_version}"
        )

    expected_parent = (ROOT / "build").resolve()
    if BUILD_ROOT.resolve().parent != expected_parent:
        raise RuntimeError(f"unsafe build directory: {BUILD_ROOT}")
    if BUILD_ROOT.exists():
        shutil.rmtree(BUILD_ROOT)
    dist_dir = BUILD_ROOT / "dist"
    spec_dir = BUILD_ROOT / "spec"
    version_dir = BUILD_ROOT / "version"
    version_dir.mkdir(parents=True)

    for index, target in enumerate(TARGETS):
        version_file = version_dir / f"target-{index}.txt"
        version_file.write_text(version_resource(target), encoding="utf-8", newline="\n")
        command = [
            sys.executable,
            "-I",
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--onefile",
            "--console",
            "--noupx",
            "--name",
            target.output.stem,
            "--version-file",
            str(version_file),
            "--distpath",
            str(dist_dir),
            "--workpath",
            str(BUILD_ROOT / "work" / str(index)),
            "--specpath",
            str(spec_dir),
            relative(target.source),
        ]
        subprocess.run(command, cwd=ROOT, check=True)
        built = dist_dir / target.output.name
        machine, _ = inspect_pe(built)
        if machine != PE_AMD64:
            raise RuntimeError(f"unexpected PE machine for {built}: 0x{machine:04X}")
        shutil.copy2(built, target.output)

    lock = {
        "schema": 1,
        "build": {
            "date": BUILD_DATE,
            "python": ".".join(str(part) for part in sys.version_info[:3]),
            "python_series": f"{PYTHON_SERIES[0]}.{PYTHON_SERIES[1]}",
            "pyinstaller": pyinstaller_version,
            "platform": "Windows-64bit-intel",
        },
        "builder": {
            "path": relative(Path(__file__).resolve()),
            "sha256": sha256(Path(__file__).resolve()),
        },
        "executables": {},
    }
    executable_rows = lock["executables"]
    assert isinstance(executable_rows, dict)
    for target in TARGETS:
        _, machine = inspect_pe(target.output)
        executable_rows[relative(target.output)] = {
            "source": relative(target.source),
            "source_sha256": sha256(target.source),
            "sha256": sha256(target.output),
            "size": target.output.stat().st_size,
            "machine": machine,
        }
    LOCK_PATH.write_text(
        json.dumps(lock, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def validate_committed_outputs() -> list[str]:
    errors: list[str] = []
    if not LOCK_PATH.exists():
        return [f"missing lock file: {relative(LOCK_PATH)}"]
    try:
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid lock file: {exc}"]

    if lock.get("schema") != 1:
        errors.append("unsupported executable lock schema")
    if lock.get("build", {}).get("date") != BUILD_DATE:
        errors.append("executable build date is stale")
    builder = lock.get("builder", {})
    if builder.get("path") != relative(Path(__file__).resolve()):
        errors.append("builder path differs from executable lock")
    elif builder.get("sha256") != sha256(Path(__file__).resolve()):
        errors.append("builder changed; rebuild Windows executables")

    rows = lock.get("executables", {})
    expected_outputs = {relative(target.output) for target in TARGETS}
    if set(rows) != expected_outputs:
        errors.append("executable set differs from lock")
    for target in TARGETS:
        output_name = relative(target.output)
        row = rows.get(output_name)
        if not isinstance(row, dict):
            errors.append(f"missing executable lock row: {output_name}")
            continue
        if row.get("source") != relative(target.source):
            errors.append(f"source path differs for {output_name}")
        elif not target.source.exists() or row.get("source_sha256") != sha256(target.source):
            errors.append(f"source changed; rebuild {output_name}")
        if not target.output.exists():
            errors.append(f"missing executable: {output_name}")
            continue
        if row.get("sha256") != sha256(target.output):
            errors.append(f"executable checksum differs: {output_name}")
        if row.get("size") != target.output.stat().st_size:
            errors.append(f"executable size differs: {output_name}")
        try:
            machine, machine_text = inspect_pe(target.output)
        except ValueError as exc:
            errors.append(f"invalid executable {output_name}: {exc}")
            continue
        if machine != PE_AMD64 or row.get("machine") != machine_text:
            errors.append(f"unexpected executable architecture: {output_name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that committed EXEs match their current Python sources",
    )
    args = parser.parse_args()
    if args.check:
        errors = validate_committed_outputs()
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print("Windows ZZZC executables match their sources and lock")
        return 0

    build_executables()
    errors = validate_committed_outputs()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    for target in TARGETS:
        print(f"built {relative(target.output)}: sha256={sha256(target.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
