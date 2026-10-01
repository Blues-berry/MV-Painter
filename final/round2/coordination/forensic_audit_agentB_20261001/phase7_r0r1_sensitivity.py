#!/usr/bin/env python3
"""Phase 7 — R0/R1 output sensitivity (agent B).

Offline only: no regeneration. (1) Image-level R0-vs-R1 comparison on the four
available anchor/realization PNG pairs. (2) Per-object metric drift
distribution seed42(R0, confirmation artifacts) vs seed10042(R1, robustness).
(3) Sanity: conditioning difference stats from the robustness artifacts.
"""
import csv, json, os, hashlib

import numpy as np
from PIL import Image

BASE = "/4T/CXY/MV-Painter/final/round2/coordination"
RB = os.path.join(BASE, "main_backbone_robustness1_20260930")
OUT = os.path.join(BASE, "forensic_audit_agentB_20261001")

pairs = [
    ("layer_llh", "obj_0024"), ("layer_llh", "obj_0025"),
    ("global_c3", "obj_0024"), ("global_c3", "obj_0025"),
]
img_report = []
for sched, obj in pairs:
    r0 = os.path.join(RB, "r0_anchor_llh_10" if sched == "layer_llh" else "r0_completion_global_c3",
                      f"{obj}_{sched}.png")
    r1 = os.path.join(RB, "realization1_core5", f"{obj}_{sched}.png")
    a = np.asarray(Image.open(r0).convert("RGB"), dtype=np.float64) / 255.0
    b = np.asarray(Image.open(r1).convert("RGB"), dtype=np.float64) / 255.0
    mae = float(np.abs(a - b).mean())
    mse = float(((a - b) ** 2).mean())
    psnr = float("inf") if mse == 0 else 10 * np.log10(1.0 / mse)
    ha = hashlib.sha256(open(r0, "rb").read()).hexdigest()[:16]
    hb = hashlib.sha256(open(r1, "rb").read()).hexdigest()[:16]
    img_report.append({"schedule": sched, "object": obj, "mae": round(mae, 6),
                       "psnr_db": round(psnr, 3), "identical": ha == hb,
                       "sha_r0": ha, "sha_r1": hb})

# per-object metric drift R0 -> R1
R0 = {
    "layer_llh": os.path.join(BASE, "layer_confirmation_20260930/layer_llh_per_object_metrics.csv"),
    "layer_lhl": os.path.join(BASE, "layer_confirmation_20260930/layer_lhl_per_object_metrics.csv"),
    "layer_fixed_mean": os.path.join(BASE, "layer_confirmation_20260930/layer_fixed_mean_per_object_metrics.csv"),
    "global_fixed_low": os.path.join(BASE, "final_acceptance_20260930/STRICT276_GLOBAL_FIXED_LOW_RAW.csv"),
}
def load(path, idcol):
    with open(path) as f:
        rs = list(csv.DictReader(f))
    return {(r[idcol]): r for r in rs if r.get("schedule", r.get("method")) }

r1_rows = list(csv.DictReader(open(os.path.join(RB, "per_object_metrics.csv"))))
r1 = {}
for r in r1_rows:
    r1.setdefault(r["schedule"], {})[r["object"]] = r

drift = {}
for sched, path in R0.items():
    r0map = load(path, "object" if "GLOBAL" not in path else "object_id")
    common = sorted(set(r0map) & set(r1.get(sched, {})))
    d_fg = [float(r1[sched][o]["fg_psnr"]) - float(r0map[o]["fg_psnr"]) for o in common]
    d_fl = [float(r1[sched][o]["fg_lpips"]) - float(r0map[o]["fg_lpips"]) for o in common]
    ad = sorted(abs(x) for x in d_fg)
    n = len(ad)
    drift[sched] = {"n": n,
                    "fg_psnr_abs_drift_median": round(ad[n // 2], 4),
                    "p90": round(ad[int(0.9 * n)], 4), "max": round(ad[-1], 4),
                    "mean_signed": round(sum(d_fg) / n, 5),
                    "fg_lpips_abs_drift_median": round(sorted(abs(x) for x in d_fl)[n // 2], 5)}

# conditioning difference stats (their artifact, sanity read)
cond_note = {}
p = os.path.join(RB, "REFERENCE_REALIZATION_DIFFERENCE_summary.json")
if os.path.exists(p):
    cond_note = json.load(open(p))

out = {"image_pairs": img_report, "metric_drift_r0_to_r1": drift,
       "cond_realization_difference_summary": cond_note}
json.dump(out, open(os.path.join(OUT, "phase7_r0r1_sensitivity.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
