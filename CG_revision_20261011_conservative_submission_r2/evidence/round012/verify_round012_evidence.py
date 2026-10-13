#!/usr/bin/env python3
"""Recompute bundled Round 12 follow-up statistics from saved score rows."""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

freeze = read("confirmation64/CONFIRMATION64_FREEZE.json")
audit = read("confirmation64/CANDIDATE_EXPOSURE_AUDIT_STAGE02.json")
test = read("confirmation64/CONFIRMATION64_TEST.json")
secondary = read("confirmation64/SECONDARY_DESCRIPTIVE_RECHECK.json")
scores_path = ROOT / "confirmation64/scores_native_grid_projection_view_projection_interaction_projection.json"
scores = json.loads(scores_path.read_text(encoding="utf-8"))
worker = ROOT / "confirmation64/evaluate_confirmation012.py"
ledger = read("confirmation64/OUTPUT_REUSE_AND_IDENTITY_LEDGER.json")
dev = read("development32/COHORT_AND_ANALYSIS_FREEZE.json")

checks = {}
checks["freeze_hash_matches_test"] = sha(ROOT / "confirmation64/CONFIRMATION64_FREEZE.json") == test["freeze_sha256"]
checks["score_rows_hash_matches_test"] = sha(scores_path) == test["scores_sha256"]
checks["scorer_source_hash_matches_scores"] = sha(worker) == scores["source_sha256"]
checks["candidate_order_matches_exposure_audit"] = freeze["uids"] == audit["eligible_uids"][:64]
checks["candidate_exposure_hash_matches_freeze"] = sha(ROOT / "confirmation64/CANDIDATE_EXPOSURE_AUDIT_STAGE02.json") == freeze["eligible_sha256"]
checks["development_and_followup_uids_disjoint"] = not (set(freeze["uids"]) & set(dev["uids"]))
checks["cohort_and_seed_counts"] = len(freeze["uids"]) == 64 and len(set(freeze["uids"])) == 64 and len(freeze["seeds"]) == 3
keys = [(r["seed"], r["uid"], r["condition"]) for r in scores["rows"]]
expected = {(s, u, c) for s in freeze["seeds"] for u in freeze["uids"] for c in freeze["conditions"]}
checks["all_768_cells_unique_and_complete"] = len(keys) == 768 and len(set(keys)) == 768 and set(keys) == expected
ledger_rows = ledger["rows"]
checks["identity_ledger_has_all_cells"] = len(ledger_rows) == 768 and len({(r["seed"], r["uid"], r["condition"]) for r in ledger_rows}) == 768

table = {(r["seed"], r["uid"], r["condition"]): r for r in scores["rows"]}
def per_object(condition: str, domain: str, metric: str) -> np.ndarray:
    return np.asarray([
        np.mean([
            table[(seed, uid, condition)][domain][metric] - table[(seed, uid, "native")][domain][metric]
            for seed in freeze["seeds"]
        ])
        for uid in freeze["uids"]
    ], dtype=np.float64)

def stats(d: np.ndarray) -> dict:
    rng = np.random.default_rng(20261010)
    index = rng.integers(0, len(d), size=(20000, len(d)))
    ci = np.percentile(d[index].mean(axis=1), [2.5, 97.5])
    rng = np.random.default_rng(20261010)
    flips = rng.choice([-1, 1], size=(200000, len(d)))
    obs = abs(float(d.mean()))
    p = (1 + int((np.abs((flips * d).mean(axis=1)) >= obs - 1e-12).sum())) / 200001
    return {"mean": float(d.mean()), "ci": [float(ci[0]), float(ci[1])], "p": float(p)}

primary_pairs = [("source", "fg_psnr"), ("source", "ciede2000")]
primary_recomputed = [stats(per_object("view_projection", domain, metric)) for domain, metric in primary_pairs]
for got, row in zip(primary_recomputed, test["primaries"]):
    checks[f"primary_{row['metric']}_mean_ci_p_match"] = (
        math.isclose(got["mean"], row["mean_difference"], abs_tol=1e-10)
        and np.allclose(got["ci"], row["ci95"], atol=1e-10, rtol=0)
        and math.isclose(got["p"], row["p_value"], abs_tol=1e-12)
    )

sec_rows = {(r["domain"], r["metric"]): r for r in secondary["rows"]}
for domain in ("source", "nonreference_mean"):
    metrics = ("fg_psnr", "fg_ssim", "fg_lpips", "ciede2000")
    for metric in metrics:
        d = per_object("view_projection", domain, metric)
        rng = np.random.default_rng(20261010)
        index = rng.integers(0, len(d), size=(20000, len(d)))
        ci = np.percentile(d[index].mean(axis=1), [2.5, 97.5])
        saved = sec_rows[(domain, metric)]
        checks[f"secondary_{domain}_{metric}_matches"] = (
            math.isclose(float(d.mean()), saved["mean"], abs_tol=1e-10)
            and np.allclose(ci, saved["ci95_pointwise"], atol=1e-10, rtol=0)
        )

apg_protocol = ROOT / "apg/APG_PROTOCOL_FREEZE.json"
apg = read("apg/APG_COMPARISONS.json")
checks["apg_protocol_hash_matches"] = sha(apg_protocol) == apg["protocol_sha256"]
mva_protocol = ROOT / "mvadapter/MVA_PROTOCOL_FREEZE.json"
mva = read("mvadapter/MVA_COMPARISONS.json")
checks["mvadapter_protocol_hash_matches"] = sha(mva_protocol) == mva["protocol_sha256"]

available_outputs = 0
output_hash_mismatches = []
for row in ledger_rows:
    path = Path(row["source_path"])
    if path.is_file():
        available_outputs += 1
        file_hash = sha(path)
        pixel_hash = hashlib.sha256(np.asarray(Image.open(path).convert("RGB")).tobytes()).hexdigest()
        if file_hash != row["source_sha256"] or pixel_hash != row["pixel_sha256"]:
            output_hash_mismatches.append({"path": str(path), "file_hash_match": file_hash == row["source_sha256"], "pixel_hash_match": pixel_hash == row["pixel_sha256"]})

if available_outputs:
    checks["all_available_output_files_and_pixels_match_ledger"] = not output_hash_mismatches

report = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "cohort": {"objects": len(freeze["uids"]), "seeds": freeze["seeds"], "conditions": freeze["conditions"], "score_rows": len(scores["rows"])},
    "primary_recomputed": primary_recomputed,
    "output_identity_audit": {
        "available": available_outputs,
        "ledger_rows": len(ledger_rows),
        "coverage": "complete" if available_outputs == len(ledger_rows) else ("partial" if available_outputs else "none"),
        "file_or_pixel_hash_mismatches": output_hash_mismatches[:10],
    },
}
print(json.dumps(report, indent=2, ensure_ascii=False))
if report["status"] != "PASS":
    raise SystemExit(1)
