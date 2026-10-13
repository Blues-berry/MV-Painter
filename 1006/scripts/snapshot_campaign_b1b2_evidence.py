#!/usr/bin/env python3
"""Copy compact campaign-B1/B2 records and index its full output payload."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path("/4T/CXY/MV-Painter")
SOURCE = ROOT / "final/round2/scientific_validation_v3/formal/campaign_B1B2"
MANIFEST = ROOT / "final/round2/scientific_validation_v3/FULL_ARTIFACT_MANIFEST.json"
DEST = ROOT / "1006/data/campaign_B1B2_prior"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def copy_immutable(source: Path, destination: Path, expected_sha: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if sha256(destination) != expected_sha:
            raise RuntimeError(f"existing snapshot file differs: {destination}")
        return
    shutil.copy2(source, destination)
    if sha256(destination) != expected_sha:
        raise RuntimeError(f"copied source hash mismatch: {destination}")


def main() -> None:
    artifact_manifest = json.loads(MANIFEST.read_text())
    entries = [e for e in artifact_manifest["entries"]
               if e.get("path", "").startswith("formal/campaign_B1B2/")]
    if not entries:
        raise RuntimeError("campaign-B1/B2 source inventory is empty")
    DEST.mkdir(parents=True, exist_ok=True)
    copied = []
    for entry in entries:
        rel = Path(entry["path"]).relative_to("formal/campaign_B1B2")
        source = SOURCE / rel
        if not source.is_file() or source.stat().st_size != entry["size_bytes"]:
            raise RuntimeError(f"campaign-B1/B2 source missing or size mismatch: {rel}")
        if sha256(source) != entry["sha256"]:
            raise RuntimeError(f"campaign-B1/B2 source differs from frozen artifact hash: {rel}")
        copy_in_1006 = len(rel.parts) == 1
        if copy_in_1006:
            copy_immutable(source, DEST / rel, entry["sha256"])
            copied.append(rel.as_posix())
        entry["source_path"] = source.relative_to(ROOT).as_posix()
        entry["snapshot_path_1006"] = (DEST / rel).relative_to(ROOT).as_posix() if copy_in_1006 else None
        entry["copied_to_1006"] = copy_in_1006

    inventory = {
        "status": "COMPACT_DATA_SNAPSHOT_VERIFIED",
        "source_campaign": SOURCE.relative_to(ROOT).as_posix(),
        "source_full_artifact_manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "source_full_artifact_manifest_sha256": sha256(MANIFEST),
        "source_entry_count": len(entries),
        "source_total_bytes": sum(e["size_bytes"] for e in entries),
        "files_copied_to_1006": len(copied),
        "copied_file_names": sorted(copied),
        "large_payloads_policy": "prediction PNGs and per-step residual JSON remain at the source path; every file path, byte size, and SHA-256 is listed here",
        "entries": entries,
    }
    (DEST / "SOURCE_DATA_MANIFEST.json").write_text(json.dumps(inventory, indent=2) + "\n")
    print(json.dumps({"status": inventory["status"], "campaign_files": len(entries),
                      "copied_files": len(copied), "source_bytes": inventory["source_total_bytes"]}, indent=2))


if __name__ == "__main__":
    main()
