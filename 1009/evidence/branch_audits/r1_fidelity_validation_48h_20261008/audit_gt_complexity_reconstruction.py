#!/usr/bin/env python3
"""Cross-check reconstructed GT texture fields against frozen Fresh B rows."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from compute_freshc_gt_complexity import gt_only_metrics  # noqa: E402
from recompute_paired_rgb_metrics import load_json, reconstruct_target, write_csv  # noqa: E402


ROOT = Path("/4T/CXY/MV-Painter/final/round2/scientific_validation_v3")
RUN = ROOT / "formal/campaign_FRESH_CONFIRM_B_20261005"
MANIFEST = ROOT / "fresh_confirm_b/FRESH_CONFIRM_B_MANIFEST.json"
UID_LIST = ROOT / "fresh_confirm_b/fresh_confirm_B_150.txt"
OUT = HERE / "GT_COMPLEXITY_RECONSTRUCTION_AUDIT_FRESHB.csv"
FIELDS = ("gt_fg_rgb_std", "gt_fg_grad_mag", "gt_fg_lap_var", "gt_fg_hf_energy")


def main() -> None:
    objects = {o["source_uid"]: o for o in load_json(MANIFEST)["objects"]}
    metrics: dict[str, dict[str, str]] = {}
    with (RUN / "per_object_metrics.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            if row["condition"] == "native_gfl":
                metrics[row["object_uid"]] = row

    rows = []
    uids = [line.strip().split("/")[-1] for line in UID_LIST.read_text().splitlines() if line.strip()]
    for uid in uids:
        target, mask, view_ids, reverse, source_digest = reconstruct_target(Path(objects[uid]["render_root"]))
        recomputed = gt_only_metrics(target, mask)
        official = metrics[uid]
        row = {
            "cohort": "FreshB",
            "uid": uid,
            "target_view_ids": json.dumps(view_ids),
            "reverse_view_rotation": reverse,
            "gt_selected_source_files_digest_sha256": source_digest,
        }
        for field in FIELDS:
            official_v = float(official[field])
            recomputed_v = float(recomputed[field])
            row[f"{field}_official"] = official_v
            row[f"{field}_reconstructed"] = recomputed_v
            row[f"{field}_absolute_difference"] = abs(official_v - recomputed_v)
        rows.append(row)

    write_csv(OUT, rows)
    report = {
        "n": len(rows),
        "fields": {},
        "interpretation": "CPU float32 reconstruction; comparison is against the frozen Fresh B official GT-only columns.",
        "output": str(OUT),
    }
    for field in FIELDS:
        diffs = np.asarray([r[f"{field}_absolute_difference"] for r in rows], dtype=float)
        report["fields"][field] = {
            "max_abs_diff": float(diffs.max()),
            "mean_abs_diff": float(diffs.mean()),
            "n_with_abs_diff_le_1e-6": int((diffs <= 1e-6).sum()),
            "n_with_abs_diff_le_1e-4": int((diffs <= 1e-4).sum()),
        }
    (HERE / "GT_COMPLEXITY_RECONSTRUCTION_AUDIT_FRESHB.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
