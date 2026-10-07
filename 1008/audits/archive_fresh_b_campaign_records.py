#!/usr/bin/env python3
"""Import checksum-verified Fresh B records while omitting generated PNGs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V3 = Path("final/round2/scientific_validation_v3")
CAMPAIGNS = (
    "campaign_FRESH_CONFIRM_B_20261005",
    "campaign_FRESH_CONFIRM_B_GENERIC_EXTENSION_20261005",
)
EXPECTED_SOURCE_COMMIT = "5c2c8829a1e19b42837761160dc4c14cf8f09045"
CHECKSUMS = Path(
    "1008/archive/branch_snapshots/paper-1006-candidate-20261007/1006/"
    "logs/fresh_b/B_PREUNBLIND_SHA256SUMS.txt"
)
SNAPSHOT = Path("1008/archive/branch_snapshots/fresh-b-campaign-records-20261007")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        type=Path,
        required=True,
        help="Original validation worktree containing the two Fresh B campaigns",
    )
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    source_v3 = source_root / V3
    formal = source_v3 / "formal"
    destination_formal = ROOT / V3 / "formal"
    snapshot_root = ROOT / SNAPSHOT
    checksum_file = ROOT / CHECKSUMS

    if not source_v3.is_dir() or not checksum_file.is_file():
        raise SystemExit("source worktree or frozen B checksum inventory is missing")
    if snapshot_root.exists():
        raise SystemExit(f"refusing to overwrite archive snapshot: {snapshot_root}")
    destinations = [destination_formal / name for name in CAMPAIGNS]
    if any(path.exists() for path in destinations):
        raise SystemExit("refusing to overwrite an existing Fresh B campaign directory")

    source_commit = subprocess.check_output(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if source_commit != EXPECTED_SOURCE_COMMIT:
        raise SystemExit(
            f"unexpected source worktree commit: {source_commit}; "
            f"expected {EXPECTED_SOURCE_COMMIT}"
        )
    expected: dict[str, str] = {}
    for line in checksum_file.read_text().splitlines():
        if line.strip():
            sha, path = line.split(None, 1)
            expected[path.strip()] = sha

    source_files: list[tuple[Path, str, str, int]] = []
    expected_paths = {
        path
        for path in expected
        if any(path.startswith(f"formal/{campaign}/") for campaign in CAMPAIGNS)
    }
    actual_paths: set[str] = set()
    for campaign in CAMPAIGNS:
        source_dir = formal / campaign
        if not source_dir.is_dir():
            raise SystemExit(f"source campaign directory is missing: {source_dir}")
        for path in sorted(source_dir.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(source_v3).as_posix()
            inventory_path = (Path("formal") / path.relative_to(formal)).as_posix()
            actual_paths.add(inventory_path)
            actual_sha = digest(path)
            if expected.get(inventory_path) != actual_sha:
                raise SystemExit(f"checksum mismatch or missing inventory entry: {rel}")
            source_files.append((path, rel, actual_sha, path.stat().st_size))

    if actual_paths != expected_paths:
        missing = sorted(expected_paths - actual_paths)[:5]
        extra = sorted(actual_paths - expected_paths)[:5]
        raise SystemExit(f"checksum inventory coverage differs; missing={missing} extra={extra}")

    destination_formal.mkdir(parents=True, exist_ok=True)
    snapshot_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".fresh-b-records-", dir=destination_formal))
    snapshot_stage = Path(tempfile.mkdtemp(prefix=".fresh-b-manifest-", dir=snapshot_root.parent))
    rows = []
    copied_count = copied_bytes = omitted_count = 0
    moved: list[Path] = []
    try:
        for source, rel, sha, size in source_files:
            relative_campaign_path = Path(rel).relative_to("formal")
            staged_path = stage / relative_campaign_path
            is_image = source.suffix.lower() in IMAGE_SUFFIXES
            if is_image:
                archive_path = ""
                disposition = "omitted"
                reason = "generated image omitted by upload scope; source SHA-256 verified"
                omitted_count += 1
            else:
                staged_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, staged_path)
                archive_path = (V3 / "formal" / relative_campaign_path).as_posix()
                disposition = "copied"
                reason = ""
                copied_count += 1
                copied_bytes += size
            rows.append(
                (rel, archive_path, source_commit, sha, size, disposition, reason)
            )

        manifest_path = snapshot_stage / "IMPORT_MANIFEST.csv"
        with manifest_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(
                ("source_path", "archive_path", "source_git_commit", "sha256", "bytes", "disposition", "reason")
            )
            writer.writerows(rows)
        readme = (
            "# Fresh B campaign records\n\n"
            f"Source worktree HEAD: `{source_commit}`. Source files were read from\n"
            "the preserved scientific-validation worktree and checked against\n"
            f"`{CHECKSUMS.as_posix()}` before import. The inventory is explicitly\n"
            "retrospective after prior B outcome disclosure; it is integrity\n"
            "evidence, not a pre-unblinding lock.\n\n"
            f"Copied {copied_count} non-image files ({copied_bytes:,} bytes),\n"
            f"including per-object residual JSON logs, result JSON, CSVs, and\n"
            f"run logs. Omitted {omitted_count} generated images. Every source\n"
            "file and omission is listed with SHA-256 and size in\n"
            "`IMPORT_MANIFEST.csv`. Statistical and residual-budget analyses\n"
            "can resolve their row, CSV, and log inputs. PNG-dependent integrity\n"
            "checks need the omitted renders and cannot be rerun from this\n"
            "reduced package.\n"
        )
        (snapshot_stage / "README.md").write_text(readme, encoding="utf-8")

        for name, destination in zip(CAMPAIGNS, destinations):
            os.replace(stage / name, destination)
            moved.append(destination)
        os.replace(snapshot_stage, snapshot_root)
    except Exception:
        for path in moved:
            shutil.rmtree(path, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)
        if snapshot_stage.exists():
            shutil.rmtree(snapshot_stage, ignore_errors=True)

    print(
        f"copied {copied_count} non-image files ({copied_bytes:,} bytes); "
        f"omitted {omitted_count} generated images; verified {len(rows)} source files"
    )


if __name__ == "__main__":
    main()
