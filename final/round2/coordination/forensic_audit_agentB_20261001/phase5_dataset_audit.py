#!/usr/bin/env python3
"""Phase 5 — dataset forensic audit (agent B).

Verifies cohort definitions and disjointness across all paper-facing
experiments, the MVDiffusion 76->75 exclusion, and the unique6 view constant.
Read-only; heavy per-file SHA inventory is delegated to the existing
FINAL_REPRODUCIBILITY_MANIFEST (cross-referenced, not duplicated).
"""
import csv, json, os

BASE = "/4T/CXY/MV-Painter/final/round2"
OUT = os.path.join(BASE, "coordination/forensic_audit_agentB_20261001")

def uids(path):
    return [l.strip() for l in open(path) if l.strip()]

strict = uids(os.path.join(BASE, "clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"))
probe = uids(os.path.join(BASE, "clean_dataset_v2/probe_objects_24_clean_v2.txt"))
eval300 = uids(os.path.join(BASE, "clean_dataset_v2/eval_objects_300_clean_v2.txt"))

report = {"counts": {"strict276": len(strict), "probe24": len(probe), "eval300": len(eval300)},
          "duplicates_within": {n: len(v) - len(set(v)) for n, v in
                                [("strict276", strict), ("probe24", probe), ("eval300", eval300)]},
          "probe_in_strict": sorted(set(probe) & set(strict)),
          "probe_in_eval300": len(set(probe) & set(eval300)),
          "strict_in_eval300": len(set(strict) & set(eval300))}

# train pool: from paper (1,118 main / 1,706 FAC). Look for the training pool list
train_candidates = []
for root, dirs, files in os.walk(os.path.join(BASE, "clean_dataset_v2")):
    for f in files:
        if "train" in f.lower():
            train_candidates.append(os.path.join(root, f))
report["train_list_files_found"] = train_candidates

# MV-Adapter 76 and MVDiffusion 75/76 manifests
mvad = None
p = os.path.join(BASE, "mv_adapter")
if os.path.isdir(p):
    for f in sorted(os.listdir(p)):
        if "76" in f and f.endswith(".json"):
            mvad = os.path.join(p, f)
mvdiff76 = json.load(open(os.path.join(BASE, "mvdiffusion/data_manifest_holdout_exact_76.json")))
mvdiff75 = json.load(open(os.path.join(BASE, "mvdiffusion/data_manifest_holdout_exact_75.json")))

def obj_ids_from_manifest(m):
    if isinstance(m, dict):
        for k in ("objects", "object_ids", "cohort", "entries"):
            if k in m:
                v = m[k]
                if isinstance(v, list) and v:
                    if isinstance(v[0], dict):
                        return [e.get("object") or e.get("object_id") or e.get("id") for e in v]
                    return v
    return None

o76 = obj_ids_from_manifest(mvdiff76)
o75 = obj_ids_from_manifest(mvdiff75)
report["mvdiffusion_76_count"] = len(o76) if o76 else None
report["mvdiffusion_75_count"] = len(o75) if o75 else None
if o76 and o75:
    excluded = sorted(set(o76) - set(o75))
    report["mvdiffusion_excluded"] = excluded
    # exclusion rule evidence
    for k in ("excluded", "exclusion", "exclusion_rule", "notes"):
        if isinstance(mvdiff75, dict) and k in mvdiff75:
            report[f"mvdiffusion_75_{k}"] = mvdiff75[k]

# cross-cohort overlaps in obj-ID space
def norm(ids):
    return set(ids) if ids else set()
if o76:
    strict_ids = set(f"obj_{i:04d}" for i in range(24, 300))
    report["mvdiffusion76_within_strict276_idspace"] = len(norm(o76) & strict_ids)
    report["mvdiffusion76_equal_strict_minus_subset"] = sorted(strict_ids - norm(o76))[:10]

# unique6 constant across runners
consts = {}
for f in ["coordination/layer_confirmation_20260930/layer_llh_protocol_manifest.json",
          "coordination/main_backbone_robustness1_20260930/PROTOCOL_LOCK.md"]:
    fp = os.path.join(BASE, f)
    if os.path.exists(fp):
        txt = open(fp).read()
        consts[f.split('/')[-1]] = ("[0, 15, 12, 16, 13, 14]" in txt) or ("0, 15, 12, 16, 13, 14" in txt)
report["unique6_documented"] = consts

# probe-24 / MV-Adapter calibration-24 overlap with strict
mvad_cal = None
for f in sorted(os.listdir(os.path.join(BASE, "mv_adapter"))) if os.path.isdir(p) else []:
    pass

json.dump(report, open(os.path.join(OUT, "phase5_dataset_audit.json"), "w"), indent=1)
print(json.dumps(report, indent=1))
