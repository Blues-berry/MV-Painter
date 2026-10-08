#!/usr/bin/env python
"""Summarize paired Stage 2 endpoints and gate activation from saved artifacts."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "1008/engineering/color_failure"
METRICS = [
    ("mean_fg_ciede2000", "lower"), ("fg_lpips", "lower"),
    ("fg_psnr", "higher"), ("edge_ssim", "higher"),
]
PAIRS = [
    ("C3 + Feature Gate", "C3", "c3_feature_gate"),
    ("Linear + Feature Gate", "Generic Linear", "linear_feature_gate"),
]


def load_table() -> list[dict]:
    return list(csv.DictReader((ARTIFACT / "OBJECT_FAILURE_TABLE.csv").open()))


def paired_summary(rows: list[dict], proposed: str, baseline: str, cohort: str) -> dict:
    subset = [r for r in rows if cohort == "all" or r["source"] == cohort]
    proposed_rows = {r["sample_id"]: r for r in subset if r["method"] == proposed}
    baseline_rows = {r["sample_id"]: r for r in subset if r["method"] == baseline}
    keys = sorted(set(proposed_rows) & set(baseline_rows))
    result = {"n_objects": len(keys)}
    for metric, direction in METRICS:
        differences = [float(proposed_rows[k][metric]) - float(baseline_rows[k][metric]) for k in keys]
        improved = [d < 0 if direction == "lower" else d > 0 for d in differences]
        result[metric] = {
            "mean_proposed": float(np.mean([float(proposed_rows[k][metric]) for k in keys])),
            "mean_baseline": float(np.mean([float(baseline_rows[k][metric]) for k in keys])),
            "mean_paired_delta": float(np.mean(differences)),
            "objects_improved": int(sum(improved)),
            "objects_worsened": int(len(improved) - sum(improved)),
        }
    result["purple_flag_count_proposed"] = int(sum(proposed_rows[k]["purple_cast_flag"] == "True" for k in keys))
    result["purple_flag_count_baseline"] = int(sum(baseline_rows[k]["purple_cast_flag"] == "True" for k in keys))
    return result


def gate_summary(method: str) -> dict:
    root = ARTIFACT / "runs/feature_ratio_gate/residual_logs" / method
    by_depth = defaultdict(list)
    total = 0
    attenuated = 0
    for path in sorted(root.glob("*.json")):
        payload = json.loads(path.read_text())
        for layers in payload.values():
            for entry in layers.values():
                by_depth[entry["depth"]].append(entry)
                total += 1
                attenuated += entry["gate"] < 0.999999
    return {
        "layer_step_calls": total,
        "attenuated_calls": attenuated,
        "attenuated_fraction": float(attenuated / max(total, 1)),
        "by_depth": {
            depth: {
                "mean_gate": float(np.mean([r["gate"] for r in entries])),
                "attenuated_fraction": float(np.mean([r["gate"] < 0.999999 for r in entries])),
                "mean_pre_gate_ratio": float(np.mean([r["pre_gate_ratio"] for r in entries])),
                "mean_post_gate_ratio": float(np.mean([r["post_gate_ratio"] for r in entries])),
                "p95_post_gate_ratio": float(np.quantile([r["post_gate_ratio"] for r in entries], 0.95)),
            }
            for depth, entries in by_depth.items()
        },
    }


def main() -> None:
    rows = load_table()
    cohorts = {
        "all": "all",
        "historical_six": "01549_fig4_fig6_original_object",
        "fresh_c_twenty": "existing_formal_fresh_c_gallery",
    }
    comparisons = {}
    for proposed, baseline, key in PAIRS:
        comparisons[key] = {
            cohort_name: paired_summary(rows, proposed, baseline, source)
            for cohort_name, source in cohorts.items()
        }
        comparisons[key]["vs_gfl_all"] = paired_summary(rows, proposed, "GFL", "all")

    run_manifest_path = ARTIFACT / "runs/feature_ratio_gate/run_manifest.json"
    run_manifest = json.loads(run_manifest_path.read_text())
    output = {
        "status": "descriptive development evaluation; no independent confirmation",
        "run_manifest": str(run_manifest_path),
        "gate_enabled": run_manifest["gate_enabled"],
        "tau_by_depth": run_manifest["tau_by_depth"],
        "paired_comparisons": comparisons,
        "gate_activation": {method: gate_summary(method) for _, _, method in PAIRS},
        "decision_rule": json.loads((ARTIFACT / "logs/STAGE2_GATE_RUN_LOCK.json").read_text())["decision_rule"],
    }
    path = ARTIFACT / "logs/STAGE2_GATE_RESULTS.json"
    path.write_text(json.dumps(output, indent=2) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
