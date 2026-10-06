#!/usr/bin/env python3
"""Refresh package provenance and checksums for the 1006 evidence bundle."""

from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "source_inventory.json"
CHECKSUMS = ROOT / "SHA256SUMS.txt"
EXCLUDED_SUFFIXES = {".aux", ".fdb_latexmk", ".fls", ".log", ".out", ".spl", ".pyc"}
EXCLUDED_DIRS = {".git", "__pycache__"}
EXCLUDED_RELATIVE_PREFIXES = (
    "data/fresh_c/source_cache/",
    "data/fresh_c/assets/",
    "data/fresh_c/renders/",
    "data/fresh_c/runs/",
    "data/e5_residual_dose/runs/",
    "data/e6_cap_calibration/runs/",
    "data/e6_cap_calibration/E6_EXECUTION_STATE.json",
    "data/fresh_c/FRESH_C_CLOSURE_EXECUTION_STATE.json",
    "data/fresh_d/source_cache/",
    "data/fresh_d/assets/",
    "data/fresh_d/renders/",
    "data/fresh_d/runs/",
    "human_private/",
)


def is_excluded(relative: Path) -> bool:
    rel = relative.as_posix()
    return (
        any(part in EXCLUDED_DIRS or part.endswith(".egg-info") for part in relative.parts)
        or relative.suffix in EXCLUDED_SUFFIXES | {".lock", ".tmp"}
        or any(rel.startswith(prefix) for prefix in EXCLUDED_RELATIVE_PREFIXES)
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    previous: dict[str, dict[str, str]] = {}
    if INVENTORY.exists():
        old = json.loads(INVENTORY.read_text(encoding="utf-8"))
        previous = {entry["package_path"]: entry for entry in old.get("entries", [])}

    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == INVENTORY or path == CHECKSUMS:
            continue
        relative = path.relative_to(ROOT)
        if is_excluded(relative):
            continue
        old_entry = previous.get(relative.as_posix(), {})
        files.append(
            {
                "package_path": relative.as_posix(),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "source_path": old_entry.get("source_path", "created_or_derived_in_1006"),
            }
        )

    INVENTORY.write_text(
        json.dumps({"created_utc": date.today().isoformat(), "entries": files}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    checksum_lines = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == CHECKSUMS:
            continue
        relative = path.relative_to(ROOT)
        if is_excluded(relative):
            continue
        checksum_lines.append(f"{sha256(path)}  {relative.as_posix()}")
    CHECKSUMS.write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    print(f"Indexed {len(files)} files; wrote {CHECKSUMS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
