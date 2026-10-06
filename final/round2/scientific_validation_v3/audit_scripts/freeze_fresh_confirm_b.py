#!/usr/bin/env python3
"""Audit and freeze the unused, technically valid FRESH_CONFIRM_B cohort.

The script aborts if any candidate UID already has a method-result row or if
any candidate's 17 decoded GT views duplicate a selected or candidate object.
It hashes every file in each frozen object directory and the corresponding
source GLB before any B method output is permitted.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from PIL import Image

ROOT = Path("/4T/CXY/MV-Painter")
V3 = ROOT / "final/round2/scientific_validation_v3"
AUDIT = V3 / "technical_validity_audit.json"
SELECTED = V3 / "fresh_confirm_300.txt"
RENDER_ROOT = ROOT / "data/fresh_confirm_v3_renders"
GLB_ROOT = Path("/home/ubuntu/.objaverse/hf-objaverse-v1/glbs")
OUT = V3 / "fresh_confirm_b"
VIEWS = tuple(f"{i:03d}" for i in range(17))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def pixel_sha(path: Path) -> str:
    with Image.open(path) as im:
        rgba = im.convert("RGBA")
        digest = hashlib.sha256()
        digest.update(f"{rgba.width}x{rgba.height}\0".encode())
        digest.update(rgba.tobytes())
        return digest.hexdigest()


def find_glb(uid: str) -> Path:
    found = sorted(GLB_ROOT.glob(f"*/{uid}.glb"))
    if len(found) != 1:
        raise RuntimeError(f"expected one source GLB for {uid}, found {len(found)}")
    return found[0]


def method_output_uids() -> set[str]:
    found: set[str] = set()
    uid_pattern = re.compile(r"^[0-9a-f]{32}$")
    for p in V3.rglob("rows_shard*.json"):
        rows = json.loads(p.read_text())
        for row in rows:
            uid = row.get("source_uid") or row.get("object_uid")
            if not uid and uid_pattern.fullmatch(str(row.get("object", ""))):
                uid = row["object"]
            if uid:
                found.add(str(uid))
    for p in V3.rglob("per_object_metrics*.csv"):
        with p.open(newline="") as f:
            for row in csv.DictReader(f):
                uid = row.get("source_uid") or row.get("object_uid")
                if not uid and uid_pattern.fullmatch(str(row.get("object", ""))):
                    uid = row["object"]
                if uid:
                    found.add(str(uid))
    return found


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    validity = json.loads(AUDIT.read_text())
    selected = {x.strip() for x in SELECTED.read_text().splitlines() if x.strip()}
    valid = {r["uid"]: r for r in validity["rows"] if r["reason"] == "ok"}
    assert len(valid) == 450
    assert len(selected) == 300 and selected <= valid.keys()
    cohort = sorted(set(valid) - selected)
    assert len(cohort) == 150

    overlap = sorted(set(cohort) & method_output_uids())
    if overlap:
        raise RuntimeError(f"candidate objects already have method outputs: {overlap}")

    selected_pixel: dict[tuple[str, ...], list[str]] = defaultdict(list)
    pool_pixel: dict[tuple[str, ...], list[str]] = defaultdict(list)
    pool_mesh: dict[str, list[str]] = defaultdict(list)
    pixel_by_uid: dict[str, tuple[str, ...]] = {}
    mesh_by_uid: dict[str, str] = {}
    for n, uid in enumerate(sorted(valid), 1):
        views = [RENDER_ROOT / uid / "image" / f"{v}.png" for v in VIEWS]
        if not all(p.is_file() for p in views):
            raise RuntimeError(f"missing one or more 17-view inputs for {uid}")
        signature = tuple(pixel_sha(p) for p in views)
        pixel_by_uid[uid] = signature
        pool_pixel[signature].append(uid)
        if uid in selected:
            selected_pixel[signature].append(uid)
        mesh_sha = sha256(find_glb(uid))
        mesh_by_uid[uid] = mesh_sha
        pool_mesh[mesh_sha].append(uid)
        if n % 100 == 0:
            print(f"audited pixel and source identity for {n}/450", flush=True)

    duplicates = [group for group in pool_pixel.values() if len(group) > 1]
    cross_duplicates = [g for g in duplicates if any(u in selected for u in g)
                        and any(u in cohort for u in g)]
    within_b_duplicates = [g for g in duplicates if all(u in cohort for u in g)]
    within_used_duplicates = [g for g in duplicates if all(u in selected for u in g)]
    source_duplicates = [group for group in pool_mesh.values() if len(group) > 1]
    if cross_duplicates or within_b_duplicates or source_duplicates:
        raise RuntimeError(json.dumps({
            "cross_selected_remainder_pixel_duplicates": cross_duplicates,
            "remainder_internal_pixel_duplicates": within_b_duplicates,
            "source_glb_byte_duplicates": source_duplicates,
        }))

    manifest_objects = []
    for i, uid in enumerate(cohort):
        obj_dir = RENDER_ROOT / uid
        mesh = find_glb(uid)
        files = []
        for p in sorted(q for q in obj_dir.rglob("*") if q.is_file()):
            entry = {"relative_path": p.relative_to(obj_dir).as_posix(),
                     "bytes": p.stat().st_size, "sha256": sha256(p)}
            if p.parent.name == "image" and p.suffix.lower() == ".png":
                entry["decoded_rgba_sha256"] = pixel_sha(p)
            files.append(entry)
        view_files = [obj_dir / "image" / f"{v}.png" for v in VIEWS]
        manifest_objects.append({
            "object": f"b_{i:04d}",
            "source_uid": uid,
            "render_root": str(obj_dir),
            "mesh_path": str(mesh),
            "mesh_bytes": mesh.stat().st_size,
            "mesh_sha256": mesh_by_uid[uid],
            "gt_images_official_order": [str(obj_dir / "image" / f"{v}.png")
                                          for v in ("014", "000", "012", "013", "015", "016")],
            "reference_image": str(obj_dir / "image/000.png"),
            "all_17_view_pixel_hashes": list(pixel_by_uid[uid]),
            "files": files,
        })

    cohort_path = OUT / "fresh_confirm_b.txt"
    cohort_path.write_text("".join(uid + "\n" for uid in cohort))
    manifest = {
        "protocol": "Scientific Validation V3 evidence-closure FRESH_CONFIRM_B",
        "frozen_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_validity_audit": str(AUDIT),
        "source_validity_audit_sha256": sha256(AUDIT),
        "source_selected_cohort": str(SELECTED),
        "source_selected_cohort_sha256": sha256(SELECTED),
        "pool_size": len(valid),
        "prior_selected_count": len(selected),
        "remainder_count": len(cohort),
        "candidate_count_with_prior_method_output": 0,
        "cross_selected_remainder_pixel_duplicate_groups": cross_duplicates,
        "within_remainder_pixel_duplicate_groups": within_b_duplicates,
        "within_selected_pixel_duplicate_groups": within_used_duplicates,
        "source_glb_byte_duplicate_groups": source_duplicates,
        "objects": manifest_objects,
    }
    manifest_path = OUT / "FRESH_CONFIRM_B_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    report = {
        "valid_pool": len(valid),
        "already_selected": len(selected),
        "candidate_objects": len(cohort),
        "candidate_prior_method_output_overlap": overlap,
        "candidate_source_glb_sha256_duplicates": source_duplicates,
        "pixel_identical_groups_within_selected": within_used_duplicates,
        "pixel_identical_groups_within_candidate": within_b_duplicates,
        "pixel_identical_groups_crossing_selected_candidate": cross_duplicates,
        "manifest_sha256": sha256(manifest_path),
        "cohort_txt_sha256": sha256(cohort_path),
        "status": "FROZEN_BEFORE_B_METHOD_OUTPUT",
    }
    report_path = OUT / "FRESH_CONFIRM_B_IDENTITY_AUDIT.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    lock = f"""# FRESH_CONFIRM_B lock

Frozen before any method output: {manifest['frozen_at_utc']}

The cohort is the complete remainder of the 450 technically valid identities
after removing all 300 IDs in `fresh_confirm_300.txt`, sorted by source UID.
No candidate has a prior method-result row in the V3 object-condition ledgers
or per-object metric files. Every object has its frozen source GLB and complete
render directory hashed in `FRESH_CONFIRM_B_MANIFEST.json`.

Identity audit: 150 candidates; zero prior-output overlap; zero source-GLB byte
duplicates; zero 17-view decoded-pixel duplicate groups within the candidate
or crossing from the previous 300. The known pixel-identical pair
0099ab6d44b742b0b62a40a7c70c29b1 / 0130e5149b6f4156b9799daa5e4006da is wholly
inside the already-used 300 and is preserved in the audit. No outcome-driven
selection or object replacement was performed.

Manifest SHA256: `{sha256(manifest_path)}`
Frozen UID-list SHA256: `{sha256(cohort_path)}`
Identity-audit SHA256: `{sha256(report_path)}`
"""
    (OUT / "FRESH_CONFIRM_B_LOCK.md").write_text(lock)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
