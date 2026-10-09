#!/usr/bin/env python3
"""Preserve 1006 human-study provenance in the private candidate only."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = "86292c8b5822533e52a1621cc04e6c076dbdc153"
ARCHIVE = Path(
    "1008/archive/branch_snapshots/paper-1006-candidate-20261007/private_only"
)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}
MARKERS = ("human", "participant", "consent", "ethic")


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-private", action="store_true", required=True)
    args = parser.parse_args()
    del args
    branch = git("branch", "--show-current").decode().strip()
    if branch != "codex/cg-round2-1008-revision-20261008":
        raise SystemExit(f"refusing to run outside private candidate branch: {branch}")

    revision = git("rev-parse", "--verify", f"{SOURCE}^{{commit}}").decode().strip()
    raw = git("ls-tree", "-r", "-l", "-z", revision, "--", "1006/")
    entries = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, oid, size = metadata.decode().split()
        path = os.fsdecode(raw_path)
        if kind == "blob" and any(marker in path.lower() for marker in MARKERS):
            entries.append((path, mode, oid, int(size)))

    root = ROOT / ARCHIVE
    rows = []
    copied_bytes = 0
    for source_path, mode, oid, size in sorted(entries):
        if Path(source_path).suffix.lower() in IMAGE_SUFFIXES:
            rows.append((source_path, "", oid, size, "omitted", "generated human-study image"))
            continue
        destination = root / source_path
        if destination.exists():
            raise SystemExit(f"refusing to overwrite private archive material: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = git("cat-file", "blob", oid)
        object_oid = hashlib.sha1(
            b"blob " + str(len(payload)).encode() + b"\0" + payload
        ).hexdigest()
        if len(payload) != size or object_oid != oid:
            raise RuntimeError(f"Git object integrity check failed: {source_path}")
        destination.write_bytes(payload)
        os.chmod(destination, 0o755 if mode.endswith("755") else 0o644)
        copied_bytes += size
        rows.append(
            (source_path, destination.relative_to(ROOT).as_posix(), oid, size, "copied", "private-only")
        )

    root.mkdir(parents=True, exist_ok=True)
    with (root / "IMPORT_MANIFEST.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            ("source_path", "archive_path", "git_blob_oid", "bytes", "disposition", "reason")
        )
        writer.writerows(rows)
    (root / "README.md").write_text(
        "# Private-only human-study history\n\n"
        f"Source commit: `{revision}`. This dated archive preserves the candidate branch's human-study "
        "protocol, aggregate result tables, analysis code, and audit notes for private provenance only. "
        "It is not current paper evidence and does not establish confirmatory status or public redistribution "
        "permission. Generated forest plots are omitted. File provenance and exclusions are listed in "
        "`IMPORT_MANIFEST.csv`.\n",
        encoding="utf-8",
    )
    print(
        f"private-only human archive: {len(entries)} source files, "
        f"{sum(1 for row in rows if row[4] == 'copied')} copied ({copied_bytes:,} bytes), "
        f"{sum(1 for row in rows if row[4] == 'omitted')} generated images omitted"
    )


if __name__ == "__main__":
    main()
