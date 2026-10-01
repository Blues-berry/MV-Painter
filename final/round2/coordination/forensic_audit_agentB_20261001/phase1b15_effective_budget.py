#!/usr/bin/env python3
"""Phase 1B+15 — LLH effective-control & residual-budget confound (agent B).

1) Requested-vs-effective scale table (analytical, from code + formal manifest).
2) Independent verification of the gradient-energy mechanism ratios
   (no_adapter 0.89x / GFL 1.54x / LLH 1.13x GT) from per-object CSVs.
3) LLH vs layer_fixed_mean (constant control) deltas from same-runner RAW.
"""
import csv, json, os

BASE = "/4T/CXY/MV-Painter/final/round2/coordination"
OUT = os.path.join(BASE, "forensic_audit_agentB_20261001")

def load(path):
    with open(path) as f:
        return list(csv.DictReader(f))

# ---------- 1) effective-scale table (17/16/17 partition, 50 steps) ----------
def stage(p, e, m, l):
    return e if p < 1/3 else (m if p < 2/3 else l)

# progress = step/49 → early steps 0..16 (17), middle 17..32 (16), late 33..49 (17)
PART = [(17, 1/3), (16, 2/3), (17, 1.01)]  # counts per band
CAPS = {"deep": 3.0, "middle": 3.5, "shallow": 0.8}

def time_mean(vals):
    n = sum(c for c, _ in PART)
    return sum(c * v for (c, _), v in zip(PART, vals)) / n

SCHEDS = {
    "no_adapter":      {"deep": [0]*3, "middle": [0]*3, "shallow": [0]*3},
    "global_fixed_low":    {"deep": [1.25]*3, "middle": [1.25]*3, "shallow": [1.25]*3},
    "global_fixed_high":   {"deep": [2.50]*3, "middle": [2.50]*3, "shallow": [2.50]*3},
    "global_fixed_mean":   {"deep": [5/3]*3, "middle": [5/3]*3, "shallow": [5/3]*3},
    "global_c3":       {"deep": [1.25, 2.50, 1.25], "middle": [1.25, 2.50, 1.25], "shallow": [1.25, 2.50, 1.25]},
    "layer_llh":       {"deep": [1.25, 1.25, 2.50], "middle": [1.25, 1.25, 2.50], "shallow": [0.50, 0.50, 0.75]},
    "layer_lhl":       {"deep": [1.25, 2.50, 1.25], "middle": [1.25, 2.50, 1.25], "shallow": [0.50, 0.75, 0.50]},
    "layer_fixed_mean":{"deep": [1.65]*3, "middle": [1.65]*3, "shallow": [0.58]*3},
}
table = {}
for name, g in SCHEDS.items():
    row = {}
    for grp, vals in g.items():
        req_mean = time_mean(vals)
        eff_vals = [min(v, CAPS[grp]) for v in vals]
        eff_mean = time_mean(eff_vals)
        row[grp] = {"requested_mean": round(req_mean, 4), "effective_mean": round(eff_mean, 4),
                    "capped": any(v > CAPS[grp] for v in vals),
                    "eff_per_stage": [round(v, 3) for v in eff_vals]}
    row["total_effective"] = round(sum(row[g]["effective_mean"] for g in ("deep", "middle", "shallow")), 4)
    table[name] = row

# ---------- 2) gradient-energy mechanism ratios ----------
def ratio(path, pred_col="fg_grad_mag", gt_col="gt_fg_grad_mag"):
    rs = load(path)
    ps = [float(r[pred_col]) for r in rs]
    gs = [float(r[gt_col]) for r in rs]
    return round(sum(ps) / sum(gs), 4), len(rs)

ratios = {}
c7 = os.path.join(BASE, "core7_same_runner_completion_20261001")
ratios["no_adapter(core7)"] = ratio(os.path.join(c7, "formal_no_adapter", "per_object_metrics.csv"))
ratios["global_fixed_high(core7)"] = ratio(os.path.join(c7, "formal_global_fixed_high", "per_object_metrics.csv"))
for m in ("layer_llh", "layer_lhl", "layer_fixed_mean"):
    ratios[f"{m}(confirmation)"] = ratio(os.path.join(BASE, "layer_confirmation_20260930", f"{m}_per_object_metrics.csv"))
ratios["global_fixed_low(robustness1-R1)"] = None
rs = load(os.path.join(BASE, "main_backbone_robustness1_20260930", "per_object_metrics.csv"))
gfl = [r for r in rs if r["schedule"] == "global_fixed_low"]
ps = sum(float(r["fg_grad_mag"]) for r in gfl)
gs = sum(float(r["gt_fg_grad_mag"]) for r in gfl)
ratios["global_fixed_low(robustness1-R1)"] = (round(ps / gs, 4), len(gfl))
# note: GFL rows in the same-runner confirmation RAW carry only headline metrics;
# gradient ratio for GFL is taken from the R1 realization copy (realization mean-neutral).

# ---------- 3) LLH vs layer_fixed_mean (constant control) ----------
raw = load(os.path.join(BASE, "final_acceptance_20260930/STRICT276_GLOBAL_FIXED_LOW_RAW.csv"))
by = {}
for r in raw:
    by.setdefault(r["method"], {})[r["object_id"]] = r
llh = by["layer_llh"]
lfm = by["layer_fixed_mean"]
objs = sorted(set(llh) & set(lfm))
def d(m, col, sign=1):
    return [sign * (float(llh[o][col]) - float(lfm[o][col])) for o in objs]
def mean(v): return sum(v) / len(v)
def pct(v, q):
    s = sorted(v); i = q * (len(s) - 1)
    lo, hi = int(i), min(int(i) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (i - lo)
lfm_report = {}
for col, sign in (("fg_psnr", 1), ("full_psnr", 1), ("fg_lpips", -1), ("fg_ssim", 1)):
    v = d("x", col, sign)
    lfm_report[col] = {"mean": round(mean(v), 4), "median": round(pct(v, .5), 4),
                       "wins": sum(1 for x in v if x > 0), "losses": sum(1 for x in v if x < 0)}

# ---------- 4) budget-response anchor + LLH vs LHL ----------
def pair_delta(a, b, col, sign=1):
    aa, bb = by[a], by[b]
    oo = sorted(set(aa) & set(bb))
    v = [sign * (float(aa[o][col]) - float(bb[o][col])) for o in oo]
    return {"mean": round(mean(v), 4), "median": round(pct(v, .5), 4),
            "wins": sum(1 for x in v if x > 0), "losses": sum(1 for x in v if x < 0)}
anchors = {
    "GFM_minus_GFL_fg_psnr (budget +33% deep/mid anchor)": pair_delta("global_fixed_low", "layer_fixed_mean", "fg_psnr"),
    "GFM_minus_GFL_full_psnr": pair_delta("global_fixed_low", "layer_fixed_mean", "full_psnr"),
    "LLH_minus_LHL_fg_psnr (temporal pair, LLH +1.5% deep budget)": pair_delta("layer_lhl", "layer_llh", "fg_psnr"),
    "LLH_minus_LHL_full_psnr": pair_delta("layer_lhl", "layer_llh", "full_psnr"),
    "LLH_minus_LHL_fg_lpips": pair_delta("layer_lhl", "layer_llh", "fg_lpips", -1),
    "LLH_minus_LHL_full_ssim": pair_delta("layer_lhl", "layer_llh", "full_ssim"),
    "LLH_minus_LHL_edge_ssim": pair_delta("layer_lhl", "layer_llh", "edge_ssim"),
    "LLH_minus_GFL_fg_psnr (reference)": pair_delta("global_fixed_low", "layer_llh", "fg_psnr"),
}

out = {"effective_scale_table": table, "gradient_energy_ratio_pred_over_gt": ratios,
       "llh_minus_layer_fixed_mean": lfm_report, "anchors": anchors}
with open(os.path.join(OUT, "phase1b15_effective_budget_stats.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
