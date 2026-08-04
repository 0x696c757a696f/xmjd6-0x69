#!/usr/bin/env python3
"""Download a pinned OpenCC bundle and merge its data into opencc/xmjd6."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import stat
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_SUFFIXES = {".json", ".ocd2"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_opencc_archive(archive: Path, destination: Path) -> int:
    destination = destination.resolve()
    pending: list[tuple[zipfile.ZipInfo, Path]] = []
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            if member.is_dir():
                continue
            parts = PurePosixPath(member.filename).parts
            if not parts or any(part in {"", ".", ".."} for part in parts):
                raise ValueError(f"unsafe archive path: {member.filename}")
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(f"archive symlink is not allowed: {member.filename}")
            if parts[0] != "opencc" or len(parts) < 2:
                continue
            relative = Path(*parts[1:])
            if relative.suffix.lower() not in ALLOWED_SUFFIXES:
                continue
            target = (destination / relative).resolve()
            if destination not in target.parents:
                raise ValueError(f"archive path escapes destination: {member.filename}")
            pending.append((member, target))

        if not pending:
            raise ValueError("archive contains no .json or .ocd2 files below opencc/")

        for member, target in pending:
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + ".tmp")
            try:
                with bundle.open(member) as source, temporary.open("wb") as output:
                    shutil.copyfileobj(source, output)
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
    return len(pending)


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "xmjd6-release-builder"})
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--destination", type=Path, default=ROOT / "opencc" / "xmjd6")
    args = parser.parse_args()

    expected = args.sha256.lower().removeprefix("sha256:")
    if len(expected) != 64 or any(char not in "0123456789abcdef" for char in expected):
        parser.error("--sha256 must be a 64-character SHA-256 digest")

    with tempfile.TemporaryDirectory(prefix="xmjd6-opencc-") as temp_dir:
        archive = Path(temp_dir) / "opencc.zip"
        download(args.url, archive)
        actual = sha256_file(archive)
        if actual != expected:
            raise SystemExit(f"OpenCC SHA-256 mismatch: expected {expected}, got {actual}")
        count = extract_opencc_archive(archive, args.destination)

    print(f"Verified and installed {count} OpenCC file(s) into {args.destination}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
