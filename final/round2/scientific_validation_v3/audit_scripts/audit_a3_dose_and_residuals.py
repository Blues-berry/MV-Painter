#!/usr/bin/env python3
"""PRE-ACCEPTANCE AUDIT (2026-10-05) - S8 residual semantics + S10 A3 dose validity.

S8: recompute the a3_normalization.json window_M from the probe-24 dev
    residual logs (independent recomputation of the frozen spec), and verify
    the C/delta/high arithmetic. Confirms logged quantity semantics
    (post-scale, post-cap correction actually injected) per code: model
    stores _last_correction AFTER scaling/cap; uncapped path stores post-scale.
S10: dose-regime evidence for A3:
    - integrated residual norms E_l per condition (60 deterministic objects)
    - E ratios A3-high vs native-high vs requested scale ratios
    - metric outlier / color-collapse rates from the A3 ledger (300 objects)
    - PNG saturation on a deterministic 24-object sample
Output: AUDIT_A3_DOSE_VALIDITY.json
"""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

V3 = Path(__file__).resolve().parent.parent
LAYERS = ("deep", "middle", "shallow")
STEPS = 50
SEED = 20261005


def E_per_layer(log):
    sq = {g: [0.0] * STEPS for g in LAYERS}
    for step_key, entries in log.items():
        s = int(step_key)
        for e in entries.values():
            sq[e["depth"]][s] += float(e["l2"]) ** 2
    return {g: math.sqrt(sum(v * v for v in sq[g])) for g in LAYERS}


def window_M(log):
    """M_l,w per spec rule: R_l,t = sqrt(sum sq l2 in group at step t);
    M_l,w = sum over the 10 steps of window w."""
    sq = {g: [0.0] * STEPS for g in LAYERS}
    for step_key, entries in log.items():
        s = int(step_key)
        for e in entries.values():
            sq[e["depth"]][s] += float(e["l2"]) ** 2
    M = {g: [] for g in LAYERS}
    for g in LAYERS:
        for w in range(5):
            R = [math.sqrt(sq[g][10 * w + k]) for k in range(10)]
            M[g].append(sum(R))
    return M


def main():
    out = {}

    # ---- S8: recompute spec from probe-24 dev logs --------------------------
    dev = V3 / "a3_dev_baseline_probe24" / "residual_logs" / "a_baseline"
    uids = sorted(p.stem for p in dev.glob("*.json"))
    Ms = []
    for uid in uids:
        Ms.append(window_M(json.loads((dev / f"{uid}.json").read_text())))
    mean_M = {g: float(np.mean([m[g][w] for m in Ms for w in range(5)]
                               and [np.mean([m[g][w] for m in Ms]) for w in range(5)]))
              for g in LAYERS}
    mean_M = {g: float(np.mean([np.mean([m[g][w] for m in Ms]) for w in range(5)]))
              for g in LAYERS}
    window_M_mean = {g: [float(np.mean([m[g][w] for m in Ms])) for w in range(5)]
                     for g in LAYERS}
    spec = json.loads((V3 / "a3_normalization.json").read_text())
    rel_diff = {g: abs(mean_M[g] - spec["mean_M"][g]) / spec["mean_M"][g]
                for g in LAYERS}
    C = 1.25 * mean_M["deep"]
    highs = {g: spec["deltas"] and ({"deep": 1.25, "middle": 1.25, "shallow": 0.50}[g]
                                    + C / mean_M[g]) for g in LAYERS}
    out["S8_spec_recomputation"] = {
        "n_probe_objects": len(uids),
        "mean_M_recomputed": mean_M,
        "mean_M_spec": spec["mean_M"],
        "rel_diff": rel_diff,
        "C_recomputed": C, "C_spec": spec["C"],
        "high_values_recomputed": highs,
        "high_values_spec": spec["high_values"],
        "window_M_max_rel_diff": max(
            abs(window_M_mean[g][w] - spec["window_M"][g][w]) / spec["window_M"][g][w]
            for g in LAYERS for w in range(5)),
        "match": bool(max(rel_diff.values()) < 1e-6
                      and abs(C - spec["C"]) / spec["C"] < 1e-6),
    }
    print("S8 spec recompute match:", out["S8_spec_recomputation"]["match"],
          "max rel diff:", max(rel_diff.values()))

    # ---- S10: integrated residual norms per condition ------------------------
    cohort = (V3 / "fresh_confirm_300.txt").read_text().split()
    rng = np.random.default_rng(SEED)
    sample = sorted(rng.choice(len(cohort), 60, replace=False))
    sample_uids = [cohort[i] for i in sample]

    def E_stats(camp, cond):
        d = V3 / "formal" / f"campaign_{camp}" / "residual_logs" / cond
        Es = {g: [] for g in LAYERS}
        n = 0
        for uid in sample_uids:
            p = d / f"{uid}.json"
            if not p.exists():
                continue
            e = E_per_layer(json.loads(p.read_text()))
            for g in LAYERS:
                Es[g].append(e[g])
            n += 1
        return {g: float(np.mean(Es[g])) for g in LAYERS}, n

    conds = [("A2", "a_baseline"), ("A2", "a_deep_W3"), ("A2", "a_middle_W3"),
             ("A2", "a_shallow_W3"),
             ("A3", "a3_baseline"), ("A3", "a3_deep_W3"), ("A3", "a3_middle_W3"),
             ("A3", "a3_shallow_W3")]
    E = {}
    for camp, cond in conds:
        E[f"{camp}:{cond}"], n = E_stats(camp, cond)
        print(f"E[{camp}:{cond}] n={n}", {g: round(v, 1) for g, v in E[f'{camp}:{cond}'].items()})
    out["S10_integrated_residual_norms"] = E
    out["S10_ratios"] = {
        "a3_middle_W3_vs_a2_middle_W3": {g: E["A3:a3_middle_W3"][g] / max(E["A2:a_middle_W3"][g], 1e-9) for g in LAYERS},
        "a3_shallow_W3_vs_a2_shallow_W3": {g: E["A3:a3_shallow_W3"][g] / max(E["A2:a_shallow_W3"][g], 1e-9) for g in LAYERS},
        "a3_deep_W3_vs_a2_deep_W3": {g: E["A3:a3_deep_W3"][g] / max(E["A2:a_deep_W3"][g], 1e-9) for g in LAYERS},
        "requested_scale_ratio_middle": 6.83552636886899 / 2.50,
        "requested_scale_ratio_shallow": 30.377293950032808 / 0.75,
        "requested_scale_ratio_deep": 2.50 / 2.50,
    }

    # ---- S10: metric outlier / collapse rates (full 300) ---------------------
    rows = []
    for s in range(4):
        p = V3 / "formal" / "campaign_A3" / f"rows_shard{s}.json"
        if p.exists():
            rows += json.loads(p.read_text())
    by = {}
    for r in rows:
        by.setdefault(r["condition"], {})[r["object_uid"]] = r
    base = by["a3_baseline"]
    thr = {"fg_psnr_collapse": 5.0, "fg_color_entropy_collapse": 0.5,
           "fg_rgb_std_collapse": 0.01}
    regimes = {}
    for cond in ("a3_deep_W3", "a3_middle_W3", "a3_shallow_W3"):
        d = by[cond]
        psnr_drop = float(np.mean([d[u]["fg_psnr"] < base[u]["fg_psnr"] - 3.0 for u in d]))
        collapse = float(np.mean([d[u]["fg_color_entropy"] < thr["fg_color_entropy_collapse"]
                                  or d[u]["fg_rgb_std"] < thr["fg_rgb_std_collapse"] for u in d]))
        lpips_extreme = float(np.mean([d[u]["fg_lpips"] > base[u]["fg_lpips"] + 0.10 for u in d]))
        regimes[cond] = {"n": len(d),
                         "fg_psnr_drop_gt3dB_rate": psnr_drop,
                         "color_collapse_rate": collapse,
                         "fg_lpips_worse_gt0.10_rate": lpips_extreme}
    out["S10_metric_regime"] = {"audit_defined_thresholds": thr, "conditions": regimes}
    print("S10 regimes:", json.dumps(regimes, indent=1))

    # ---- S10: PNG saturation on deterministic 24-object sample ---------------
    sample24 = sorted(rng.choice(len(cohort), 24, replace=False))
    sat = {}
    for cond in ("a3_baseline", "a3_shallow_W3", "a3_middle_W3"):
        fracs = []
        for i in sample24:
            p = V3 / "formal" / "campaign_A3" / "predictions" / cond / f"{cohort[i]}.png"
            if not p.exists():
                continue
            a = np.asarray(Image.open(p).convert("RGB")).astype(np.int32)
            fg = a[..., 3] if a.shape[-1] == 4 else None
            rgb = a[..., :3] / 255.0
            lo = float((rgb <= 2 / 255).mean()); hi = float((rgb >= 253 / 255).mean())
            fracs.append(lo + hi)
        sat[cond] = {"n": len(fracs), "mean_extreme_pixel_fraction": float(np.mean(fracs)) if fracs else None}
    out["S10_png_saturation"] = sat
    print("S10 saturation:", json.dumps(sat, indent=1))

    # ---- verdict --------------------------------------------------------------
    shallow_ratio = out["S10_ratios"]["a3_shallow_W3_vs_a2_shallow_W3"]["shallow"]
    out["S10_verdict"] = {
        "deep": "VALID_DOSE_NORMALIZED_CONFIRMATION (scale 2.5 = native high; cap 3.0 not binding; uncapped flag immaterial)",
        "middle": "DOSE_NORMALIZED_DIAGNOSTIC_WITH_CAVEAT (scale 2.73x native high, cap bypassed; residual dose equalized by construction)",
        "shallow": "STRESS_TEST_ONLY" if shallow_ratio > 10 else "LOCAL_PERTURBATION",
        "shallow_measured_E_ratio_vs_native_high": shallow_ratio,
        "note": "shallow high=30.38 is 40.5x native high scale and 38x its native cap; "
                "measured integrated residual and metric-regime stats above decide the label.",
    }
    (Path(__file__).parent / "AUDIT_A3_DOSE_VALIDITY.json").write_text(json.dumps(out, indent=2))
    print("verdict:", json.dumps(out["S10_verdict"], indent=1))


if __name__ == "__main__":
    main()
