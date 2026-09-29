"""Freeze the independent exact-GLB baking cohort without changing evaluation data."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import trimesh


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "final/round2/main_adapter_clean_v2"
GLB_DIR = OUT / "exact_glbs"
EVAL_RENDER = OUT / "exact_glb_validation"
EVAL_DIR = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6"
OBJECTS = ROOT / "final/round2/clean_dataset_v2/eval_objects_300_clean_v2.txt"
MAPPING = ROOT / "final/round2/main_adapter_clean_v2/clean_v2_provenance_300.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    uids = [x.strip() for x in OBJECTS.read_text().splitlines() if x.strip()]
    provenance = {r["uid"]: r for r in csv.DictReader(MAPPING.open())}
    with (EVAL_DIR / "per_object_c3.csv").open(newline="") as f:
        c3 = {r["object"]: r for r in csv.DictReader(f)}
    with (EVAL_DIR / "per_object_fixed_high.csv").open(newline="") as f:
        high = {r["object"]: r for r in csv.DictReader(f)}

    candidates = []
    for glb in sorted(GLB_DIR.glob("*.glb")):
        if glb.stem not in uids:
            continue
        idx = uids.index(glb.stem)
        object_id = f"obj_{idx:04d}"
        scene = trimesh.load(glb, force="scene", process=False)
        geoms = list(scene.geometry.values()) if hasattr(scene, "geometry") else [scene]
        uv_ok = all(getattr(getattr(g, "visual", None), "uv", None) is not None for g in geoms)
        delta = float(c3[object_id]["fg_psnr"]) - float(high[object_id]["fg_psnr"])
        candidates.append({
            "object": object_id,
            "position": idx,
            "uid": glb.stem,
            "glb": str(glb),
            "glb_sha256": sha256(glb),
            "glb_bytes": glb.stat().st_size,
            "mesh_geometry_count": len(geoms),
            "mesh_uv_available": uv_ok,
            "source_type": provenance.get(glb.stem, {}).get("source_type", ""),
            "source_file_identifier": provenance.get(glb.stem, {}).get("source_file_identifier", ""),
            "validation_render_dir": str(EVAL_RENDER / object_id),
            "c3_fg_psnr": float(c3[object_id]["fg_psnr"]),
            "fixed_high_fg_psnr": float(high[object_id]["fg_psnr"]),
            "c3_minus_fixed_high_fg_psnr": delta,
        })
    if len(candidates) < 1:
        raise RuntimeError("no disjoint exact GLBs found")
    if len(candidates) >= 12:
        candidates = sorted(candidates, key=lambda x: x["position"])[:12]
    ranked = sorted(candidates, key=lambda x: (x["c3_minus_fixed_high_fg_psnr"], x["uid"]))
    n = len(ranked)
    for rank, row in enumerate(ranked):
        row["fixed_stratum_rank"] = rank + 1
        row["fixed_stratum"] = "failure" if rank < n / 3 else ("general" if rank < 2 * n / 3 else "success")
        row["stratum_rule"] = "rank by clean-v2 C3 minus fixed-high FG-PSNR; lower third failure, middle third general, upper third success"
    rows = sorted(ranked, key=lambda x: x["position"])
    fields = list(rows[0])
    with (OUT / "exact_baking_cohort_manifest.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "protocol": "clean-v2-independent-exact-glb-cohort-v1",
        "cohort_count": len(rows),
        "requested_count": 12,
        "independence_rule": "UID not in historical 1,118-object train list; clean-v2 list intersection is zero",
        "mesh_rule": "original recovered GLB retained; original UVs required; no proxy mesh",
        "stratification_rule": rows[0]["stratum_rule"],
        "objects": rows,
        "not_used_for": ["checkpoint selection", "C3 selection", "dataset replacement selection"],
    }
    (OUT / "exact_baking_cohort_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"cohort_count": len(rows), "strata": {s: sum(r["fixed_stratum"] == s for r in rows) for s in ("failure", "general", "success")}}, indent=2))


if __name__ == "__main__":
    main()
