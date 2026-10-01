#!/usr/bin/env python3
"""Phase 16 — per-object failure analysis for LLH vs GFL (agent B).

Loss set = 34 objects with negative LLH-GFL FG-PSNR delta in the same-runner
strict-276 confirmation. Characterizes: realization stability (does the same
object lose at R1?), schedule consistency (does it also lose under LHL/LFM?),
metric signature, and covariate profile vs wins.
"""
import csv, json, os

BASE = "/4T/CXY/MV-Painter/final/round2/coordination"
OUT = os.path.join(BASE, "forensic_audit_agentB_20261001")

def load(path, idcol, schedcol=None, schedval=None):
    with open(path) as f:
        rs = list(csv.DictReader(f))
    if schedcol:
        return {r[idcol]: r for r in rs if r[schedcol] == schedval}
    return {r[idcol]: r for r in rs}

raw = load(os.path.join(BASE, "final_acceptance_20260930/STRICT276_GLOBAL_FIXED_LOW_RAW.csv"), "object_id", "method", "layer_llh")
raw_gfl = load(os.path.join(BASE, "final_acceptance_20260930/STRICT276_GLOBAL_FIXED_LOW_RAW.csv"), "object_id", "method", "global_fixed_low")
raw_lhl = load(os.path.join(BASE, "final_acceptance_20260930/STRICT276_GLOBAL_FIXED_LOW_RAW.csv"), "object_id", "method", "layer_lhl")
raw_lfm = load(os.path.join(BASE, "final_acceptance_20260930/STRICT276_GLOBAL_FIXED_LOW_RAW.csv"), "object_id", "method", "layer_fixed_mean")
rb = os.path.join(BASE, "main_backbone_robustness1_20260930/per_object_metrics.csv")
r1_llh = load(rb, "object", "schedule", "layer_llh")
r1_gfl = load(rb, "object", "schedule", "global_fixed_low")
cov = load(os.path.join(BASE, "layer_confirmation_20260930/layer_llh_per_object_metrics.csv"), "object")

objs = sorted(set(raw) & set(raw_gfl), key=lambda o: int(o.split("_")[1]))
def d(a, b, o, col, sign=1):
    return sign * (float(a[o][col]) - float(b[o][col]))

losses = [o for o in objs if d(raw, raw_gfl, o, "fg_psnr") < 0]
wins = [o for o in objs if d(raw, raw_gfl, o, "fg_psnr") > 0]

def summarize(group):
    n = len(group)
    out = {"n": n}
    for name, vals in {
        "mean_loss_delta_fg_psnr": [d(raw, raw_gfl, o, "fg_psnr") for o in group],
        "mean_crop_area": [float(cov[o]["crop_area"]) for o in group if o in cov],
        "mean_gt_lap_var": [float(cov[o]["gt_fg_lap_var"]) for o in group if o in cov],
        "mean_gt_rgb_std": [float(cov[o]["gt_fg_rgb_std"]) for o in group if o in cov],
        "mean_gfl_baseline_fg_psnr": [float(raw_gfl[o]["fg_psnr"]) for o in group],
    }.items():
        out[name] = round(sum(vals) / len(vals), 4) if vals else None
    return out

rep = {"loss_profile": summarize(losses), "win_profile": summarize(wins)}

# realization stability: same object also loses at R1 (seed 10042)?
both = [o for o in losses if o in r1_llh and o in r1_gfl]
stable_loss = [o for o in both if d(r1_llh, r1_gfl, o, "fg_psnr") < 0]
rep["realization_stability"] = {
    "losses_checked": len(both),
    "also_loss_at_R1": len(stable_loss),
    "fraction": round(len(stable_loss) / len(both), 3) if both else None,
    "objects_also_loss_R1": stable_loss,
}
# win-set consistency at R1
both_w = [o for o in wins if o in r1_llh and o in r1_gfl]
still_win = [o for o in both_w if d(r1_llh, r1_gfl, o, "fg_psnr") > 0]
rep["realization_stability_wins"] = {"wins_checked": len(both_w), "also_win_at_R1": len(still_win)}

# schedule consistency: loss objects under LHL/LFM vs GFL
rep["schedule_consistency"] = {
    "also_loss_under_LHL": sum(1 for o in losses if d(raw_lhl, raw_gfl, o, "fg_psnr") < 0),
    "also_loss_under_LFM": sum(1 for o in losses if d(raw_lfm, raw_gfl, o, "fg_psnr") < 0),
    "losses_also_worse_than_LHL": sum(1 for o in losses if d(raw, raw_lhl, o, "fg_psnr") < 0),
    "losses_also_worse_than_LFM": sum(1 for o in losses if d(raw, raw_lfm, o, "fg_psnr") < 0),
}

# metric signature on losses: which co-metrics also lose?
sig = {}
for col, sign in (("full_psnr", 1), ("fg_ssim", 1), ("full_ssim", 1), ("edge_ssim", 1), ("fg_lpips", -1), ("full_lpips", -1)):
    vals = [d(raw, raw_gfl, o, col, sign) for o in losses]
    sig[col] = {"mean": round(sum(vals) / len(vals), 4),
                "also_lose": sum(1 for v in vals if v < 0), "n": len(vals)}
rep["metric_signature_on_losses"] = sig

# color-shift proxy on losses: pred/gt rgb_std ratio LLH vs GFL
# texture columns exist only in the robustness R1 per-object CSV (both methods, one realization)
def rgb_ratio(m, o):
    r = {"layer_llh": r1_llh, "global_fixed_low": r1_gfl}[m][o]
    return float(r["fg_rgb_std"]) / max(float(cov[o]["gt_fg_rgb_std"]), 1e-9)
rep["rgb_std_ratio_pred_over_gt"] = {
    "losses_LLH": round(sum(rgb_ratio("layer_llh", o) for o in losses) / len(losses), 4),
    "losses_GFL": round(sum(rgb_ratio("global_fixed_low", o) for o in losses) / len(losses), 4),
    "wins_LLH": round(sum(rgb_ratio("layer_llh", o) for o in wins) / len(wins), 4),
    "wins_GFL": round(sum(rgb_ratio("global_fixed_low", o) for o in wins) / len(wins), 4),
}

# texture-smoothing proxy: lap_var ratio
def lap_ratio(m, o):
    r = {"layer_llh": r1_llh, "global_fixed_low": r1_gfl}[m][o]
    return float(r["fg_lap_var"]) / max(float(cov[o]["gt_fg_lap_var"]), 1e-9)
rep["lap_var_ratio_pred_over_gt"] = {
    "losses_LLH": round(sum(lap_ratio("layer_llh", o) for o in losses) / len(losses), 4),
    "losses_GFL": round(sum(lap_ratio("global_fixed_low", o) for o in losses) / len(losses), 4),
    "wins_LLH": round(sum(lap_ratio("layer_llh", o) for o in wins) / len(wins), 4),
    "wins_GFL": round(sum(lap_ratio("global_fixed_low", o) for o in wins) / len(wins), 4),
}

rep["loss_objects_sorted"] = sorted(losses, key=lambda o: d(raw, raw_gfl, o, "fg_psnr"))
json.dump(rep, open(os.path.join(OUT, "phase16_failure_stats.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in rep.items() if k != "loss_objects_sorted"}, indent=1))
print("loss_objects:", rep["loss_objects_sorted"])
