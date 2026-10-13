#!/usr/bin/env python3
"""Experiment B3 — residual-budget and cap-activation decomposition.

For every condition in a campaign, reads the per-object residual logs and
computes (paired at object level):
  * integrated requested/effective scale per layer
  * integrated residual energy E_l = sum_t R_l,t  (R_l,t = sqrt(sum of squared
    per-wrapper l2 norms in group l at step t))
  * cap activation frequency: fraction of (step, object) cells per layer where
    eff_scale < requested - 1e-9 (uncapped conditions report 0 by construction)
  * paired deltas of log E_l vs a reference condition (bootstrap CI)

Output: <run_dir>/residual_budget_audit.json
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np

LAYERS = ("deep", "middle", "shallow")
STEPS = 50


def cond_budget(run_dir: Path, condition: str, uids: list[str]) -> dict:
    logs_dir = run_dir / "residual_logs" / condition
    per_layer_E = {g: [] for g in LAYERS}
    req_sums = {g: 0.0 for g in LAYERS}
    eff_sums = {g: 0.0 for g in LAYERS}
    scale_cells = {g: 0 for g in LAYERS}
    cap_hits = {g: 0 for g in LAYERS}
    manifest = json.loads((run_dir / "run_manifest_shard0.json").read_text())
    if condition not in manifest.get("condition_specs", {}):
        raise KeyError(f"{condition} missing from run manifest: {run_dir}")
    uncapped = bool(manifest["condition_specs"][condition].get("uncapped", False))
    n_used = 0
    for uid in uids:
        p = logs_dir / f"{uid}.json"
        if not p.exists():
            continue
        log = json.loads(p.read_text())
        sq = {g: [0.0] * STEPS for g in LAYERS}
        for step_key, entries in log.items():
            s = int(step_key)
            for e in entries.values():
                g = e["depth"]
                sq[g][s] += float(e["l2"]) ** 2
                requested = float(e["scale"])
                logged_eff = float(e["eff_scale"])
                actual_eff = requested if uncapped else logged_eff
                req_sums[g] += requested
                eff_sums[g] += actual_eff
                scale_cells[g] += 1
                # explore_contradiction logs eff_scale=min(requested, cap)
                # even when the campaign swaps in its uncapped forward. In
                # that mode the field is hypothetical; the manifest is the
                # authority for whether the cap was applied.
                if not uncapped and logged_eff < requested - 1e-9:
                    cap_hits[g] += 1
        n_used += 1
        for g in LAYERS:
            per_layer_E[g].append(math.sqrt(sum(v * v for v in sq[g])))
    out = {
        "condition": condition,
        "n_objects": n_used,
        "uncapped": uncapped,
        "effective_scale_source": (
            "requested scale (cap bypassed); logged eff_scale is hypothetical"
            if uncapped else "logged eff_scale (post-cap)"
        ),
        "layers": {},
    }
    for g in LAYERS:
        v = np.array(per_layer_E[g])
        out["layers"][g] = {
            "E_mean": float(v.mean()) if len(v) else None,
            "E_median": float(np.median(v)) if len(v) else None,
            "E_log_mean": float(np.log(v).mean()) if len(v) else None,
            "requested_scale_mean": (
                req_sums[g] / scale_cells[g] if scale_cells[g] else None
            ),
            "effective_scale_mean": (
                eff_sums[g] / scale_cells[g] if scale_cells[g] else None
            ),
            "cap_activation_rate": (
                0.0 if uncapped else
                (cap_hits[g] / scale_cells[g]) if scale_cells[g] else 0.0
            ),
        }
    return out


def paired_log_delta(run_dir: Path, a: str, b: str, uids: list[str]) -> dict:
    la, lb = run_dir / "residual_logs" / a, run_dir / "residual_logs" / b
    deltas = {g: [] for g in LAYERS}
    common = []
    for uid in uids:
        pa, pb = la / f"{uid}.json", lb / f"{uid}.json"
        if not (pa.exists() and pb.exists()):
            continue
        common.append(uid)
        for g in LAYERS:
            ea = _energy(pa, g)
            eb = _energy(pb, g)
            if ea <= 0 or eb <= 0:
                continue  # zero residuals (e.g., adapter bypassed): ratio undefined
            deltas[g].append(math.log(ea / eb))
    out = {"a": a, "b": b, "n": len(common), "log_E_ratio": {},
           "note": "objects with zero residual energy in either condition are excluded from ratios"}
    rng = np.random.default_rng(20261002)
    for g in LAYERS:
        d = np.array(deltas[g]) if deltas[g] else np.array([0.0])
        if len(deltas[g]) == 0:
            out["log_E_ratio"][g] = {"mean": None, "ci95": None, "win_rate": None,
                                     "note": "no comparable objects (zero-energy condition)"}
            continue
        idx = rng.integers(0, len(d), size=(10000, len(d)))
        boots = d[idx].mean(axis=1)
        lo, hi = np.percentile(boots, [2.5, 97.5])
        out["log_E_ratio"][g] = {
            "mean": float(d.mean()), "ci95": [float(lo), float(hi)],
            "win_rate": float((d > 0).mean()),
        }
    return out


def _energy(log_path: Path, group: str) -> float:
    log = json.loads(log_path.read_text())
    sq = [0.0] * STEPS
    for step_key, entries in log.items():
        s = int(step_key)
        for e in entries.values():
            if e["depth"] == group:
                sq[s] += float(e["l2"]) ** 2
    return math.sqrt(sum(v * v for v in sq))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--conditions", required=True)
    ap.add_argument("--object-list", required=True)
    ap.add_argument("--reference", default=None,
                    help="condition for paired log-E ratio deltas (optional)")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    uids = [l.strip() for l in Path(args.object_list).open() if l.strip()]
    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]

    result = {"run_dir": str(run_dir), "conditions": {}}
    for c in conditions:
        result["conditions"][c] = cond_budget(run_dir, c, uids)
        print(c, json.dumps(result["conditions"][c]["layers"], default=float)[:220], flush=True)
    if args.reference:
        ref = args.reference
        result["paired_log_E_ratio"] = {}
        for c in conditions:
            if c == ref:
                continue
            result["paired_log_E_ratio"][c] = paired_log_delta(run_dir, c, ref, uids)
            print(f"ratio {c}/{ref}:", json.dumps(result["paired_log_E_ratio"][c]["log_E_ratio"], default=float)[:220], flush=True)

    out = run_dir / "residual_budget_audit.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
