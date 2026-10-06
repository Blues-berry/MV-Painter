#!/usr/bin/env python3
"""Reproduce the unified-bake UV-addressing and extreme-object sensitivity audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

import numpy as np
import trimesh

V3 = Path(__file__).resolve().parents[1]
ROOT = V3.parents[2]
BAKE = V3 / "bake_handoff"
OUT_DEFAULT = V3 / "audit_scripts/UV_ADDRESSING_AUDIT.json"
EXTREME_UID = "01e3b853f0f74bd0b44d34ac5106a84f"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or length != len(data):
        raise ValueError(f"invalid GLB header: {path}")
    offset = 12
    while offset < len(data):
        size, kind = struct.unpack_from("<I4s", data, offset)
        offset += 8
        chunk = data[offset : offset + size]
        offset += size
        if kind == b"JSON":
            return json.loads(chunk.decode("utf-8").rstrip("\x00 \t\r\n"))
    raise ValueError(f"GLB has no JSON chunk: {path}")


def uv_summary(glb: Path) -> dict:
    scene = trimesh.load(glb, force="scene", process=False)
    arrays = []
    for geometry in scene.geometry.values():
        uv = np.asarray(getattr(geometry.visual, "uv", []), dtype=np.float64)
        if uv.ndim == 2 and uv.shape[1] == 2 and len(uv):
            arrays.append(uv)
    if not arrays:
        return {"uv_pairs": 0}
    uv = np.concatenate(arrays)
    finite = np.isfinite(uv).all(axis=1)
    valid = uv[finite]
    outside = ((valid < 0) | (valid > 1)).any(axis=1)
    material = ((valid < -1e-3) | (valid > 1 + 1e-3)).any(axis=1)
    return {
        "uv_pairs": int(len(uv)),
        "finite_pairs": int(finite.sum()),
        "outside_unit_pairs": int(outside.sum()),
        "substantive_outside_pairs_tol_1e-3": int(material.sum()),
        "abs_gt_10_pairs": int((np.abs(valid) > 10).any(axis=1).sum()),
        "abs_gt_1e6_pairs": int((np.abs(valid) > 1e6).any(axis=1).sum()),
        "uv_min": valid.min(axis=0).tolist(),
        "uv_max": valid.max(axis=0).tolist(),
    }


def bootstrap_mean_ci(values: np.ndarray, seed: int = 20261005) -> list[float]:
    rng = np.random.default_rng(seed)
    sampled = values[rng.integers(0, len(values), size=(10_000, len(values)))].mean(axis=1)
    return [float(x) for x in np.quantile(sampled, [0.025, 0.975])]


def paired_sensitivity(metrics_path: Path) -> dict:
    rows = list(csv.DictReader(metrics_path.open()))
    out = {}
    for metric in ("masked_psnr", "fg_lpips", "ciede2000"):
        llh = {row["object"]: float(row[metric]) for row in rows
               if row["method"] == "layer_llh" and row[metric]}
        gfl = {row["object"]: float(row[metric]) for row in rows
               if row["method"] == "native_gfl" and row[metric]}
        objects = sorted(llh.keys() & gfl.keys())
        delta = np.array([llh[obj] - gfl[obj] for obj in objects], dtype=np.float64)
        records = {}
        for label, keep in (
            ("N20", np.ones(len(objects), dtype=bool)),
            ("N19_excluding_extreme_uv_uid", np.array([obj != EXTREME_UID for obj in objects])),
        ):
            values = delta[keep]
            records[label] = {
                "n_objects": int(len(values)),
                "mean_delta": float(values.mean()),
                "ci95_object_bootstrap": bootstrap_mean_ci(values),
                "positive_delta_count": int((values > 0).sum()),
            }
        out[metric] = {
            "unit": "LLH minus GFL; lower FG-LPIPS is favorable",
            "extreme_uid_delta": float(llh[EXTREME_UID] - gfl[EXTREME_UID]),
            **records,
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT_DEFAULT)
    args = parser.parse_args()

    handoff_path = BAKE / "BAKE_INPUT_HANDOFF_V3.json"
    handoff = json.loads(handoff_path.read_text())
    run = json.loads((BAKE / "cpu_bake_v3/BAKE_RUN_SUMMARY.json").read_text())
    excluded = set(json.loads((BAKE / "excluded_uv_missing.json").read_text()))
    metrics_path = BAKE / "cpu_bake_v3/UNSEEN_OBJECT_METRICS.csv"
    metrics_rows = list(csv.DictReader(metrics_path.open()))
    included = {row["object"] for row in metrics_rows}
    if len(metrics_rows) != len(included) * len(run["methods"]):
        raise SystemExit("Unseen metric rows are incomplete or duplicated.")
    if included != {record["object"] for record in handoff["objects"]} - excluded:
        raise SystemExit("Metrics object set differs from the frozen 24-minus-4 cohort.")

    source_objects = {}
    hash_mismatches = []
    for record in handoff["objects"]:
        uid = record["object"]
        source = Path(record["exact_glb_path"])
        current_hash = sha256(source)
        if current_hash != record["exact_glb_sha256"]:
            hash_mismatches.append(uid)
        if uid in included:
            source_objects[uid] = {
                "source_sha256": current_hash,
                **uv_summary(source),
            }

    sampler_checks = []
    sampler_mag_filters = Counter()
    sampler_min_filters = Counter()
    metadata_checks = []
    for uid in sorted(included):
        record = next(item for item in handoff["objects"] if item["object"] == uid)
        for method in run["methods"]:
            glb = BAKE / "cpu_bake_v3" / method / uid / f"{uid}_{method}_textured.glb"
            if not glb.is_file():
                raise SystemExit(f"Missing exported GLB: {uid}/{method}")
            samplers = glb_json(glb).get("samplers", [])
            sampler_mag_filters.update(str(item.get("magFilter", "UNSET")) for item in samplers)
            sampler_min_filters.update(str(item.get("minFilter", "UNSET")) for item in samplers)
            sampler_checks.append({
                "object": uid,
                "method": method,
                "sampler_count": len(samplers),
                "missing_wrap_s": all("wrapS" not in item for item in samplers),
                "missing_wrap_t": all("wrapT" not in item for item in samplers),
                "sha256": sha256(glb),
            })
            metadata_path = BAKE / "cpu_bake_v3" / method / uid / "bake_metadata.json"
            if metadata_path.is_file():
                metadata = json.loads(metadata_path.read_text())
                if metadata.get("object") != uid or metadata.get("method") != method:
                    raise SystemExit(f"Bake metadata identity mismatch: {uid}/{method}")
                if metadata.get("input_exact_glb") != record["exact_glb_path"]:
                    raise SystemExit(f"Bake metadata source-path mismatch: {uid}/{method}")
                metadata_checks.append({"object": uid, "method": method, "sha256": sha256(metadata_path)})

    seam_dir = BAKE / "BAKE_SEAM_AUDIT_V3"
    audit_script = ROOT / "scripts/audit_bake_seams_v3.py"
    metrics_path = BAKE / "cpu_bake_v3/UNSEEN_OBJECT_METRICS.csv"
    output = {
        "status": "UV_ADDRESSING_MISMATCH_CONFIRMED",
        "cohort": {
            "frozen_n": int(handoff["cohort_count"]),
            "baked_n": len(included),
            "no_uv_exclusions": sorted(excluded),
            "source_hash_mismatches": hash_mismatches,
            "baked_source_objects": source_objects,
            "unseen_metric_rows": len(metrics_rows),
            "unseen_metrics_sha256": sha256(metrics_path),
            "run_summary_objects": len(run["objects"]),
            "run_summary_object_ids": sorted(run["objects"]),
            "run_summary_omits_baked_objects": sorted(included - set(run["objects"])),
            "run_summary_records": len(run["records"]),
            "bake_metadata_records_found": len(metadata_checks),
            "bake_metadata_records": metadata_checks,
        },
        "sampler_audit": {
            "exported_glbs_checked": len(sampler_checks),
            "all_missing_wrap_s": all(x["missing_wrap_s"] for x in sampler_checks),
            "all_missing_wrap_t": all(x["missing_wrap_t"] for x in sampler_checks),
            "default_address_mode": "REPEAT per glTF 2.0",
            "mag_filter_values": dict(sorted(sampler_mag_filters.items())),
            "min_filter_values": dict(sorted(sampler_min_filters.items())),
            "filtering_note": "The frozen CPU renderer uses bilinear sampling without mipmaps; exported GLB minification filtering must also be matched for faithful-view validation.",
            "records": sampler_checks,
        },
        "bake_pipeline": {
            "script": "geotex/cpu_texture_bake.py",
            "sha256": sha256(ROOT / "geotex/cpu_texture_bake.py"),
            "exported_glbs_found": len(sampler_checks),
        },
        "seam_artifact_hashes": {
            "script_sha256": sha256(audit_script),
            "per_object_csv_sha256": sha256(seam_dir / "SEAM_AUDIT_PER_OBJECT.csv"),
            "aggregates_json_sha256": sha256(seam_dir / "SEAM_AUDIT_AGGREGATES.json"),
        },
        "existing_metric_sensitivity": {
            "source_sha256": sha256(metrics_path),
            "bootstrap": {"unit": "object", "resamples": 10000, "seed": 20261005, "ci": "percentile 95%"},
            "contrasts": paired_sensitivity(metrics_path),
        },
        "implementation": {
            "bake_clamp_lines": "geotex/cpu_texture_bake.py:289-290",
            "unseen_render_clamp_lines": "geotex/cpu_texture_bake.py:488-489",
            "seam_integer_cast_lines": "scripts/audit_bake_seams_v3.py:65-66",
            "corrected_bake_rerun": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({
        "output": str(args.output),
        "objects": output["cohort"]["baked_n"],
        "glbs_checked": output["sampler_audit"]["exported_glbs_checked"],
        "all_sampler_defaults_repeat": output["sampler_audit"]["all_missing_wrap_s"] and output["sampler_audit"]["all_missing_wrap_t"],
        "source_hash_mismatches": hash_mismatches,
    }, indent=2))


if __name__ == "__main__":
    main()
