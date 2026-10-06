#!/usr/bin/env python3
"""Audit native-GLB render integrity and compare with legacy CPU metrics."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


V3 = Path(__file__).resolve().parents[1]
BAKE = V3 / "bake_handoff"
DEFAULT_RENDER = BAKE / "GLB_NATIVE_EGL_RENDER_V1"
EXTREME_UV_UID = "01e3b853f0f74bd0b44d34ac5106a84f"
METRICS = ("masked_psnr", "fg_lpips", "ciede2000", "silhouette_iou")
CONTRAST_METHODS = (
    "native_gfl",
    "native_gfh",
    "native_gc3",
    "lfm_exact",
    "layer_lhl",
    "no_adapter",
    "gt",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def values_by_object(rows: list[dict[str, str]], metric: str) -> dict[tuple[str, str], float]:
    return {
        (row["object"], row["method"]): float(row[metric])
        for row in rows
        if row.get(metric, "") not in ("", "None")
    }


def bootstrap_mean_ci(values: np.ndarray) -> list[float]:
    rng = np.random.default_rng(20261005)
    sample = values[rng.integers(0, len(values), size=(10_000, len(values)))].mean(axis=1)
    return [float(x) for x in np.quantile(sample, [0.025, 0.975])]


def audit_render_files(manifest: dict, render_root: Path, legacy_root: Path) -> dict:
    renders = manifest["renders"]
    keys = [(r["object"], r["method"], int(r["raw_view"])) for r in renders]
    missing = []
    hash_mismatches = []
    mask_xor = []
    min_iou = 1.0
    pixel_count = 0
    for row in renders:
        uid, method, view = row["object"], row["method"], int(row["raw_view"])
        render_path = render_root / row["render_path"]
        legacy_path = legacy_root / method / uid / "unseen_renders" / f"view_{view:03d}.png"
        if not render_path.is_file() or not legacy_path.is_file():
            missing.append({"object": uid, "method": method, "raw_view": view})
            continue
        if sha256(render_path) != row["render_sha256"]:
            hash_mismatches.append(str(render_path))
        if Image.open(render_path).size != (512, 512):
            raise ValueError(f"unexpected render dimensions: {render_path}")
        a = np.asarray(Image.open(render_path).convert("RGBA"))[:, :, 3] > 127
        b = np.asarray(Image.open(legacy_path).convert("RGBA"))[:, :, 3] > 127
        diff = int(np.count_nonzero(a ^ b))
        union = int(np.count_nonzero(a | b))
        inter = int(np.count_nonzero(a & b))
        mask_xor.append(diff)
        min_iou = min(min_iou, inter / union if union else 1.0)
        pixel_count += int(a.size)

    source_paths = sorted({Path(r["source_glb"]) for r in renders})
    source_hash_mismatches = []
    source_hashes = {}
    for path in source_paths:
        uid_method = f"{path.parent.parent.name}/{path.parent.name}"
        expected = next(r["source_glb_sha256"] for r in renders if Path(r["source_glb"]) == path)
        current = sha256(path)
        source_hashes[uid_method] = current
        if current != expected:
            source_hash_mismatches.append(str(path))

    return {
        "manifest_render_count": len(renders),
        "unique_object_method_view_keys": len(set(keys)),
        "missing_render_pairs": missing,
        "render_sha256_mismatches": hash_mismatches,
        "unique_source_glbs_hashed": len(source_paths),
        "source_glb_sha256_mismatches": source_hash_mismatches,
        "source_glb_sha256": source_hashes,
        "native_vs_legacy_alpha_mask": {
            "pairs_compared": len(mask_xor),
            "missing_pairs": len(missing),
            "pixel_xor_total": int(sum(mask_xor)),
            "max_pixel_xor_per_view": int(max(mask_xor, default=0)),
            "views_with_any_edge_difference": int(sum(value != 0 for value in mask_xor)),
            "fraction_of_mask_pixels_identical": (
                float(1 - sum(mask_xor) / pixel_count) if pixel_count else None
            ),
            "minimum_pairwise_iou": float(min_iou),
            "interpretation": "The comparison checks scene geometry/cameras; edge rasterization can differ by a few boundary pixels.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-dir", type=Path, default=DEFAULT_RENDER)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    render_root = args.render_dir.resolve()
    legacy_root = BAKE / "cpu_bake_v3"
    manifest_path = render_root / "GLB_NATIVE_EGL_RENDER_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    native_rows = read_rows(render_root / "UNSEEN_OBJECT_METRICS.csv")
    legacy_rows = read_rows(legacy_root / "UNSEEN_OBJECT_METRICS.csv")
    objects = sorted(manifest["rendered_objects"])
    methods = manifest["rendered_methods"]
    if len(native_rows) != len(objects) * len(methods):
        raise ValueError("native object metric ledger has missing or duplicated rows")
    if len(legacy_rows) != len(objects) * len(methods):
        raise ValueError("legacy object metric ledger has missing or duplicated rows")

    means = {}
    deltas = {}
    contrasts = {}
    for metric in METRICS:
        native = values_by_object(native_rows, metric)
        legacy = values_by_object(legacy_rows, metric)
        means[metric] = {}
        deltas[metric] = {}
        for method in methods:
            means[metric][method] = {
                "native_glb_mean": float(np.mean([native[u, method] for u in objects])),
                "legacy_cpu_mean": float(np.mean([legacy[u, method] for u in objects])),
                "native_minus_legacy_mean": float(
                    np.mean([native[u, method] - legacy[u, method] for u in objects])
                ),
            }
        if metric == "silhouette_iou":
            continue
        contrasts[metric] = {}
        for comparator in CONTRAST_METHODS:
            values = np.asarray(
                [native[uid, "layer_llh"] - native[uid, comparator] for uid in objects],
                dtype=np.float64,
            )
            keep = np.asarray([uid != EXTREME_UV_UID for uid in objects])
            contrast_rows = {}
            for label, selected in (("N20", np.ones(len(objects), dtype=bool)), ("N19_excluding_extreme_uv_uid", keep)):
                selected_values = values[selected]
                contrast_rows[label] = {
                    "n_objects": int(len(selected_values)),
                    "mean_delta": float(selected_values.mean()),
                    "object_bootstrap_ci95": bootstrap_mean_ci(selected_values),
                }
            contrasts[metric][f"layer_llh_minus_{comparator}"] = {
                "positive_delta_favors_llh": metric in ("masked_psnr", "silhouette_iou"),
                "lower_is_better_for_llh": metric in ("fg_lpips", "ciede2000"),
                **contrast_rows,
            }

    file_audit = audit_render_files(manifest, render_root, legacy_root)
    if file_audit["missing_render_pairs"] or file_audit["render_sha256_mismatches"] or file_audit["source_glb_sha256_mismatches"]:
        raise ValueError("native GLB render file/hash integrity audit failed")

    evaluator = render_root / "UNSEEN_METRICS_SUMMARY.json"
    metric_summary = json.loads(evaluator.read_text())
    metric_summary.update(
        {
            "protocol": "glb-native-basecolor-unseen-evaluation-v1",
            "renderer_manifest_sha256": sha256(manifest_path),
            "metric_definitions": "unchanged from geotex/evaluate_cpu_bakes.py; object means pool 11 frozen unseen raw views",
            "legacy_cpu_render_is_comparator_only": True,
        }
    )
    evaluator.write_text(json.dumps(metric_summary, indent=2, sort_keys=True) + "\n")

    result = {
        "protocol": "glb-native-basecolor-metric-reconciliation-v1",
        "status": "PASS_RENDER_AND_SOURCE_HASHES",
        "interpretation": "Stored exported GLBs were sampled with their embedded glTF baseColor sampler. This is an unlit base-color image comparison, not a full PBR viewer study or a re-bake.",
        "cohort": {
            "frozen_n": int(manifest["frozen_cohort_n"]),
            "supported_rendered_n": len(objects),
            "prebake_no_uv_exclusions": manifest["prebake_no_uv_exclusions"],
            "methods": methods,
            "raw_unseen_views": manifest["raw_views"],
            "extreme_uv_sensitivity_uid": EXTREME_UV_UID,
            "extreme_uv_rule": "report full supported N=20 and prespecified N=19 omission for the UID already classified as |UV|>1e6; no outcome-based exclusion",
        },
        "renderer_manifest_sha256": sha256(manifest_path),
        "renderer_script_sha256": manifest["renderer_script_sha256"],
        "native_metrics_sha256": {
            "per_view": sha256(render_root / "UNSEEN_PER_VIEW_METRICS.csv"),
            "per_object": sha256(render_root / "UNSEEN_OBJECT_METRICS.csv"),
            "summary": sha256(evaluator),
        },
        "legacy_metrics_sha256": sha256(legacy_root / "UNSEEN_OBJECT_METRICS.csv"),
        "file_integrity_and_geometry_checks": file_audit,
        "condition_means_and_legacy_delta": means,
        "layer_llh_minus_comparator_object_bootstrap": {
            "unit": "object; metric is each object's mean across 11 views",
            "resamples": 10000,
            "seed": 20261005,
            "ci": "percentile 95%",
            "multiplicity_adjustment": "none; only the LLH versus native_gfl 3D comparison has prior descriptive focus; all other contrasts are exploratory",
            "contrasts": contrasts,
        },
        "retrospective_practical_scale_reference": {
            "status": "descriptive only; not a significance test or acceptance threshold",
            "source": "PRACTICAL_EFFECT_REFERENCE.md, repeated-realization development probe",
            "fg_psnr_drift_median": 3.094010,
            "fg_psnr_drift_p95": 9.548559,
            "fg_lpips_drift_median": 0.026770,
            "fg_lpips_drift_p95": 0.112665,
            "absolute_mean_effect_over_drift": {
                "layer_llh_minus_native_gfl": {
                    "fg_psnr": {
                        "over_median": abs(contrasts["masked_psnr"]["layer_llh_minus_native_gfl"]["N20"]["mean_delta"]) / 3.094010,
                        "over_p95": abs(contrasts["masked_psnr"]["layer_llh_minus_native_gfl"]["N20"]["mean_delta"]) / 9.548559,
                    },
                    "fg_lpips": {
                        "over_median": abs(contrasts["fg_lpips"]["layer_llh_minus_native_gfl"]["N20"]["mean_delta"]) / 0.026770,
                        "over_p95": abs(contrasts["fg_lpips"]["layer_llh_minus_native_gfl"]["N20"]["mean_delta"]) / 0.112665,
                    },
                },
                "layer_llh_minus_lfm_exact": {
                    "fg_psnr": {
                        "over_median": abs(contrasts["masked_psnr"]["layer_llh_minus_lfm_exact"]["N20"]["mean_delta"]) / 3.094010,
                        "over_p95": abs(contrasts["masked_psnr"]["layer_llh_minus_lfm_exact"]["N20"]["mean_delta"]) / 9.548559,
                    },
                    "fg_lpips": {
                        "over_median": abs(contrasts["fg_lpips"]["layer_llh_minus_lfm_exact"]["N20"]["mean_delta"]) / 0.026770,
                        "over_p95": abs(contrasts["fg_lpips"]["layer_llh_minus_lfm_exact"]["N20"]["mean_delta"]) / 0.112665,
                    },
                },
            },
        },
        "metric_availability": {
            "lpips": metric_summary.get("lpips"),
            "dists": metric_summary.get("dists"),
        },
        "limitations": [
            "Four frozen objects without UVs were excluded before the bake; this analysis does not close strict 24-object 3D coverage.",
            "Textures were created by the original clamp-based bake and are evaluated as the exported GLBs actually store them; no repeat-aware re-bake was performed.",
            "The renderer matches the embedded base-color addressing/filtering on the recorded NVIDIA EGL implementation; extreme 1e36-scale UV precision can vary across graphics implementations.",
            "Base-color-only rendering omits lighting/material BRDF and does not establish human-perceived material fidelity.",
            "The 40-slot human study remains pre-collection; no participant responses are included.",
        ],
    }
    output_path = args.output.resolve() if args.output else render_root / "GLB_NATIVE_EGL_ANALYSIS.json"
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "status": result["status"],
                "native_render_count": file_audit["manifest_render_count"],
                "mask_audit": file_audit["native_vs_legacy_alpha_mask"],
                "native_mean_metrics": {
                    metric: means[metric]["layer_llh"]["native_glb_mean"] for metric in ("masked_psnr", "fg_lpips", "ciede2000")
                },
                "LLH_minus_GFL": {
                    metric: contrasts[metric]["layer_llh_minus_native_gfl"] for metric in contrasts
                },
                "analysis": str(output_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
