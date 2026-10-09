#!/usr/bin/env python3
"""Archive selected historical branch records without changing active files.

The output is a provenance snapshot, not an endorsement of any archived claim.
The public profile omits candidate human-study records; all profiles omit
generated image panels. The authenticated 01549 source remains the only
manuscript baseline.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path("1008/archive/branch_snapshots")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}
PAPER_1006_CONFLICTS = {
    "1006/evidence/audits/FINAL_REVIEWER_RESPONSE_SKELETON.md",
    "1006/evidence/audits/FORMAL_VISUAL_EVIDENCE_REPORT.md",
}
PAPER_1006_CONFLICT_REASON = (
    "reviewed; d59 version retained in the base tree; alternative blob remains "
    "traceable in the source commit; see CONFLICT_AUTHENTICITY_DECISIONS.md"
)


@dataclass(frozen=True)
class Source:
    snapshot: str
    revision: str
    selectors: tuple[tuple[str, str], ...]
    description: str


SOURCES = (
    Source(
        "round2-author-review-20260929",
        "96c35952673038b53213630deef2585c16267b58",
        (
            ("release/round2_author_review_20260929/", "release/round2_author_review_20260929/"),
            ("geotex/round2_main_eval.py", "source_conflicts/"),
            ("geotex/stage_placement_eval.py", "source_conflicts/"),
            ("geotex/cpu_texture_bake.py", "source_conflicts/"),
            ("geotex/evaluate_cpu_bakes.py", "source_conflicts/"),
            ("geotex/runtime.py", "source_conflicts/"),
        ),
        "2026-09-29 author-review release and the superseded runner variants",
    ),
    Source(
        "adaptive-control-pilot-20260929",
        "1b3867983a9e8dad23a657cbf4844c0b7453f87a",
        (
            ("TRB_PILOT_REVIEW_20260929.md", "unique/"),
            ("geotex/residual_budget_pilot.py", "unique/"),
            ("geotex/round2_main_eval.py", "source_conflicts/"),
            ("geotex/stage_placement_eval.py", "source_conflicts/"),
            ("geotex/cpu_texture_bake.py", "source_conflicts/"),
            ("geotex/evaluate_cpu_bakes.py", "source_conflicts/"),
            ("geotex/runtime.py", "source_conflicts/"),
        ),
        "2026-09-29 adaptive-control pilot records and its runner variants",
    ),
    Source(
        "paper-1006-candidate-20261007",
        "86292c8b5822533e52a1621cc04e6c076dbdc153",
        (("1006/", "1006/"),),
        "2026-10-07 candidate evidence package; not the manuscript baseline",
    ),
)


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def source_records(source: Source) -> list[tuple[str, str, str, int]]:
    selectors = [selector for selector, _ in source.selectors]
    raw = git("ls-tree", "-r", "-l", "-z", source.revision, "--", *selectors)
    found: dict[str, tuple[str, str, int]] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, oid, size = metadata.decode().split()
        if kind == "blob":
            found[os.fsdecode(raw_path)] = (mode, oid, int(size))
    for selector, _ in source.selectors:
        if not selector.endswith("/") and selector not in found:
            raise RuntimeError(f"expected source path is absent: {source.revision}:{selector}")
        if selector.endswith("/") and not any(path.startswith(selector) for path in found):
            raise RuntimeError(f"expected source directory is empty: {source.revision}:{selector}")
    return [(path, *found[path]) for path in sorted(found)]


def archive_path(source: Source, source_path: str) -> Path:
    for selector, destination_prefix in source.selectors:
        if selector.endswith("/") and source_path.startswith(selector):
            suffix = source_path[len(selector) :]
        elif source_path == selector:
            suffix = source_path
        else:
            continue
        return ARCHIVE / source.snapshot / destination_prefix / suffix
    raise RuntimeError(f"source path does not match its selectors: {source_path}")


def omission_reason(source: Source, path: str, variant: str) -> str | None:
    suffix = Path(path).suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        return "generated image panel/render omitted; source path and blob ID are recorded"
    if source.snapshot == "paper-1006-candidate-20261007":
        if path in PAPER_1006_CONFLICTS:
            return PAPER_1006_CONFLICT_REASON
        if path.startswith("1006/manuscript/"):
            return "candidate manuscript tree omitted; authenticated 01549 remains the baseline"
        if path.startswith("1006/figures/") and suffix == ".pdf":
            return "generated figure export omitted; data, scripts, and figure manifests are retained"
        if variant == "public" and any(
            marker in path.lower()
            for marker in ("human", "participant", "consent", "ethic")
        ):
            return "human-study material withheld from public candidate; retained only in private archive"
    return None


def materialize(source: Source, variant: str) -> tuple[int, int, int]:
    source_sha = git("rev-parse", "--verify", f"{source.revision}^{{commit}}").decode().strip()
    records = source_records(source)
    rows: list[tuple[str, str, str, int, str, str]] = []
    copied_bytes = 0
    included_count = 0
    omitted_count = 0

    for source_path, mode, oid, size in records:
        reason = omission_reason(source, source_path, variant)
        if reason:
            rows.append((source_path, "", oid, size, "omitted", reason))
            omitted_count += 1
            continue
        destination = ROOT / archive_path(source, source_path)
        if destination.exists():
            raise SystemExit(f"refusing to overwrite archived material: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = git("cat-file", "blob", oid)
        git_blob_oid = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
        if len(payload) != size or git_blob_oid != oid:
            raise RuntimeError(f"Git object integrity check failed: {source_path}")
        destination.write_bytes(payload)
        os.chmod(destination, 0o755 if mode.endswith("755") else 0o644)
        copied_bytes += size
        included_count += 1
        rows.append((source_path, destination.relative_to(ROOT).as_posix(), oid, size, "copied", ""))

    snapshot_root = ROOT / ARCHIVE / source.snapshot
    snapshot_root.mkdir(parents=True, exist_ok=True)
    manifest = snapshot_root / "IMPORT_MANIFEST.csv"
    with manifest.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("source_path", "archive_path", "git_blob_oid", "bytes", "disposition", "reason"))
        writer.writerows(rows)

    (snapshot_root / "README.md").write_text(
        f"# {source.snapshot} archive\n\n"
        f"Source commit: `{source_sha}`\n\n"
        f"{source.description}. This is a dated provenance archive; it does not make the archived claims, "
        "manuscripts, metrics, or scripts current authority. Active runner code and paper-facing claim "
        "authority remain at d59, and the only manuscript baseline is the authenticated 01549 source.\n\n"
        f"Profile: `{variant}`. Imported {included_count} files ({copied_bytes:,} bytes); omitted "
        f"{omitted_count} files. Each source path, Git blob ID, size, and disposition is recorded in "
        "`IMPORT_MANIFEST.csv`. No source or existing remote branch was modified.\n",
        encoding="utf-8",
    )
    return included_count, copied_bytes, omitted_count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("public",), required=True)
    args = parser.parse_args()
    for source in SOURCES:
        count, size, omitted = materialize(source, args.variant)
        print(f"{source.snapshot}: copied {count} files ({size:,} bytes), omitted {omitted}")


if __name__ == "__main__":
    main()
