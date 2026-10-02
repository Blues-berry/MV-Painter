#!/usr/bin/env python3
"""Build the GT-only texture statistics JSON for Experiment E (H5).

Sources (GT-only, method-independent):
  * gt_fg_lap_var / gt_fg_rgb_std / gt_fg_grad_mag / gt_fg_hf_energy —
    any per-condition CSV column (GT-side probes are identical across
    conditions; the script verifies equality across two conditions)
  * coverage — mean alpha coverage over the six target views from the frozen
    cohort manifest (fresh_confirm_N_manifest.csv)

Output: gt_stats.json  {stat_name: {uid: value}}
"""
import csv
import json
import sys
from pathlib import Path


def main() -> None:
    run_dir = Path(sys.argv[1])
    manifest = Path(sys.argv[2])
    out = Path(sys.argv[3])

    stats = {k: {} for k in ("gt_fg_lap_var", "gt_fg_rgb_std", "gt_fg_grad_mag",
                             "gt_fg_hf_energy", "coverage")}

    csvs = sorted(run_dir.glob("*_per_object_metrics.csv"))
    if not csvs:
        raise RuntimeError("no per-condition CSVs found")
    ref_cond = csvs[0]
    print(f"reference CSV: {ref_cond.name}")

    def collect(path: Path, keys) -> dict:
        rows = csv.DictReader(path.open())
        table = {}
        for r in rows:
            uid = r["object_uid"]
            table[uid] = {k: float(r[k]) for k in keys if r.get(k) not in (None, "")}
        return table

    keys = list(stats)[:4]
    table = collect(ref_cond, keys)
    for uid, kv in table.items():
        for k, v in kv.items():
            stats[k][uid] = v

    # cross-check GT columns are condition-independent on one other CSV
    if len(csvs) > 1:
        other = collect(csvs[1], keys)
        n_mismatch = 0
        for uid, kv in other.items():
            for k, v in kv.items():
                if uid in stats[k] and abs(stats[k][uid] - v) > 1e-9:
                    n_mismatch += 1
        print(f"cross-check {csvs[1].name}: mismatches={n_mismatch}")
        if n_mismatch:
            raise RuntimeError("GT columns differ across conditions — abort")

    # coverage from manifest
    with manifest.open() as f:
        rdr = csv.DictReader(f)
        cov_cols = [c for c in rdr.fieldnames if c.startswith("coverage_")]
        for r in rdr:
            vals = [float(r[c]) for c in cov_cols if r.get(c) not in (None, "")]
            if vals:
                stats["coverage"][r["uid"]] = sum(vals) / len(vals)

    out.write_text(json.dumps(stats, indent=2) + "\n")
    print(f"wrote {out} ({len(table)} objects)")


if __name__ == "__main__":
    sys.exit(main())
