#!/usr/bin/env python3
"""Build the human-readable FRESH_CONFIRM_B freeze package from its frozen JSON."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
V3 = ROOT / "final/round2/scientific_validation_v3"
PKG = V3 / "fresh_confirm_b"
MANIFEST = PKG / "FRESH_CONFIRM_B_MANIFEST.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = json.loads(MANIFEST.read_text())
    objects = data["objects"]
    ids = [row["source_uid"] for row in objects]
    uid_path = PKG / "fresh_confirm_b.txt"
    if uid_path.read_text().splitlines() != ids:
        raise RuntimeError("UID list order/content differs from frozen manifest")
    if len(ids) != 150 or len(set(ids)) != 150:
        raise RuntimeError(f"expected 150 unique identities, found {len(ids)}")
    if data["candidate_count_with_prior_method_output"] != 0:
        raise RuntimeError("frozen manifest reports prior method-output overlap")
    if data["cross_selected_remainder_pixel_duplicate_groups"]:
        raise RuntimeError("frozen manifest reports cross-cohort pixel duplicates")
    if data["within_remainder_pixel_duplicate_groups"] or data["source_glb_byte_duplicate_groups"]:
        raise RuntimeError("frozen manifest reports duplicate candidate content")

    alias = PKG / "fresh_confirm_B_150.txt"
    alias.write_bytes(uid_path.read_bytes())
    csv_path = PKG / "fresh_confirm_B_manifest.csv"
    fields = ["object", "source_uid", "mesh_path", "mesh_bytes", "mesh_sha256",
              "render_root", "reference_image", "gt_images_official_order_json",
              "view_count", "all_17_view_pixel_hashes_json"]
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in objects:
            writer.writerow({
                "object": row["object"],
                "source_uid": row["source_uid"],
                "mesh_path": row["mesh_path"],
                "mesh_bytes": row["mesh_bytes"],
                "mesh_sha256": row["mesh_sha256"],
                "render_root": row["render_root"],
                "reference_image": row["reference_image"],
                "gt_images_official_order_json": json.dumps(row["gt_images_official_order"], separators=(",", ":")),
                "view_count": len(row["all_17_view_pixel_hashes"]),
                "all_17_view_pixel_hashes_json": json.dumps(row["all_17_view_pixel_hashes"], separators=(",", ":")),
            })

    disjointness = PKG / "FRESH_CONFIRM_B_DISJOINTNESS_AUDIT.md"
    disjointness.write_text(
        "# FRESH_CONFIRM_B disjointness audit\n\n"
        "Derived from the frozen identity audit and complete per-object input manifest; "
        "no method outputs were read.\n\n"
        f"- Valid source pool: {data['pool_size']} technically valid identities.\n"
        f"- Previously selected FRESH_CONFIRM_300: {data['prior_selected_count']}.\n"
        f"- Complete unused remainder selected: {data['remainder_count']} identities.\n"
        f"- Candidate identities with prior method output: {data['candidate_count_with_prior_method_output']}.\n"
        f"- Source GLB byte duplicate groups in the candidate: {len(data['source_glb_byte_duplicate_groups'])}.\n"
        f"- Pixel duplicate groups within candidate: {len(data['within_remainder_pixel_duplicate_groups'])}.\n"
        f"- Pixel duplicate groups crossing selected/candidate cohorts: {len(data['cross_selected_remainder_pixel_duplicate_groups'])}.\n"
        "- Selection: every valid unused identity, sorted by source UID; no outcome-based exclusions or substitutions.\n\n"
        f"UID list SHA256: `{sha256(uid_path)}`  \n"
        f"Complete JSON input-manifest SHA256: `{sha256(MANIFEST)}`  \n"
    )

    source_inputs = [
        V3 / "technical_validity_audit.json",
        V3 / "fresh_confirm_300.txt",
        V3 / "audit_scripts/freeze_fresh_confirm_b.py",
    ]
    for p in source_inputs:
        if not p.is_file():
            raise FileNotFoundError(p)
    package_files = [
        uid_path, alias, MANIFEST, csv_path,
        PKG / "FRESH_CONFIRM_B_IDENTITY_AUDIT.json",
        PKG / "FRESH_CONFIRM_B_LOCK.md", disjointness,
        Path(__file__).resolve(), *source_inputs,
    ]
    sums = PKG / "SHA256SUMS.txt"
    lines = [f"{sha256(p)}  {p.relative_to(ROOT)}" for p in sorted(set(package_files))]
    sums.write_text("\n".join(lines) + "\n")
    print(json.dumps({
        "uids": len(ids), "csv_rows": sum(1 for _ in csv.DictReader(csv_path.open())),
        "uid_sha256": sha256(uid_path), "manifest_sha256": sha256(MANIFEST),
        "checksums": str(sums.relative_to(ROOT)), "checksum_entries": len(lines),
    }, indent=2))


if __name__ == "__main__":
    main()
