#!/usr/bin/env python3
"""Materialize reproducibility records from a v3 evidence commit.

The public profile keeps source documents, CSV, JSON, logs, scripts, and 24
selected formal qualitative panels. It omits bulk rendered outputs, cached
arrays, meshes, bytecode, and participant-level human-study CSVs. The private
profile differs only by retaining those four human-study CSVs.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
from pathlib import Path


SOURCE_PATH = "final/round2/scientific_validation_v3/"
PANEL_RE = re.compile(r"formal_qualitative_archive/panel_\d+_[0-9a-f]+\.png$")
HUMAN_RESULTS = "human_study_results_20261006/"


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


def exclusion_reason(relative: str, variant: str) -> str | None:
    suffix = Path(relative).suffix.lower()
    if suffix == ".npz":
        return "cached array or mask artifact; source data can regenerate it"
    if suffix == ".glb":
        return "intermediate 3D/render artifact; not required for paper-facing records"
    if suffix == ".pyc":
        return "generated Python bytecode"
    if suffix == ".png" and not PANEL_RE.fullmatch(relative):
        return "bulk rendered image; selected formal panels are retained"
    if (
        variant == "public"
        and relative.startswith(HUMAN_RESULTS)
        and suffix == ".csv"
    ):
        return "participant-level human-study record; retained only in private profile"
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="source Git commit")
    parser.add_argument("--base", required=True, help="existing authority commit")
    parser.add_argument("--variant", choices=("public", "private"), required=True)
    parser.add_argument("--destination", type=Path, default=Path.cwd())
    args = parser.parse_args()

    source = git("rev-parse", "--verify", f"{args.source}^{{commit}}").decode().strip()
    base = git("rev-parse", "--verify", f"{args.base}^{{commit}}").decode().strip()
    tree = git("ls-tree", "-r", "-l", "-z", source, "--", SOURCE_PATH)
    base_tree = git("ls-tree", "-r", "-l", "-z", base, "--", SOURCE_PATH)
    inherited: dict[str, tuple[str, int]] = {}
    for entry in base_tree.split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        _, object_type, oid, raw_size = metadata.decode().split()
        if object_type == "blob":
            inherited[os.fsdecode(raw_path)] = (oid, int(raw_size))
    included: list[tuple[str, str, int]] = []
    omitted: list[tuple[str, str, int, str]] = []
    source_count = 0
    inherited_count = 0
    inherited_bytes = 0
    total_bytes = 0
    conflicts: list[str] = []
    source_paths: set[str] = set()

    for entry in tree.split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        mode, object_type, oid, raw_size = metadata.decode().split()
        if object_type != "blob":
            continue
        source_path = os.fsdecode(raw_path)
        source_paths.add(source_path)
        relative = source_path.removeprefix(SOURCE_PATH)
        size = int(raw_size)
        source_count += 1
        total_bytes += size
        if source_path in inherited:
            if inherited[source_path][0] != oid:
                conflicts.append(source_path)
            else:
                inherited_count += 1
                inherited_bytes += size
            continue
        reason = exclusion_reason(relative, args.variant)
        if reason:
            omitted.append((relative, oid, size, reason))
        else:
            included.append((source_path, oid, size))

    restricted_base: list[tuple[str, str, int, str]] = []
    if args.variant == "public":
        for source_path, (oid, size) in inherited.items():
            if source_path in source_paths:
                continue
            relative = source_path.removeprefix(SOURCE_PATH)
            reason = exclusion_reason(relative, args.variant)
            if reason:
                row = (relative, oid, size, reason)
                omitted.append(row)
                restricted_base.append(row)

    if conflicts:
        raise SystemExit(
            "source/base path conflicts require authenticity review before import:\n"
            + "\n".join(conflicts)
        )

    archive_root = args.destination / SOURCE_PATH

    process = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    assert process.stdin is not None and process.stdout is not None
    copied_bytes = 0
    for source_path, oid, size in included:
        process.stdin.write(oid.encode("ascii") + b"\n")
        process.stdin.flush()
        header = process.stdout.readline().split()
        if len(header) != 3 or header[0].decode() != oid or header[1] != b"blob":
            raise RuntimeError(f"unexpected cat-file header for {source_path}: {header!r}")
        object_size = int(header[2])
        if object_size != size:
            raise RuntimeError(f"size mismatch for {source_path}: {object_size} != {size}")

        destination = args.destination / source_path
        if destination.exists():
            raise SystemExit(f"refusing to overwrite an existing file: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        remaining = object_size
        with destination.open("wb") as output:
            while remaining:
                chunk = process.stdout.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise RuntimeError(f"truncated object while copying {source_path}")
                output.write(chunk)
                remaining -= len(chunk)
        if process.stdout.read(1) != b"\n":
            raise RuntimeError(f"missing object delimiter after {source_path}")
        copied_bytes += object_size

    process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError("git cat-file failed")

    manifest = archive_root / "OMITTED_EXPERIMENT_ARTIFACTS.csv"
    with manifest.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("path", "bytes", "git_blob_oid", "reason"))
        for relative, oid, size, reason in omitted:
            writer.writerow((relative, size, oid, reason))

    report = archive_root / "ARCHIVE_CURATION.md"
    report.write_text(
        f"# Scientific validation v3 archive curation\n\n"
        f"- Source commit: {source}\n"
        f"- Authority base: {base}\n"
        f"- Profile: {args.variant}\n"
        f"- Source files: {source_count:,} "
        f"({total_bytes / 1024**3:.2f} GiB)\n"
        f"- Identical source files already present in the authority base: "
        f"{inherited_count:,} ({inherited_bytes / 1024**3:.2f} GiB)\n"
        f"- Newly retained source files: {len(included):,} "
        f"({copied_bytes / 1024**3:.2f} GiB)\n"
        f"- Omitted v3 source files and restricted base records: {len(omitted):,}\n"
        f"- Participant-level CSVs withheld from the public profile: "
        f"{len(restricted_base):,}\n\n"
        "All source Markdown, text, JSON, CSV, log, shell, and Python files are "
        "retained. The 24 selected formal qualitative panels are retained. "
        "Other rendered PNGs, cached NPZ files, GLB intermediates, and Python "
        "bytecode are omitted; their source paths, sizes, Git blob IDs, and "
        "reasons are recorded in OMITTED_EXPERIMENT_ARTIFACTS.csv. The public "
        "public profile omits participant-level human-study CSVs from both the "
        "source package and the authority-base snapshot; the private profile "
        "retains them. This file curation does not rewrite remote history. "
        "No results are pooled or promoted by this file selection.\n",
        encoding="utf-8",
    )
    print(
        f"{args.variant}: added {len(included):,} files "
        f"({copied_bytes / 1024**3:.2f} GiB); omitted {len(omitted):,} files "
        f"from {source}"
    )


if __name__ == "__main__":
    main()
