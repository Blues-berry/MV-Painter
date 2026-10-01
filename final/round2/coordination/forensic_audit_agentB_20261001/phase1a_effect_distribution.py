#!/usr/bin/env python3
"""Phase 1A — MAIN_EFFECT_DISTRIBUTION_AUDIT (agent B, 20261001).

Independent recomputation of the LLH-vs-GFL large-effect distribution on the
strict-276 same-runner confirmation. Read-only on paper artifacts; outputs
land in forensic_audit_agentB_20261001/.
"""
import csv, json, math, os
from collections import OrderedDict

BASE = "/4T/CXY/MV-Painter/final/round2/coordination"
RAW = os.path.join(BASE, "final_acceptance_20260930/STRICT276_GLOBAL_FIXED_LOW_RAW.csv")
LLH_EXTRA = os.path.join(BASE, "layer_confirmation_20260930/layer_llh_per_object_metrics.csv")
OUTDIR = os.path.join(BASE, "forensic_audit_agentB_20261001")

def rows(path):
    with open(path) as f:
        return list(csv.DictReader(f))

raw = rows(RAW)
by = {}
for r in raw:
    by.setdefault(r["method"], {})[r["object_id"]] = r

llh, gfl = by["layer_llh"], by["global_fixed_low"]
objs = sorted(set(llh) & set(gfl), key=lambda o: int(o.split("_")[1]))
assert len(objs) == 276, len(objs)

# extra covariates (same runner, LLH rows) for correlation checks
cov = {}
for r in rows(LLH_EXTRA):
    cov[r["object"]] = r

def f(r, k):
    return float(r[k])

deltas = OrderedDict()
for o in objs:
    d = OrderedDict()
    d["fg_psnr"] = f(llh[o], "fg_psnr") - f(gfl[o], "fg_psnr")          # higher better
    d["full_psnr"] = f(llh[o], "full_psnr") - f(gfl[o], "full_psnr")
    d["fg_lpips"] = f(gfl[o], "fg_lpips") - f(llh[o], "fg_lpips")        # benefit-oriented
    d["full_lpips"] = f(gfl[o], "full_lpips") - f(llh[o], "full_lpips")
    d["fg_ssim"] = f(llh[o], "fg_ssim") - f(gfl[o], "fg_ssim")
    d["full_ssim"] = f(llh[o], "full_ssim") - f(gfl[o], "full_ssim")
    d["edge_ssim"] = f(llh[o], "edge_ssim") - f(gfl[o], "edge_ssim")
    deltas[o] = d

def pct(v, q):
    s = sorted(v)
    idx = q * (len(s) - 1)
    lo, hi = math.floor(idx), math.ceil(idx)
    if lo == hi:
        return s[lo]
    return s[lo] + (s[hi] - s[lo]) * (idx - lo)

def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return float("nan")
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / math.sqrt(sxx * syy)

def spearman(x, y):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[s[k]] = avg
            i = j + 1
        return r
    return pearson(rank(x), rank(y))

report = {}
dp = [deltas[o]["fg_psnr"] for o in objs]
report["fg_psnr_delta"] = {
    "mean": sum(dp) / len(dp),
    "median": pct(dp, 0.5),
    "p10": pct(dp, 0.10), "p25": pct(dp, 0.25), "p75": pct(dp, 0.75), "p90": pct(dp, 0.90),
    "min": min(dp), "max": max(dp),
    "wins": sum(1 for v in dp if v > 0), "losses": sum(1 for v in dp if v < 0),
    "ties": sum(1 for v in dp if v == 0),
    "stdev": math.sqrt(sum((v - sum(dp) / len(dp)) ** 2 for v in dp) / (len(dp) - 1)),
}

# concentration: how much of total positive mass comes from the top-k objects?
sp = sorted(dp, reverse=True)
total_pos = sum(v for v in dp if v > 0)
conc = {}
cum = 0.0
for k in (5, 10, 20, 28):
    cum = sum(sp[:k])
    conc[f"top{k}_share_of_positive_mass"] = cum / total_pos if total_pos > 0 else None
conc["mean_excl_top10"] = (sum(dp) - sum(sp[:10])) / (len(dp) - 10)
conc["mean_excl_top_bottom_5pct"] = sum(sp[14:-14]) / (len(sp) - 28)  # 276*0.05≈14
report["concentration"] = conc

# correlation of delta with baseline quality and covariates
base_fp = [f(gfl[o], "fg_psnr") for o in objs]
base_fl_gfl = [f(gfl[o], "fg_lpips") for o in objs]
areas, gt_lap, gt_rgbstd, gt_grad = [], [], [], []
missing_cov = []
for o in objs:
    c = cov.get(o)
    if c is None:
        missing_cov.append(o); areas.append(None); gt_lap.append(None); gt_rgbstd.append(None); gt_grad.append(None)
    else:
        areas.append(f(c, "crop_area")); gt_lap.append(f(c, "gt_fg_lap_var"))
        gt_rgbstd.append(f(c, "gt_fg_rgb_std")); gt_grad.append(f(c, "gt_fg_grad_mag"))
pairs = {
    "delta_vs_gfl_baseline_fg_psnr": (dp, base_fp),
    "delta_vs_gfl_baseline_fg_lpips": (dp, base_fl_gfl),
}
if not missing_cov:
    pairs["delta_vs_crop_area(fg coverage)"] = (dp, areas)
    pairs["delta_vs_gt_fg_lap_var"] = (dp, gt_lap)
    pairs["delta_vs_gt_fg_rgb_std"] = (dp, gt_rgbstd)
    pairs["delta_vs_gt_fg_grad_mag"] = (dp, gt_grad)
report["correlations"] = {k: {"pearson": pearson(x, y), "spearman": spearman(x, y)} for k, (x, y) in pairs.items()}
report["cov_missing_objects"] = missing_cov

# wins by baseline-quality quartile
qs = [pct(base_fp, q) for q in (0.25, 0.5, 0.75)]
bands = {"Q1(worst baseline)": [], "Q2": [], "Q3": [], "Q4(best baseline)": []}
for o, b in zip(objs, base_fp):
    d = deltas[o]["fg_psnr"]
    if b <= qs[0]: bands["Q1(worst baseline)"].append(d)
    elif b <= qs[1]: bands["Q2"].append(d)
    elif b <= qs[2]: bands["Q3"].append(d)
    else: bands["Q4(best baseline)"].append(d)
report["wins_by_baseline_quartile"] = {
    k: {"n": len(v), "wins": sum(1 for x in v if x > 0), "mean_delta": sum(v) / len(v), "median_delta": pct(v, 0.5)}
    for k, v in bands.items()}

# other metrics summary
report["other_metrics"] = {}
for m in ("full_psnr", "fg_lpips", "full_lpips", "fg_ssim", "full_ssim", "edge_ssim"):
    v = [deltas[o][m] for o in objs]
    report["other_metrics"][m] = {
        "mean": sum(v) / len(v), "median": pct(v, 0.5),
        "wins": sum(1 for x in v if x > 0), "losses": sum(1 for x in v if x < 0),
        "p10": pct(v, 0.10), "p90": pct(v, 0.90)}

# top / bottom objects by fg_psnr delta (for Phase 2 fixed visual set + failure analysis)
order = sorted(objs, key=lambda o: deltas[o]["fg_psnr"])
report["bottom12_losses"] = [{"object": o, "delta_fg_psnr": deltas[o]["fg_psnr"],
                              "gfl_fg_psnr": f(gfl[o], "fg_psnr"), "llh_fg_psnr": f(llh[o], "fg_psnr")}
                             for o in order[:12]]
report["top12_wins"] = [{"object": o, "delta_fg_psnr": deltas[o]["fg_psnr"],
                         "gfl_fg_psnr": f(gfl[o], "fg_psnr"), "llh_fg_psnr": f(llh[o], "fg_psnr")}
                        for o in order[-12:]][::-1]
# median-delta objects for visual audit (fixed rule: closest to median on either side)
med = pct(dp, 0.5)
near = sorted(objs, key=lambda o: abs(deltas[o]["fg_psnr"] - med))[:6]
report["median_band_objects"] = [{"object": o, "delta_fg_psnr": deltas[o]["fg_psnr"]} for o in near]

# per-object dump
with open(os.path.join(OUTDIR, "phase1a_llh_gfl_per_object_deltas.csv"), "w", newline="") as fo:
    w = csv.writer(fo)
    w.writerow(["object_id"] + list(next(iter(deltas.values())).keys()) +
               ["gfl_fg_psnr", "llh_fg_psnr", "crop_area"])
    for o in objs:
        w.writerow([o] + [deltas[o][k] for k in next(iter(deltas.values())).keys()] +
                   [f(gfl[o], "fg_psnr"), f(llh[o], "fg_psnr"), cov.get(o, {}).get("crop_area", "")])

with open(os.path.join(OUTDIR, "phase1a_stats.json"), "w") as fo:
    json.dump(report, fo, indent=1)

for k, v in report.items():
    print(k, "=", json.dumps(v) if not isinstance(v, str) else v)
