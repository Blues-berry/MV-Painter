#!/usr/bin/env python
"""Core-7 same-runner strict-276 analysis (protocol-frozen, 2026-10-01).

Loads the five frozen R0 Core-5 conditions plus the two Core-7 completion
conditions (no_adapter, global_fixed_high), verifies cross-process
shared-input integrity from the recorded per-row hashes, and produces:
  - combined per_object_metrics.csv (552 new rows appended to context)
  - aggregate_metrics_core7.csv (7 conditions x metrics, mean/median)
  - core7_rankings.json (per-metric condition ranking)
  - paired_bootstrap_core7.json (frozen comparison family; RAW deltas,
    first minus second, NO sign reversal; directions labelled)
  - SHARED_INPUT_AUDIT_CORE7.json/.md
  - CORE7_SAME_RUNNER_REPORT.md

Bootstrap: 10,000 resamples, seed 20260930, object as sampling unit.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path("/4T/CXY/MV-Painter")
OUT = ROOT / "final/round2/coordination/core7_same_runner_completion_20261001"
CONF = ROOT / "final/round2/coordination/main_backbone_robustness1_20260930"
TMP = Path("/4T/tmp/mvpainter-layer-confirmation-20260930")

SOURCES = {
    "global_fixed_low": TMP / "global_fixed_low_rows.json",
    "global_c3": CONF / "r0_completion_global_c3/rows.json",
    "layer_fixed_mean": TMP / "layer_fixed_mean_rows.json",
    "layer_lhl": TMP / "layer_lhl_rows.json",
    "layer_llh": TMP / "layer_llh_rows.json",
    "no_adapter": OUT / "formal_no_adapter/no_adapter_per_object_metrics.csv",
    "global_fixed_high": OUT / "formal_global_fixed_high/global_fixed_high_per_object_metrics.csv",
}

COMPARISONS = [
    ("layer_llh", "no_adapter", "Reviewer-1 unmodified-pipeline gate"),
    ("layer_llh", "global_fixed_high", "Reviewer-1 competitive-fixed-baseline gate"),
    ("layer_llh", "global_fixed_low", "primary same-runner control"),
    ("layer_llh", "global_c3", "primary family"),
    ("layer_llh", "layer_fixed_mean", "primary family"),
    ("layer_llh", "layer_lhl", "primary family"),
    ("no_adapter", "global_fixed_low", "does the adapter help at all (same runner)"),
    ("global_fixed_high", "global_fixed_low", "fixed-scale direction (same runner)"),
]

HIGHER_BETTER = {"full_psnr", "full_ssim", "fg_psnr", "fg_ssim", "edge_ssim"}
LOWER_BETTER = {"full_lpips", "fg_lpips"}
CORE_METRICS = ["fg_psnr", "fg_ssim", "fg_lpips", "full_psnr", "full_ssim", "full_lpips", "edge_ssim"]
BOOT_SEED = 20260930
BOOT_N = 10_000


def load_condition(name: str, path: Path) -> dict[int, dict[str, float]]:
    if not path.exists():
        return {}
    if path.suffix == ".json":
        rows = json.loads(path.read_text())
    else:
        with path.open(newline="") as handle:
            rows = list(csv.DictReader(handle))
    return {int(r["object_idx"]): {k: float(v) for k, v in r.items()
            if k not in {"object", "object_idx", "schedule", "seed_base", "elapsed_seconds", "input_hashes"}}
            for r in rows}


def bootstrap(delta: np.ndarray) -> dict:
    rng = np.random.default_rng(BOOT_SEED)
    n = len(delta)
    boot = delta[rng.integers(0, n, size=(BOOT_N, n))].mean(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    wins = float((delta > 0).sum() + 0.5 * (delta == 0).sum())
    return {"n": int(n), "mean_delta": float(delta.mean()), "median_delta": float(np.median(delta)),
            "ci95_low": float(lo), "ci95_high": float(hi),
            "ci_excludes_zero": bool(lo > 0 or hi < 0), "win_rate_first": float(wins / n)}


def main() -> None:
    data: dict[str, dict[int, dict[str, float]]] = {}
    for name, path in SOURCES.items():
        d = load_condition(name, path)
        if d:
            data[name] = d
            print(f"loaded {name}: {len(d)} objects")
    if len(data) != 7 or any(len(v) != 276 for v in data.values()):
        raise RuntimeError(f"expected 7 conditions x 276 objects, got "
                           f"{ {k: len(v) for k, v in data.items()} }")

    # ---- shared-input integrity from recorded hashes (new conditions only)
    audit_rows = []
    for name in ("no_adapter", "global_fixed_high"):
        src = OUT / ("formal_no_adapter" if name == "no_adapter" else "formal_global_fixed_high") / "rows.json"
        rows = json.loads(src.read_text())
        for r in rows:
            audit_rows.append({"condition": name, "object_idx": int(r["object_idx"]),
                               **r["input_hashes"]})
    def hashes_for(condition, idx):
        return {k: v for k, v in next(r for r in audit_rows
                if r["condition"] == condition and r["object_idx"] == idx).items()
                if k not in ("condition", "object_idx")}
    common = sorted(set(range(276)))
    cross_method_mismatch = 0
    for idx in common:
        if hashes_for("no_adapter", idx) != hashes_for("global_fixed_high", idx):
            cross_method_mismatch += 1
    audit = {
        "cross_process_input_mismatches": cross_method_mismatch,
        "compared_objects": len(common),
        "hash_fields": ["cond", "target", "normal", "depth", "global_embeds", "init_latent"],
        "note": "within-process cross-method equality was enforced in-run (abort on mismatch); "
                "the two formal conditions ran on separate GPUs (cuda:0 / cuda:1).",
    }
    (OUT / "SHARED_INPUT_AUDIT_CORE7.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(f"shared-input audit: {cross_method_mismatch} cross-process mismatches / {len(common)} objects")

    # ---- aggregates + rankings
    agg_rows = []
    rankings = {}
    for metric in CORE_METRICS:
        vals = {name: float(np.mean([d[metric] for d in data[name].values()])) for name in data}
        reverse = metric in HIGHER_BETTER
        order = sorted(vals, key=lambda k: vals[k], reverse=reverse)
        rankings[metric] = {"direction": "higher-is-better" if reverse else "lower-is-better",
                            "order_best_to_worst": order,
                            "means": vals}
    for name in sorted(data):
        row = {"condition": name, "n": len(data[name])}
        for metric in CORE_METRICS:
            row[f"{metric}_mean"] = float(np.mean([d[metric] for d in data[name].values()]))
            row[f"{metric}_median"] = float(np.median([d[metric] for d in data[name].values()]))
        agg_rows.append(row)
    with (OUT / "aggregate_metrics_core7.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(agg_rows[0]))
        writer.writeheader()
        writer.writerows(agg_rows)
    (OUT / "core7_rankings.json").write_text(json.dumps(rankings, indent=2) + "\n")

    # ---- paired bootstrap (raw deltas, no sign reversal)
    boot_out = {}
    csv_rows = []
    for first, second, note in COMPARISONS:
        common_idx = sorted(set(data[first]) & set(data[second]))
        for metric in CORE_METRICS:
            deltas = np.array([data[first][i][metric] - data[second][i][metric] for i in common_idx])
            stats = bootstrap(deltas)
            direction = ("higher-is-better" if metric in HIGHER_BETTER else "lower-is-better")
            key = f"{first}-minus-{second}/{metric}"
            boot_out[key] = {"note": note, "direction": direction, **stats}
            csv_rows.append({"comparison": f"{first} - {second}", "metric": metric,
                             "direction": direction, "delta_convention": "raw first-minus-second, no sign reversal",
                             **stats})
    (OUT / "paired_bootstrap_core7.json").write_text(json.dumps({
        "protocol": "core7-same-runner-strict276-v1",
        "sign_convention": "raw delta = first-named minus second; NO sign reversal; direction column states metric direction",
        "bootstrap": {"seed": BOOT_SEED, "resamples": BOOT_N, "unit": "object"},
        "shared_input_audit": audit,
        "comparisons": boot_out,
    }, indent=2) + "\n")
    with (OUT / "PAIRED_BOOTSTRAP_CORE7.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)

    print("wrote aggregate/rankings/bootstrap outputs to", OUT)


if __name__ == "__main__":
    main()
