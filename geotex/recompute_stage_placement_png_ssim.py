"""Recompute stage-placement Full-SSIM from PNG predictions and raw RGBA GT.

The formal stage runner records metrics before PNG serialization.  This
post-processing step keeps the frozen predictions and checkpoint untouched and
recomputes only Full-SSIM under the selected saved-artifact path:
float32 PNG reload prediction versus float32 RGBA/white-background GT.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "geotex"))

from audit_clean_v2_raw_metrics import compute_ssim, load_panel, panel_for_uid  # noqa: E402
from round2_stats import paired_csv_summary  # noqa: E402


OUT = ROOT / "final/round2/stage_placement_276_20260929"
PNG_DIR = OUT / "predictions"
OBJECT_LIST = ROOT / "final/round2/clean_dataset_v2/strict_holdout_objects_276_clean_v2.txt"
DATA_ROOT = ROOT / "data/train_data/rendered_full"
SCHEDULES = ("fixed_mean", "hll", "llh", "c3_lhl")
OBJECT_IDS = tuple(f"obj_{i:04d}" for i in range(24, 300))


def write_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def main() -> int:
    uids = [line.strip() for line in OBJECT_LIST.read_text().splitlines() if line.strip()]
    if len(uids) != len(OBJECT_IDS):
        raise ValueError(f"expected {len(OBJECT_IDS)} strict-holdout UIDs, found {len(uids)}")
    rows: list[dict[str, object]] = []
    for index, (object_id, uid) in enumerate(zip(OBJECT_IDS, uids)):
        target, _mask, _depth, _reverse = panel_for_uid(DATA_ROOT, uid)
        for schedule in SCHEDULES:
            prediction_path = PNG_DIR / schedule / f"{object_id}.png"
            prediction = load_panel(prediction_path)
            rows.append({
                "object": object_id,
                "uid": uid,
                "schedule": schedule,
                "full_ssim": float(compute_ssim(prediction.unsqueeze(0), target.unsqueeze(0))),
                "prediction_png": str(prediction_path.resolve()),
                "prediction_dtype": "torch.float32",
                "ground_truth": "raw_rgba_composited_over_white_float32",
            })
        if (index + 1) % 25 == 0:
            print(f"[{index + 1}/{len(OBJECT_IDS)}]", flush=True)

    output_csv = OUT / "serialized_full_ssim_per_object.csv"
    with output_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    by_schedule: dict[str, dict[str, dict[str, str]]] = {}
    for schedule in SCHEDULES:
        schedule_rows = [row for row in rows if row["schedule"] == schedule]
        schedule_csv = OUT / f"per_object_{schedule}_serialized_full_ssim.csv"
        with schedule_csv.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["object", "uid", "full_ssim"])
            writer.writeheader()
            writer.writerows({key: row[key] for key in ("object", "uid", "full_ssim")} for row in schedule_rows)
        by_schedule[schedule] = {str(row["object"]): {"object": str(row["object"]), "full_ssim": str(row["full_ssim"])} for row in schedule_rows}

    comparisons = {}
    for baseline in ("fixed_mean", "hll", "llh"):
        comparisons[f"c3_lhl_vs_{baseline}"] = paired_csv_summary(
            by_schedule["c3_lhl"],
            by_schedule[baseline],
            metrics=("full_ssim",),
            object_ids=OBJECT_IDS,
            higher_is_better={"full_ssim": True},
            seed=20260928,
            n_resamples=10000,
        )

    summary = {
        "status": "complete",
        "protocol": "clean-v2-stage-placement-followup-v1",
        "metric": "full_ssim",
        "prediction": "PNG reload float32",
        "ground_truth": "original RGBA composited over white float32",
        "objects": len(OBJECT_IDS),
        "schedules": list(SCHEDULES),
        "paired_bootstrap": {"seed": 20260928, "resamples": 10000, "unit": "object-level paired bootstrap", "ci": 0.95},
        "mean_by_schedule": {
            schedule: sum(float(row["full_ssim"]) for row in rows if row["schedule"] == schedule) / len(OBJECT_IDS)
            for schedule in SCHEDULES
        },
        "comparisons": comparisons,
        "source_csv": str(output_csv.resolve()),
        "paper_edit_allowed": False,
    }
    write_json(OUT / "serialized_full_ssim_paired_comparisons.json", summary)
    (OUT / "SERIALIZED_FULL_SSIM_STAGE_PLACEMENT.md").write_text(
        "# Serialized Full-SSIM stage-placement audit\n\n"
        "This CPU-only post-processing pass recomputes Full-SSIM from the frozen PNG predictions, "
        "reloaded as float32, against the original RGBA/white-background float32 GT. The formal "
        "pre-save metric CSV remains unchanged; this file is the saved-artifact Full-SSIM branch.\n\n"
        f"- Objects: {len(OBJECT_IDS)}\n"
        f"- Schedules: {', '.join(SCHEDULES)}\n"
        "- Bootstrap: 10,000 object-level paired resamples, seed 20260928\n"
        "- No checkpoint, dataset, prediction PNG, or paper source was modified.\n"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
