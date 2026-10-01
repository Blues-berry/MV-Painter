"""Merge the split temporary run and compute paired holdout statistics."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ROOT = Path("/4T/CXY/MV-Painter")
TMP = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule")
MERGED = TMP / "layer_official_v2_merged"
HEAD = TMP / "layer_official_v2_head" / "per_object_metrics.csv"
TAIL = TMP / "layer_official_v2_tail" / "per_object_metrics.csv"
BASE = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6"
STAGE = ROOT / "final/round2/stage_placement_276_20260929"

STANDARD = [
    "full_psnr", "full_ssim", "full_lpips", "fg_psnr", "fg_ssim",
    "fg_lpips", "edge_ssim",
]
TEXTURE = [
    "fg_rgb_std", "fg_grad_mag", "fg_lap_var", "fg_hf_energy",
    "gt_fg_rgb_std", "gt_fg_grad_mag", "gt_fg_lap_var", "gt_fg_hf_energy",
]
HIGHER = {"full_psnr", "full_ssim", "fg_psnr", "fg_ssim", "edge_ssim", "fg_mask_corr", "edge_fscore"}
LOWER = {"full_lpips", "fg_lpips", "bgwhite_lpips", "crop_lpips"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", "None", "nan", "NaN") else float("nan")


def index_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    indexed = {row["object"]: row for row in rows}
    if len(indexed) != len(rows):
        raise ValueError("duplicate object IDs")
    return indexed


def bootstrap_delta(left: np.ndarray, right: np.ndarray, seed: int = 20260929) -> dict[str, float]:
    delta = left - right
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(delta), size=(10000, len(delta)))
    means = delta[indices].mean(axis=1)
    return {
        "mean": float(delta.mean()),
        "median": float(np.median(delta)),
        "ci95_low": float(np.quantile(means, 0.025)),
        "ci95_high": float(np.quantile(means, 0.975)),
    }


def summarize_pair(left: dict[str, dict[str, str]], right: dict[str, dict[str, str]], metrics: list[str]) -> dict[str, object]:
    objects = sorted(set(left) & set(right))
    if len(objects) != 276:
        raise ValueError(f"pair has {len(objects)} objects, expected 276")
    out: dict[str, object] = {"n": len(objects), "metrics": {}}
    for metric in metrics:
        l = np.asarray([as_float(left[obj], metric) for obj in objects], dtype=np.float64)
        r = np.asarray([as_float(right[obj], metric) for obj in objects], dtype=np.float64)
        if not np.isfinite(l).all() or not np.isfinite(r).all():
            raise ValueError(f"non-finite metric: {metric}")
        diff = l - r
        higher = metric in HIGHER
        better = diff > 0 if higher else diff < 0
        out["metrics"][metric] = {
            "left_mean": float(l.mean()),
            "right_mean": float(r.mean()),
            "left_median": float(np.median(l)),
            "right_median": float(np.median(r)),
            "delta_left_minus_right": float(diff.mean()),
            "paired": bootstrap_delta(l, r),
            "win_rate_left": float(better.mean()),
            "higher_is_better": higher,
        }
    return out


def merge_layer() -> dict[str, dict[str, str]]:
    head = index_rows(read_csv(HEAD))
    tail = index_rows(read_csv(TAIL))
    head = {obj: row for obj, row in head.items() if int(row["object_idx"]) < 138}
    tail = {obj: row for obj, row in tail.items() if int(row["object_idx"]) >= 138}
    merged = {**head, **tail}
    expected = {f"obj_{idx:04d}" for idx in range(24, 300)}
    if set(merged) != expected:
        missing = sorted(expected - set(merged))
        extra = sorted(set(merged) - expected)
        raise ValueError(f"invalid merge: missing={missing}, extra={extra}")
    MERGED.mkdir(parents=True, exist_ok=True)
    rows = [merged[obj] for obj in sorted(merged)]
    with (MERGED / "per_object_metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return merged


def main() -> None:
    layer = merge_layer()
    main_baselines = {
        name: index_rows(read_csv(BASE / f"per_object_{name}.csv"))
        for name in ("fixed_low", "c3", "fixed_high")
    }
    stage_baselines = {
        name: index_rows(read_csv(STAGE / f"per_object_{name}.csv"))
        for name in ("fixed_mean", "c3_lhl", "llh", "hll")
    }
    comparisons: dict[str, object] = {}
    all_metrics = STANDARD + TEXTURE
    for name, rows in {**main_baselines, **stage_baselines}.items():
        comparisons[f"layer_vs_{name}"] = summarize_pair(layer, rows, all_metrics)

    summary = {
        "protocol": {
            "checkpoint": str(ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"),
            "object_ids": "obj_0024..obj_0299",
            "count": 276,
            "seed": 42,
            "steps": 50,
            "target_view_mode": "unique6",
            "layer_schedule": {
                "deep": [1.25, 2.50, 1.25],
                "middle": [1.25, 2.50, 1.25],
                "shallow": [0.50, 0.75, 0.50],
            },
            "temporary_only": True,
        },
        "row_counts": {
            "head_raw": len(read_csv(HEAD)),
            "head_used": sum(int(r["object_idx"]) < 138 for r in read_csv(HEAD)),
            "tail_raw": len(read_csv(TAIL)),
            "tail_used": sum(int(r["object_idx"]) >= 138 for r in read_csv(TAIL)),
            "merged": len(layer),
        },
        "comparisons": comparisons,
    }
    (MERGED / "official_comparisons.json").write_text(json.dumps(summary, indent=2) + "\n")

    lines = [
        "# Temporary official layer-LHL holdout analysis",
        "",
        "This report is outside the repository and uses the frozen clean-v2 276-object holdout.",
        "Rows are paired by object ID. Positive deltas mean layer-LHL minus comparator; for LPIPS, lower is better and win rates use the correct direction.",
        "",
        "## Standard metrics",
        "",
        "| comparator | Full PSNR | Full SSIM | Full LPIPS | FG PSNR | FG SSIM | FG LPIPS | Edge SSIM |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ["fixed_low", "c3", "fixed_high", "fixed_mean", "c3_lhl", "llh", "hll"]:
        comp = comparisons[f"layer_vs_{name}"]["metrics"]
        vals = []
        for metric in STANDARD:
            item = comp[metric]
            vals.append(f"{item['left_mean']:.4f} ({item['delta_left_minus_right']:+.4f})")
        lines.append(f"| layer vs {name} | " + " | ".join(vals) + " |")
    lines += [
        "",
        "Format: layer mean (layer minus comparator mean). Full details, medians, 95% paired bootstrap CIs, and win rates are in `official_comparisons.json`.",
        "",
        "## Texture probes",
        "",
        "| comparator | RGB std delta | gradient delta | Lap variance delta | HF energy delta |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ["fixed_low", "c3", "fixed_high", "fixed_mean", "c3_lhl", "llh", "hll"]:
        comp = comparisons[f"layer_vs_{name}"]["metrics"]
        vals = [comp[m]["delta_left_minus_right"] for m in ("fg_rgb_std", "fg_grad_mag", "fg_lap_var", "fg_hf_energy")]
        lines.append(f"| layer vs {name} | " + " | ".join(f"{x:+.6f}" for x in vals) + " |")
    (MERGED / "OFFICIAL_LAYER_LHL_REPORT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(summary["row_counts"], indent=2))
    print((MERGED / "OFFICIAL_LAYER_LHL_REPORT.md").read_text())


if __name__ == "__main__":
    main()
