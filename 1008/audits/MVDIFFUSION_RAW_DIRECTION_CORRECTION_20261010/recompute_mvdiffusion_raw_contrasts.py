#!/usr/bin/env python3
"""Recompute MVDiffusion paired contrasts using raw condition A minus B.

The frozen source analysis direction-codes lower-is-better metrics so a
positive value favors the left condition. This script preserves that result
for comparison while also exporting raw A-B estimates and intervals.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "source_evidence/r2/cross_backbone_20261010/mvdiffusion"
RESULTS = SOURCE / "results"
RESAMPLES = 10_000
SEED = 20_260_928

METRICS = {
    "interop_psnr": ("PSNR (dB)", "higher"),
    "interop_fg_ssim": ("FG-SSIM", "higher"),
    "interop_edge_ssim": ("Edge-SSIM", "higher"),
    "interop_fg_lpips": ("FG-LPIPS", "lower"),
    "interop_ciede2000": ("CIEDE2000", "lower"),
    "interop_gt_relative_texture_error": ("GT-relative texture error", "lower"),
}

COMPARISONS = [
    ("P1", "L-LLH", "G-FL"),
    ("P2", "L-LLH", "G-LLH"),
    ("P3", "L-LLH", "L-FIX"),
    ("P4", "L-LHL", "G-LHL"),
    ("P5", "G-LLH", "G-LHL"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    panel_path = RESULTS / "MVDIFFUSION_STANDARD_PANEL_RESULTS.csv"
    panel_rows = read_csv(panel_path)
    expected_conditions = {"R0", "G-FL", "G-LHL", "G-LLH", "L-FIX", "L-LHL", "L-LLH"}
    conditions = sorted({row["condition"] for row in panel_rows})
    if len(panel_rows) != 525 or set(conditions) != expected_conditions:
        raise ValueError(f"Expected 525 rows across seven conditions; got {len(panel_rows)} / {conditions}")

    object_ids = sorted({row["object"] for row in panel_rows})
    if len(object_ids) != 75:
        raise ValueError(f"Expected 75 object IDs; got {len(object_ids)}")

    panel: dict[str, dict[str, dict[str, float]]] = {condition: {} for condition in conditions}
    for row in panel_rows:
        condition, object_id = row["condition"], row["object"]
        if object_id in panel[condition]:
            raise ValueError(f"Duplicate condition/object row: {condition}/{object_id}")
        panel[condition][object_id] = {metric: float(row[metric]) for metric in METRICS}

    for condition in conditions:
        if set(panel[condition]) != set(object_ids):
            raise ValueError(f"Object set mismatch for {condition}")

    # Verify that all six newly scheduled conditions exactly match their
    # preserved per-object source CSVs; the seventh condition is archived R0.
    source_csvs = []
    run_configs = []
    source_uids: dict[str, str] = {}
    for condition in expected_conditions - {"R0"}:
        source_csv = RESULTS / f"panel_{condition}_75/per_object_metrics_ext.csv"
        source_csvs.append(source_csv)
        rows = read_csv(source_csv)
        if len(rows) != 75 or {row["object"] for row in rows} != set(object_ids):
            raise ValueError(f"Source object mismatch for {condition}")
        for row in rows:
            if int(row["target_view_count"]) != 6:
                raise ValueError(f"Expected six scored target views in {condition}/{row['object']}")
            previous_uid = source_uids.setdefault(row["object"], row["source_uid"])
            if previous_uid != row["source_uid"]:
                raise ValueError(f"Source UID mismatch for {condition}/{row['object']}")
            for metric in METRICS:
                expected = panel[condition][row["object"]][metric]
                observed = float(row[metric])
                if not np.isclose(expected, observed, rtol=0, atol=1e-12):
                    raise ValueError(f"Panel/source mismatch: {condition}/{row['object']}/{metric}")
        config_path = RESULTS / f"panel_{condition}_75/run_config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if config["condition"] != condition or config["config"]["dataset"]["num_views"] != 12:
            raise ValueError(f"Unexpected run condition or output-grid size in {config_path}")
        run_configs.append(config_path)

    manifest_path = SOURCE / "data_manifest_holdout_exact_75.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_objects = {row["object"]: row for row in manifest["objects"]}
    if set(manifest_objects) != set(object_ids) or any(
        len(row["target_view_ids"]) != 6 for row in manifest["objects"]
    ):
        raise ValueError("The frozen metric manifest must contain the same 75 objects and six scored views per object")

    archive_json_path = RESULTS / "MVDIFFUSION_PAIRED_BOOTSTRAP.json"
    archived = json.loads(archive_json_path.read_text(encoding="utf-8"))
    output_rows: list[dict[str, str | float | int]] = []

    for short_name, condition_a, condition_b in COMPARISONS:
        archive_key = f"{short_name}_{condition_a}_vs_{condition_b}"
        for metric, (display_name, direction) in METRICS.items():
            raw = np.array([
                panel[condition_a][object_id][metric] - panel[condition_b][object_id][metric]
                for object_id in object_ids
            ], dtype=float)
            if not np.isfinite(raw).all():
                raise ValueError(f"Non-finite paired values in {archive_key}/{metric}")

            # Match the archived percentile-bootstrap protocol exactly:
            # one seeded generator per metric and comparison.
            rng = np.random.default_rng(SEED)
            sample_indices = rng.integers(0, len(raw), size=(RESAMPLES, len(raw)))
            raw_boot = raw[sample_indices].mean(axis=1)
            raw_low, raw_high = np.percentile(raw_boot, [2.5, 97.5])

            improvement = -raw if direction == "lower" else raw
            improvement_boot = improvement[sample_indices].mean(axis=1)
            improvement_low, improvement_high = np.percentile(improvement_boot, [2.5, 97.5])

            prior = archived["comparisons"][archive_key]["metrics"][metric]
            for key, observed in (
                ("paired_mean_delta", float(improvement.mean())),
                ("ci95_low", float(improvement_low)),
                ("ci95_high", float(improvement_high)),
            ):
                if not np.isclose(observed, float(prior[key]), rtol=0, atol=1e-12):
                    raise ValueError(f"Archived direction-coded statistic mismatch: {archive_key}/{metric}/{key}")

            a_better = raw < 0 if direction == "lower" else raw > 0
            output_rows.append({
                "comparison": short_name,
                "condition_A": condition_a,
                "condition_B": condition_b,
                "metric": display_name,
                "direction": f"{direction}-is-better",
                "n_objects": len(raw),
                "raw_A_minus_B_mean": float(raw.mean()),
                "raw_CI95_low": float(raw_low),
                "raw_CI95_high": float(raw_high),
                "improvement_coded_mean": float(improvement.mean()),
                "improvement_CI95_low": float(improvement_low),
                "improvement_CI95_high": float(improvement_high),
                "objects_favoring_A": int(a_better.sum()),
                "objects_favoring_A_fraction": float(a_better.mean()),
            })

    contrast_csv = HERE / "MVDIFFUSION_RAW_CONTRASTS.csv"
    with contrast_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    means_csv = HERE / "MVDIFFUSION_PANEL_MEANS.csv"
    mean_fields = ["condition", "n_objects", *[m[0] for m in METRICS.values()]]
    with means_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=mean_fields)
        writer.writeheader()
        for condition in conditions:
            row: dict[str, str | int | float] = {"condition": condition, "n_objects": 75}
            for metric, (display_name, _) in METRICS.items():
                row[display_name] = float(np.mean([panel[condition][o][metric] for o in object_ids]))
            writer.writerow(row)

    input_paths = [panel_path, archive_json_path, RESULTS / "MVDIFFUSION_PAIRED_BOOTSTRAP_SUMMARY.md",
                   SOURCE / "scripts/analyze_mvdiffusion_panel_20260930.py", manifest_path,
                   *source_csvs, *run_configs]
    input_hashes = HERE / "INPUTS_SHA256SUMS.txt"
    input_hashes.write_text("".join(f"{sha256(path)}  {path.relative_to(SOURCE)}\n" for path in input_paths),
                            encoding="utf-8")

    print(f"Verified {len(panel_rows)} panel rows ({len(conditions)} conditions x {len(object_ids)} objects).")
    print(f"Verified {len(source_csvs)} scheduled per-object CSVs, 12-view run configs, and the six-view metric manifest.")
    print(f"Reproduced all {len(output_rows)} archived direction-coded means and bootstrap intervals.")
    print(f"Wrote {contrast_csv.name}, {means_csv.name}, and {input_hashes.name}.")


if __name__ == "__main__":
    main()
