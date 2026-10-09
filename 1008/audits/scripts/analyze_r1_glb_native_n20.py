#!/usr/bin/env python3
"""Verify stored GLB-native render artifacts and summarize paired N=20 results.

This is a read-only audit of existing files. It does not render, bake, or alter
any experiment input. Requires Python 3 and NumPy.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


METHODS = {
    "gt",
    "no_adapter",
    "native_gfl",
    "native_gfh",
    "native_gc3",
    "lfm_exact",
    "layer_lhl",
    "layer_llh",
}
CONTRASTS = [
    ("native_gc3", "native_gfl"),
    ("native_gc3", "native_gfh"),
    ("native_gc3", "no_adapter"),
]
METRICS = [
    ("fg_psnr", "masked_psnr", True),
    ("fg_lpips", "fg_lpips", False),
    ("ciede2000", "ciede2000", False),
]
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED = 20261005


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def verify_render_artifacts(manifest_path: Path, renderer_path: Path) -> tuple[dict, dict]:
    manifest = json.loads(manifest_path.read_text())
    expected_renderer_hash = manifest["renderer_script_sha256"]
    actual_renderer_hash = sha256(renderer_path)
    require(
        actual_renderer_hash == expected_renderer_hash,
        f"renderer hash mismatch: {actual_renderer_hash} != {expected_renderer_hash}",
    )

    renders = manifest["renders"]
    require(len(renders) == manifest["render_count"] == 1_760, "unexpected render count")
    require(len({r["source_glb"] for r in renders}) == 160, "expected 160 unique source GLBs")
    require(len({r["render_path"] for r in renders}) == 1_760, "duplicate render paths")
    require(set(manifest["rendered_methods"]) == METHODS, "unexpected render method set")
    require(len(manifest["rendered_objects"]) == 20, "expected 20 rendered objects")
    require(manifest["raw_views"] == list(range(1, 12)), "unexpected unseen-view set")

    checked = defaultdict(int)
    bad_cameras = 0
    camera_hashes: dict[tuple[str, int], set[str]] = defaultdict(set)
    samplers = set()
    render_root = manifest_path.parent

    for record in renders:
        glb_path = Path(record["source_glb"])
        require(glb_path.is_file(), f"missing GLB: {glb_path}")
        require(sha256(glb_path) == record["source_glb_sha256"], f"GLB hash mismatch: {glb_path}")
        checked["glb"] += 1

        metadata_path = glb_path.parent / "bake_metadata.json"
        require(metadata_path.is_file(), f"missing bake metadata: {metadata_path}")
        require(
            sha256(metadata_path) == record["source_bake_metadata_sha256"],
            f"bake metadata hash mismatch: {metadata_path}",
        )
        checked["bake_metadata"] += 1

        render_path = render_root / record["render_path"]
        require(render_path.is_file(), f"missing render: {render_path}")
        require(sha256(render_path) == record["render_sha256"], f"render hash mismatch: {render_path}")
        checked["render"] += 1

        camera_hashes[(record["object"], int(record["raw_view"]))].add(record["camera_sha256"])
        sampler = record["sampler"]
        samplers.add(tuple(sorted(sampler.items())))
        require(
            sampler == {"magFilter": 9729, "minFilter": 9987, "wrapS": 10497, "wrapT": 10497},
            f"unexpected embedded sampler semantics: {sampler}",
        )

    bad_cameras = sum(len(hashes) != 1 for hashes in camera_hashes.values())
    require(len(camera_hashes) == 20 * 11 and bad_cameras == 0, "camera hashes differ by method")
    require(len(samplers) == 1, "sampler semantics differ within the render set")
    require(checked == {"glb": 1_760, "bake_metadata": 1_760, "render": 1_760}, "incomplete artifact checks")

    summary = {
        "manifest_sha256": sha256(manifest_path),
        "renderer_sha256": actual_renderer_hash,
        "verified_glb_references": 160,
        "verified_glb_render_records": checked["glb"],
        "verified_bake_metadata_records": checked["bake_metadata"],
        "verified_render_pngs": checked["render"],
        "verified_camera_object_view_groups": len(camera_hashes),
        "camera_hash_disagreements": bad_cameras,
        "sampler": dict(next(iter(samplers))),
        "status": "PASS",
    }
    return manifest, summary


def read_object_metrics(path: Path, manifest: dict) -> tuple[dict, list[str]]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 160, f"expected 160 object-method rows; got {len(rows)}")

    methods = set(manifest["rendered_methods"])
    objects = sorted(manifest["rendered_objects"])
    keyed = {}
    for row in rows:
        uid, method = row["object"], row["method"]
        require(method in methods and uid in objects, f"unexpected object-method row: {uid}/{method}")
        require(int(row["unseen_views"]) == 11, f"unexpected unseen-view count for {uid}/{method}")
        key = (uid, method)
        require(key not in keyed, f"duplicate object-method metric row: {uid}/{method}")
        keyed[key] = row
        for _, column, _ in METRICS:
            require(math.isfinite(float(row[column])), f"non-finite {column} for {uid}/{method}")

    require(len(keyed) == 20 * len(methods), "object-method matrix is incomplete")
    require(set(keyed) == {(uid, method) for uid in objects for method in methods}, "object-method keys differ")
    return keyed, objects


def paired_rows(keyed: dict, objects: list[str], metrics_sha: str, manifest_sha: str) -> list[dict]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    output = []

    for metric_name, column, higher_is_better in METRICS:
        for method_a, method_b in CONTRASTS:
            a = np.array([float(keyed[(uid, method_a)][column]) for uid in objects])
            b = np.array([float(keyed[(uid, method_b)][column]) for uid in objects])
            delta = a - b
            favorable = delta > 0 if higher_is_better else delta < 0
            draws = rng.integers(0, len(objects), size=(BOOTSTRAP_DRAWS, len(objects)))
            boot_means = delta[draws].mean(axis=1)
            lower, upper = np.quantile(boot_means, [0.025, 0.975])

            for index, uid in enumerate(objects):
                output.append(
                    {
                        "row_type": "paired_object",
                        "cohort": "historical_n20_glb_native",
                        "object_uid": uid,
                        "method_a": method_a,
                        "method_b": method_b,
                        "metric": metric_name,
                        "direction": "higher_better" if higher_is_better else "lower_better",
                        "a_value": f"{a[index]:.12g}",
                        "b_value": f"{b[index]:.12g}",
                        "delta_a_minus_b": f"{delta[index]:.12g}",
                        "favorable_for_a": str(bool(favorable[index])).lower(),
                        "n_objects": len(objects),
                        "mean_a": "",
                        "mean_b": "",
                        "paired_mean_delta": "",
                        "ci95_lower": "",
                        "ci95_upper": "",
                        "favorable_object_count": "",
                        "favorable_object_fraction": "",
                        "adverse_object_count": "",
                        "bootstrap_draws": "",
                        "bootstrap_seed": "",
                        "source_metric_column": column,
                        "metrics_csv_sha256": metrics_sha,
                        "render_manifest_sha256": manifest_sha,
                        "note": "Object-level mean across 11 frozen unseen views; pair is the analysis unit.",
                    }
                )

            output.append(
                {
                    "row_type": "paired_summary",
                    "cohort": "historical_n20_glb_native",
                    "object_uid": "",
                    "method_a": method_a,
                    "method_b": method_b,
                    "metric": metric_name,
                    "direction": "higher_better" if higher_is_better else "lower_better",
                    "a_value": "",
                    "b_value": "",
                    "delta_a_minus_b": "",
                    "favorable_for_a": "",
                    "n_objects": len(objects),
                    "mean_a": f"{a.mean():.12g}",
                    "mean_b": f"{b.mean():.12g}",
                    "paired_mean_delta": f"{delta.mean():.12g}",
                    "ci95_lower": f"{lower:.12g}",
                    "ci95_upper": f"{upper:.12g}",
                    "favorable_object_count": int(favorable.sum()),
                    "favorable_object_fraction": f"{favorable.mean():.12g}",
                    "adverse_object_count": int((~favorable).sum()),
                    "bootstrap_draws": BOOTSTRAP_DRAWS,
                    "bootstrap_seed": BOOTSTRAP_SEED,
                    "source_metric_column": column,
                    "metrics_csv_sha256": metrics_sha,
                    "render_manifest_sha256": manifest_sha,
                    "note": "Paired percentile bootstrap over objects; intervals are descriptive and unadjusted.",
                }
            )

    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="GLB_NATIVE_EGL_RENDER_MANIFEST.json")
    parser.add_argument("--metrics", type=Path, required=True, help="UNSEEN_OBJECT_METRICS.csv")
    parser.add_argument("--renderer-script", type=Path, required=True, help="render_glb_native_egl.py")
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args()

    manifest, verification = verify_render_artifacts(args.manifest, args.renderer_script)
    keyed, objects = read_object_metrics(args.metrics, manifest)
    output_rows = paired_rows(keyed, objects, sha256(args.metrics), verification["manifest_sha256"])

    verification_row = {
        "row_type": "artifact_integrity",
        "cohort": "historical_n20_glb_native",
        "object_uid": "",
        "method_a": "",
        "method_b": "",
        "metric": "",
        "direction": "",
        "a_value": "",
        "b_value": "",
        "delta_a_minus_b": "",
        "favorable_for_a": "",
        "n_objects": 20,
        "mean_a": "",
        "mean_b": "",
        "paired_mean_delta": "",
        "ci95_lower": "",
        "ci95_upper": "",
        "favorable_object_count": "",
        "favorable_object_fraction": "",
        "adverse_object_count": "",
        "bootstrap_draws": "",
        "bootstrap_seed": "",
        "source_metric_column": "",
        "metrics_csv_sha256": sha256(args.metrics),
        "render_manifest_sha256": verification["manifest_sha256"],
        "note": json.dumps(verification, sort_keys=True),
    }

    fields = list(verification_row)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(verification_row)
        writer.writerows(output_rows)

    print(json.dumps({"output_csv": str(args.output_csv), "rows": len(output_rows) + 1, **verification}, indent=2))


if __name__ == "__main__":
    main()
