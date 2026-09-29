"""Generate auditable Round-2 tables from one four-condition eval directory."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .round2_stats import paired_csv_summary, symmetric_log_error
except ImportError:
    from round2_stats import paired_csv_summary, symmetric_log_error


METHODS = ("no_adapter", "fixed_low", "fixed_high", "c3")
METRICS = (
    "full_psnr", "full_ssim", "full_lpips", "fg_psnr", "fg_ssim", "fg_lpips", "edge_ssim",
)
TEXTURE_METRICS = {
    "fg_rgb_std": "gt_fg_rgb_std",
    "fg_grad_mag": "gt_fg_grad_mag",
    "fg_lap_var": "gt_fg_lap_var",
    "fg_hf_energy": "gt_fg_hf_energy",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    out = {}
    for row in rows:
        key = row["object"]
        if key in out:
            raise ValueError(f"duplicate object {key} in {path}")
        out[key] = row
    return out


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset-manifest", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260928)
    parser.add_argument("--resamples", type=int, default=10000)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = {method: read_rows(args.input_dir / f"per_object_{method}.csv") for method in METHODS}
    all_ids = tuple(f"obj_{i:04d}" for i in range(300))
    if any(tuple(sorted(r)) != tuple(sorted(all_ids)) for r in rows.values()):
        raise ValueError("each condition must contain exactly obj_0000--obj_0299")
    splits = {
        "probe_24": all_ids[:24],
        "clean_holdout_276": all_ids[24:],
        "pooled_300": all_ids,
    }

    absolute = {}
    for split_name, object_ids in splits.items():
        out_rows = []
        for method in METHODS:
            out_rows.append({
                "condition": method,
                "n": len(object_ids),
                **{metric: float(np.mean([float(rows[method][o][metric]) for o in object_ids])) for metric in METRICS},
            })
        absolute[split_name] = out_rows
        write_csv(args.output_dir / f"absolute_{split_name}.csv", out_rows, ["condition", "n", *METRICS])

    comparisons = {}
    direction = {metric: metric not in {"full_lpips", "fg_lpips"} for metric in METRICS}
    for split_name, object_ids in splits.items():
        comparisons[split_name] = {}
        for baseline in ("no_adapter", "fixed_low", "fixed_high"):
            comparisons[split_name][f"c3_vs_{baseline}"] = paired_csv_summary(
                rows["c3"], rows[baseline], metrics=METRICS, object_ids=object_ids,
                higher_is_better=direction, seed=args.seed, n_resamples=args.resamples,
            )
    (args.output_dir / "paired_c3_vs_baselines.json").write_text(json.dumps({
        "seed": args.seed, "resamples": args.resamples, "direction": direction,
        "splits": comparisons,
    }, indent=2) + "\n")

    texture_rows = []
    for split_name, object_ids in splits.items():
        for method in METHODS:
            row = {"split": split_name, "condition": method, "n": len(object_ids)}
            for pred_key, gt_key in TEXTURE_METRICS.items():
                values = np.asarray([
                    symmetric_log_error(float(rows[method][o][pred_key]), float(rows[method][o][gt_key]))
                    for o in object_ids
                ])
                row[f"{pred_key}_error"] = float(values.mean())
            texture_rows.append(row)
    write_csv(args.output_dir / "texture_errors.csv", texture_rows, list(texture_rows[0]))

    manifest = {
        "input_dir": str(args.input_dir.resolve()),
        "evaluation_manifest_sha256": sha256(args.input_dir / "evaluation_manifest.json"),
        "dataset_manifest": str(args.dataset_manifest.resolve()),
        "dataset_manifest_sha256": sha256(args.dataset_manifest),
        "methods": METHODS,
        "metrics": METRICS,
        "splits": {name: len(ids) for name, ids in splits.items()},
        "bootstrap": {"seed": args.seed, "resamples": args.resamples},
        "texture_error": "abs(log((generated_stat+1e-6)/(GT_stat+1e-6)))",
    }
    (args.output_dir / "table_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
