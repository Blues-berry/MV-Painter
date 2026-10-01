#!/usr/bin/env python
"""P2 texture-fidelity extension for the strict-276 same-runner matrix.

Offline analysis (no GPU, no re-inference): computes GT-relative texture
error diagnostics from the per-object columns that the frozen runners
already logged (fg_* prediction stats + gt_fg_* GT stats), then paired
deltas + 10k percentile bootstrap for the frozen comparison family.

GT-relative errors (lower is better, per protocol lock):
  grad_err   = |fg_grad_mag  - gt_fg_grad_mag|  / gt_fg_grad_mag
  lap_err    = |fg_lap_var   - gt_fg_lap_var|   / gt_fg_lap_var
  rgbstd_err = |fg_rgb_std   - gt_fg_rgb_std|   / gt_fg_rgb_std
  hf_err     = |fg_hf_energy - gt_fg_hf_energy| / gt_fg_hf_energy

Sign convention: raw delta = first-named minus second; NO sign reversal.
Bootstrap seed 20260930, 10,000 resamples, object as sampling unit.
Reads all 7 condition sources when present (Core-5 frozen + Core-7 new).
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
OUT_DIR = ROOT / "final/round2/coordination/core7_same_runner_completion_20261001"
CONF_DIR = ROOT / "final/round2/coordination/main_backbone_robustness1_20260930"

# condition -> rows.json path (frozen R0 records + Core-7 completion)
SOURCES = {
    "global_fixed_low": Path("/4T/tmp/mvpainter-layer-confirmation-20260930/global_fixed_low_rows.json"),
    "global_c3": CONF_DIR / "r0_completion_global_c3/rows.json",
    "layer_fixed_mean": Path("/4T/tmp/mvpainter-layer-confirmation-20260930/layer_fixed_mean_rows.json"),
    "layer_lhl": Path("/4T/tmp/mvpainter-layer-confirmation-20260930/layer_lhl_rows.json"),
    "layer_llh": Path("/4T/tmp/mvpainter-layer-confirmation-20260930/layer_llh_rows.json"),
    "no_adapter": OUT_DIR / "formal_no_adapter/no_adapter_per_object_metrics.csv",
    "global_fixed_high": OUT_DIR / "formal_global_fixed_high/global_fixed_high_per_object_metrics.csv",
}

METRIC_KEYS = {
    "grad_err": ("fg_grad_mag", "gt_fg_grad_mag"),
    "lap_err": ("fg_lap_var", "gt_fg_lap_var"),
    "rgbstd_err": ("fg_rgb_std", "gt_fg_rgb_std"),
    "hf_err": ("fg_hf_energy", "gt_fg_hf_energy"),
}

# Frozen comparison family (first minus second; raw deltas, no sign reversal)
COMPARISONS = [
    ("layer_llh", "global_fixed_low", "primary: LLH vs frozen fixed-low control"),
    ("layer_llh", "global_c3", "primary family"),
    ("layer_llh", "layer_fixed_mean", "primary family"),
    ("layer_llh", "layer_lhl", "primary family"),
    ("layer_llh", "no_adapter", "Reviewer-1 unmodified-pipeline gate"),
    ("layer_llh", "global_fixed_high", "Reviewer-1 competitive-fixed-baseline gate"),
    ("no_adapter", "global_fixed_low", "does the adapter help at all (same runner)"),
    ("global_fixed_high", "global_fixed_low", "fixed-scale direction (same runner)"),
]

BOOTSTRAP_SEED = 20260930
BOOTSTRAP_N = 10_000


def load_condition(name: str, path: Path) -> dict[int, dict[str, float]]:
    if not path.exists():
        return {}
    if path.suffix == ".json":
        rows = json.loads(path.read_text())
    else:
        with path.open(newline="") as handle:
            rows = list(csv.DictReader(handle))
    per_object = {}
    for row in rows:
        idx = int(row["object_idx"])
        per_object[idx] = {k: float(v) for k, v in row.items()
                           if k not in {"object", "object_idx", "schedule", "seed_base",
                                        "elapsed_seconds", "input_hashes"}}
    return per_object


def texture_errors(stats: dict[str, float]) -> dict[str, float]:
    out = {}
    for name, (pred_key, gt_key) in METRIC_KEYS.items():
        pred = stats[pred_key]
        gt = stats[gt_key]
        out[name] = abs(pred - gt) / gt if gt > 0 else float("nan")
    return out


def paired_bootstrap(delta: np.ndarray, rng_seed: int) -> dict:
    rng = np.random.default_rng(rng_seed)
    n = len(delta)
    boot = delta[rng.integers(0, n, size=(BOOTSTRAP_N, n))].mean(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    wins = float((delta > 0).sum() + 0.5 * (delta == 0).sum())
    return {
        "n": int(n),
        "mean_delta": float(delta.mean()),
        "median_delta": float(np.median(delta)),
        "ci95_low": float(lo),
        "ci95_high": float(hi),
        "ci_excludes_zero": bool(lo > 0 or hi < 0),
        "win_rate": float(wins / n),
    }


def main() -> None:
    data: dict[str, dict[int, dict[str, float]]] = {}
    for name, path in SOURCES.items():
        per_object = load_condition(name, path)
        if per_object:
            data[name] = per_object
            print(f"loaded {name}: {len(per_object)} objects from {path}")
        else:
            print(f"SKIP {name}: source missing ({path})")

    available = sorted(data)
    if len(available) < 2:
        raise RuntimeError("need at least two conditions")

    # integrity: GT statistic columns must be identical across conditions per object
    gt_keys = [gt for _, gt in METRIC_KEYS.values()]
    ref_name = "layer_llh"
    mismatches = 0
    for name in available:
        if name == ref_name:
            continue
        for idx in data[ref_name]:
            if idx not in data[name]:
                continue
            for key in gt_keys:
                if abs(data[ref_name][idx][key] - data[name][idx][key]) > 0:
                    mismatches += 1
    print(f"GT-column cross-condition integrity: {mismatches} mismatches")

    # per-condition per-object texture errors
    errors: dict[str, dict[int, dict[str, float]]] = {}
    for name in available:
        errors[name] = {idx: texture_errors(stats) for idx, stats in data[name].items()}

    # aggregate means per condition
    agg_rows = []
    for name in available:
        row: dict[str, object] = {"condition": name, "n": len(errors[name])}
        for metric in METRIC_KEYS:
            vals = [e[metric] for e in errors[name].values() if not np.isnan(e[metric])]
            row[f"{metric}_mean"] = float(np.mean(vals))
            row[f"{metric}_median"] = float(np.median(vals))
            row[f"{metric}_nan"] = len(errors[name]) - len(vals)
        agg_rows.append(row)

    # paired deltas + bootstrap
    comparison_rows = []
    bootstrap_out = {}
    for first, second, note in COMPARISONS:
        if first not in data or second not in data:
            print(f"comparison {first} - {second}: SKIP (condition missing)")
            continue
        common = sorted(set(errors[first]) & set(errors[second]))
        for metric in METRIC_KEYS:
            deltas = np.array([
                errors[first][idx][metric] - errors[second][idx][metric]
                for idx in common
                if not (np.isnan(errors[first][idx][metric]) or np.isnan(errors[second][idx][metric]))
            ])
            if len(deltas) == 0:
                continue
            stats = paired_bootstrap(deltas, BOOTSTRAP_SEED)
            key = f"{first}-minus-{second}/{metric}"
            bootstrap_out[key] = {"note": note, **stats}
            comparison_rows.append({
                "comparison": f"{first} - {second}",
                "metric": metric,
                "direction": "lower-is-better (raw delta, no sign reversal)",
                "note": note,
                **stats,
            })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / "TEXTURE_FIDELITY_EXTENSION_BOOTSTRAP.json").open("w") as handle:
        json.dump({
            "protocol": "texture-fidelity-extension-strict276-v1 (offline, from frozen per-object columns)",
            "definitions": {k: f"abs({p} - {g}) / {g}" for k, (p, g) in METRIC_KEYS.items()},
            "sign_convention": "raw delta = first minus second; lower-is-better metrics; NO sign reversal",
            "bootstrap": {"seed": BOOTSTRAP_SEED, "resamples": BOOTSTRAP_N, "unit": "object"},
            "gt_column_integrity_mismatches": mismatches,
            "conditions_used": available,
            "comparisons": bootstrap_out,
        }, handle, indent=2)
        handle.write("\n")

    fields = list(comparison_rows[0])
    with (OUT_DIR / "TEXTURE_FIDELITY_EXTENSION_COMPARISONS.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(comparison_rows)

    fields = list(agg_rows[0])
    with (OUT_DIR / "TEXTURE_FIDELITY_EXTENSION_AGGREGATES.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(agg_rows)

    print(f"wrote {len(comparison_rows)} comparison rows; conditions: {available}")


if __name__ == "__main__":
    main()
