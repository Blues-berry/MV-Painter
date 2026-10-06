#!/usr/bin/env python3
"""Summarize A3b probe-only post-scale residual logs; never reads image metrics."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

V3 = Path(__file__).resolve().parent.parent
ROOT = V3.parents[2]
DEV = V3 / "a3b_development_residual_only"
BASE = V3 / "a3_dev_baseline_probe24/residual_logs/a_baseline"
RUN = DEV / "candidate_highs_run_pinned"
HIGH_DIR = RUN / "residual_logs"
SPEC = json.loads((DEV / "A3B_CANDIDATE_HIGHS.json").read_text())
LAUNCH = json.loads((RUN / "LAUNCH_RECORD.json").read_text())
LAYERS = ("deep", "middle", "shallow")
WINDOWS = range(1, 6)


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def layer_norm(step: dict, layer: str) -> float:
    vals = [float(v["l2"]) for v in step.values() if v.get("depth") == layer]
    if not vals:
        raise RuntimeError(f"no {layer} residual entries at step")
    return math.sqrt(sum(v * v for v in vals))


def main() -> None:
    objects = sorted(p.stem for p in BASE.glob("*.json"))
    assert len(objects) == 24
    conditions = [f"a3_{layer}_W{w}" for layer in LAYERS for w in WINDOWS]
    object_list = ROOT / "final/round2/clean_dataset_v2/probe_objects_24_clean_v2.txt"
    spec_path = DEV / "A3B_CANDIDATE_HIGHS.json"
    expected_object_hash = hashlib.sha256(object_list.read_bytes()).hexdigest()
    expected_spec_hash = hashlib.sha256(spec_path.read_bytes()).hexdigest()
    assert LAUNCH["conditions"] == conditions
    assert len(object_list.read_text().splitlines()) == 24
    assert LAUNCH["runner_sha256"] == hashlib.sha256(
        (V3 / "audit_scripts/frozen_a3b_residual_runner.py").read_bytes()).hexdigest()
    for shard in (0, 1):
        manifest = json.loads((RUN / f"run_manifest_shard{shard}.json").read_text())
        assert manifest["status"] == "complete"
        assert manifest["shard"] == shard and manifest["num_shards"] == 2
        assert manifest["runner_script_sha256"] == LAUNCH["runner_sha256"]
        assert manifest["object_list_sha256"] == expected_object_hash
        assert manifest["a3_spec_sha256"] == expected_spec_hash
        assert manifest["checkpoint_sha256"] == LAUNCH["checkpoint_sha256"]
        assert manifest["conditions"] == conditions
        assert manifest["residuals_only"] is True and manifest["row_count"] == 0
    assert not any((RUN / "predictions").rglob("*.png"))
    assert not list(RUN.glob("*per_object_metrics*.csv"))

    rows = []
    for layer in LAYERS:
        low = float(SPEC["baseline_scales"][layer])
        high = float(SPEC["high_values"][layer])
        delta = high - low
        for w in WINDOWS:
            cond = f"a3_{layer}_W{w}"
            for obj in objects:
                base_log = load(BASE / f"{obj}.json")
                high_path = HIGH_DIR / cond / f"{obj}.json"
                if not high_path.is_file():
                    continue
                hi_log = load(high_path)
                inc, net = 0.0, 0.0
                lo_step, hi_step = 10 * (w - 1), 10 * w
                for k in range(lo_step, hi_step):
                    hs = hi_log[str(k)]
                    bs = base_log[str(k)]
                    layer_entries = [v for v in hs.values() if v.get("depth") == layer]
                    scales = {round(float(v["eff_scale"]), 12) for v in layer_entries}
                    if scales != {round(high, 12)}:
                        raise RuntimeError(f"effective scale mismatch in {cond}/{obj}/{k}: {scales}")
                    high_norm = layer_norm(hs, layer)
                    base_norm = layer_norm(bs, layer)
                    raw_norm = high_norm / high
                    inc += delta * raw_norm
                    net += high_norm - base_norm
                # The active pulse is the sole scale change in the condition.
                for k in range(50):
                    step = hi_log[str(k)]
                    for entry in step.values():
                        expected = (high if entry["depth"] == layer and lo_step <= k < hi_step
                                    else low if entry["depth"] == layer
                                    else float(SPEC["baseline_scales"][entry["depth"]]))
                        if not math.isclose(float(entry["eff_scale"]), expected,
                                            rel_tol=0.0, abs_tol=1e-10):
                            raise RuntimeError(f"off-protocol effective scale in {cond}/{obj}/{k}")
                rows.append({
                    "object": obj, "layer": layer, "window": f"W{w}",
                    "baseline_scale": low, "high_scale": high,
                    "requested_delta": delta, "effective_delta": delta,
                    "integrated_multiplier_increment": inc,
                    "net_postscale_norm_change_vs_baseline": net,
                    "target_increment": float(SPEC["max_common_increment_target"]),
                })

    expected = 24 * 3 * 5
    assert len(rows) == expected, f"expected {expected} object-window records, got {len(rows)}"
    by_cell = defaultdict(list)
    by_layer = defaultdict(list)
    for row in rows:
        by_cell[(row["layer"], row["window"])].append(row)
        by_layer[row["layer"]].append(row)
    cell_means = {f"{l}_{w}": sum(r["integrated_multiplier_increment"] for r in rs) / len(rs)
                  for (l, w), rs in by_cell.items()}
    target = float(SPEC["max_common_increment_target"])
    layer_means = {l: sum(r["integrated_multiplier_increment"] for r in rs) / len(rs)
                   for l, rs in by_layer.items()}
    rel_error = {l: layer_means[l] / target - 1.0 for l in LAYERS}
    balanced = all(abs(v) <= 0.20 for v in rel_error.values())
    cell_net = {f"{l}_{w}": sum(r["net_postscale_norm_change_vs_baseline"] for r in rs) / len(rs)
                for (l, w), rs in by_cell.items()}
    summary = {
        "development_objects": len(objects),
        "object_layer_window_records": len(rows),
        "pinned_runner_sha256": LAUNCH["runner_sha256"],
        "development_object_list_sha256": expected_object_hash,
        "candidate_spec_sha256": expected_spec_hash,
        "candidate_highs": SPEC["high_values"],
        "frozen_target": target,
        "mean_increment_by_layer_window": cell_means,
        "mean_increment_by_layer_over_all_windows": layer_means,
        "relative_error_by_layer": rel_error,
        "net_postscale_norm_change_by_layer_window": cell_net,
        "within_plus_minus_20_percent_target": balanced,
        "interpretation": "approximately layer-balanced" if balanced else
            "not approximately layer-balanced; retain frozen highs and describe A3b as bounded-dose map",
        "image_metrics_read": False,
    }
    out = DEV / "A3B_DEV_RESIDUAL_CALIBRATION.json"
    out.write_text(json.dumps(summary, indent=2) + "\n")
    with (DEV / "A3B_DEV_REALIZED_DOSE.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
