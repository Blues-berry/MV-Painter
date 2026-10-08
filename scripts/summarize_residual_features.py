#!/usr/bin/env python
"""Summarize per-step adapter-to-feature ratios on the frozen R1 set."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "1008/engineering/color_failure"
FREEZE = ARTIFACT / "SAMPLE_FREEZE.json"
METHODS = [
    ("no_adapter", "No Adapter"),
    ("native_gfl", "GFL"),
    ("native_gfh", "GFH"),
    ("native_gc3", "C3"),
    ("gen_linear", "Generic Linear"),
    ("layer_llh", "LLH"),
]
GROUPS = ["deep", "middle", "shallow"]
PHASES = [("early", 0, 16), ("middle", 17, 32), ("late", 33, 49)]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observer_root(sample: dict) -> Path:
    if sample["source"] == "existing_formal_fresh_c_gallery":
        return ARTIFACT / "runs/fresh_c_observer"
    return ARTIFACT / "runs/fig4_fig6_observer"


def main() -> None:
    freeze = json.loads(FREEZE.read_text())
    metric_rows = list(csv.DictReader((ARTIFACT / "OBJECT_FAILURE_TABLE.csv").open()))
    metrics = {(r["sample_id"], r["method"]): r for r in metric_rows}
    phase_rows = []
    aggregate_rows = []
    logs_used = []

    for sample in freeze["samples"]:
        sid, uid = sample["sample_id"], sample["uid"]
        for method_key, method_label in METHODS:
            path = observer_root(sample) / "residual_logs" / method_key / f"{uid}.json"
            if not path.is_file():
                raise FileNotFoundError(f"missing observer log: {path}")
            logs_used.append({"path": str(path), "sha256": sha256(path)})
            payload = json.loads(path.read_text())
            entries = []
            for step_s, layer_map in payload.items():
                step = int(step_s)
                for layer, data in layer_map.items():
                    entries.append({"step": step, "adapter_idx": layer, **data})

            per_group_phase = {}
            for depth in GROUPS:
                for phase, start, end in PHASES:
                    selected = [e for e in entries
                                if e["depth"] == depth and start <= e["step"] <= end]
                    if not selected:
                        raise RuntimeError(f"empty residual group: {sid}/{method_key}/{depth}/{phase}")
                    ratios = np.asarray([e["correction_to_feature_rms"] for e in selected], dtype=float)
                    anomalies = np.asarray([e["anomaly_fraction_gt_0p25_feature_rms"] for e in selected], dtype=float)
                    row = {
                        "sample_id": sid, "uid": uid, "source": sample["source"],
                        "method": method_label, "depth": depth, "phase": phase,
                        "step_start": start, "step_end": end, "n_layer_steps": len(selected),
                        "mean_feature_rms": float(np.mean([e["feature_rms"] for e in selected])),
                        "mean_residual_rms_over_feature_rms": float(np.mean(ratios)),
                        "p95_residual_rms_over_feature_rms": float(np.quantile(ratios, 0.95)),
                        "mean_anomaly_fraction_gt_0p25_feature_rms": float(np.mean(anomalies)),
                        "mean_requested_scale": float(np.mean([e["scale"] for e in selected])),
                        "mean_applied_scale": float(np.mean([e["eff_scale"] for e in selected])),
                    }
                    phase_rows.append(row)
                    per_group_phase[(depth, phase)] = row

            ratios = np.asarray([e["correction_to_feature_rms"] for e in entries], dtype=float)
            anomalies = np.asarray([e["anomaly_fraction_gt_0p25_feature_rms"] for e in entries], dtype=float)
            color = metrics[(sid, method_label)]
            aggregate_rows.append({
                "sample_id": sid, "uid": uid, "source": sample["source"],
                "method": method_label,
                "mean_residual_rms_over_feature_rms": float(np.mean(ratios)),
                "p95_residual_rms_over_feature_rms": float(np.quantile(ratios, 0.95)),
                "mean_anomaly_fraction_gt_0p25_feature_rms": float(np.mean(anomalies)),
                "mean_fg_ciede2000": float(color["mean_fg_ciede2000"]),
                "mean_delta_a_star": float(color["mean_delta_a_star"]),
                "mean_delta_b_star": float(color["mean_delta_b_star"]),
                "purple_cast_flag": color["purple_cast_flag"],
            })

    phase_path = ARTIFACT / "logs/OBJECT_RESIDUAL_FEATURE_PHASE_SUMMARY.csv"
    with phase_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=phase_rows[0].keys())
        writer.writeheader(); writer.writerows(phase_rows)
    aggregate_path = ARTIFACT / "logs/OBJECT_RESIDUAL_FEATURE_AGGREGATE.csv"
    with aggregate_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=aggregate_rows[0].keys())
        writer.writeheader(); writer.writerows(aggregate_rows)

    method_summary = {}
    for method_key, method_label in METHODS:
        subset = [r for r in aggregate_rows if r["method"] == method_label]
        method_summary[method_label] = {
            "n_objects": len(subset),
            "mean_residual_rms_over_feature_rms": float(np.mean([r["mean_residual_rms_over_feature_rms"] for r in subset])),
            "mean_anomaly_fraction": float(np.mean([r["mean_anomaly_fraction_gt_0p25_feature_rms"] for r in subset])),
            "mean_fg_ciede2000": float(np.mean([r["mean_fg_ciede2000"] for r in subset])),
            "purple_flag_count": int(sum(r["purple_cast_flag"] == "True" for r in subset)),
        }

    adapted = [r for r in aggregate_rows if r["method"] != "No Adapter"]
    association = spearmanr(
        [r["mean_residual_rms_over_feature_rms"] for r in adapted],
        [r["mean_fg_ciede2000"] for r in adapted],
    )
    # One threshold per depth group, calibrated only from GFL residual ratios;
    # no color or visual endpoint is used to choose it.
    taus = {}
    for depth in GROUPS:
        vals = []
        for sample in freeze["samples"]:
            path = observer_root(sample) / "residual_logs/native_gfl" / f"{sample['uid']}.json"
            payload = json.loads(path.read_text())
            for step_s, layer_map in payload.items():
                for data in layer_map.values():
                    if data["depth"] == depth:
                        vals.append(float(data["correction_to_feature_rms"]))
        taus[depth] = float(np.quantile(np.asarray(vals), 0.95))

    gate_lock = {
        "locked_from_baseline_before_proposed_generation": True,
        "rule": "per-depth tau = 95th percentile of GFL actual correction RMS / pre-adapter feature RMS across all frozen objects and 50 steps",
        "target_metrics_used_for_calibration": False,
        "tau_by_depth": taus,
        "sample_freeze_sha256": sha256(FREEZE),
        "observer_logs": logs_used,
    }
    (ARTIFACT / "logs/FEATURE_RATIO_GATE_LOCK.json").write_text(json.dumps(gate_lock, indent=2) + "\n")
    (ARTIFACT / "logs/RESIDUAL_COLOR_ASSOCIATION.json").write_text(json.dumps({
        "purpose": "descriptive diagnostic association; selected objects and repeated methods are not independent",
        "spearman_residual_ratio_vs_ciede2000": {
            "rho": float(association.statistic), "p_value_descriptive_only": float(association.pvalue),
            "n_object_method_rows": len(adapted),
        },
        "mean_by_method": method_summary,
        "phase_summary_csv": str(phase_path),
        "aggregate_summary_csv": str(aggregate_path),
        "gate_lock": str(ARTIFACT / "logs/FEATURE_RATIO_GATE_LOCK.json"),
    }, indent=2) + "\n")
    print(f"wrote {len(phase_rows)} phase rows, {len(aggregate_rows)} object-method rows; tau={taus}")


if __name__ == "__main__":
    main()
