#!/usr/bin/env python3
"""Build visual casebooks from identity-checked C1 paired output manifests."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = Path("/4T/CXY/MV-Painter-r1color")
BASE = Path("/4T/CXY/MV-Painter")
DEV_INTERVENTION = HERE / "runs/phase_b/COLOR_INTERVENTION_RESULTS.csv"
DEV_PAIRED = HERE / "runs/phase_c/dev/C_REPAIR_PAIRED_RESULTS.csv"
DEV_CASES = HERE / "runs/phase_c/dev/case_images"
HOLDOUT_PAIRED = HERE / "runs/phase_d/freshb/C_REPAIR_PAIRED_RESULTS.csv"
HOLDOUT_OBJECTS = HERE / "runs/phase_d/freshb/COLOR_REPAIR_VALIDATION.csv"
HOLDOUT_CASES = HERE / "runs/phase_d/freshb/case_images"
HOLDOUT_LOCK = HERE / "protocol/D_VALIDATION_LOCK.json"
PRIOR_RESULTS = ROOT / "1008/engineering/fidelity_validation_48h/B_OBJECT_LEVEL_RESULTS.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def load_rgb(path: str | Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"))


def sha_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_image(path: str | Path, expected_sha256: str) -> None:
    if sha_file(path) != expected_sha256:
        raise RuntimeError(f"casebook image SHA mismatch: {path}")


def add_image_panel(ax, path: str | Path, title: str, *, zoom=0.92) -> None:
    image = load_rgb(path)
    ax.imshow(image)
    ax.set_title(title, fontsize=11)
    ax.set_xticks([])
    ax.set_yticks([])
    for edge in ax.spines.values():
        edge.set_visible(False)


def compose_page(pdf: PdfPages, uid: str, record: dict, panels: list[tuple[str, str]],
                 subtitle: str, *, blind_labels: bool = False) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(17, 12))
    flat = axes.ravel()
    for ax, (title, path) in zip(flat, panels):
        add_image_panel(ax, path, title)
    for ax in flat[len(panels):]:
        ax.axis("off")
    fig.suptitle(f"{uid}\n{subtitle}", fontsize=15, y=0.99)
    if not blind_labels:
        text = (
            f"5 unseen views: ΔFG-CIEDE2000={float(record.get('delta_unseen_fg_ciede2000', 'nan')):+.3f}; "
            f"ΔFG-PSNR={float(record.get('delta_unseen_fg_psnr', 'nan')):+.3f} dB; "
            f"ΔFG-LPIPS={float(record.get('delta_unseen_fg_lpips', 'nan')):+.4f}; "
            f"ΔL*SSIM-to-GT={float(record.get('delta_unseen_lstar_ssim_to_gt', 'nan')):+.4f}"
        )
        source_text = (
            f"Source view: ΔFG-CIEDE2000={float(record.get('source_delta_fg_ciede2000', 'nan')):+.3f}; "
            f"estimated offset=({float(record.get('applied_delta_a_star', 'nan')):+.2f}, "
            f"{float(record.get('applied_delta_b_star', 'nan')):+.2f}) Lab"
        )
        fig.text(0.5, 0.018, text + "\n" + source_text, ha="center", va="bottom", fontsize=10)
    fig.tight_layout(rect=(0.02, 0.065, 0.98, 0.95))
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def dev_pages(pdf: PdfPages) -> list[dict]:
    per_view = read_csv(DEV_PAIRED)
    interventions = read_csv(DEV_INTERVENTION)
    by_uid: dict[str, dict] = {}
    for row in per_view:
        if row["view_idx"] == "0":
            by_uid[row["uid"]] = row
    by_condition = {}
    for row in interventions:
        if row["target_tile_index"] == "0":
            by_condition.setdefault(row["uid"], {})[row["condition"]] = row["prediction_png"]
    records = []
    for uid in sorted(by_uid):
        row = by_uid[uid]
        paths = by_condition.get(uid, {})
        required = ["no_adapter", "gfl_baseline", "layer_llh"]
        if any(name not in paths for name in required):
            raise RuntimeError(f"{uid}: Phase B reference images are incomplete")
        for condition in required:
            source_row = next(r for r in interventions
                              if r["uid"] == uid and r["condition"] == condition and r["target_tile_index"] == "0")
            verify_image(paths[condition], source_row["prediction_png_sha256"])
        for image_path, image_sha in (
            (row["source_condition_png"], row["source_condition_png_sha256"]),
            (row["gt_sixview_png"], row["gt_sixview_png_sha256"]),
            (row["baseline_png"], row["baseline_png_sha256"]),
            (row["candidate_png"], row["candidate_png_sha256"]),
        ):
            verify_image(image_path, image_sha)
        panels = [
            ("Transformed source condition", row["source_condition_png"]),
            ("GT unique6", row["gt_sixview_png"]),
            ("No Adapter", paths["no_adapter"]),
            ("GFL", paths["gfl_baseline"]),
            ("LLH", paths["layer_llh"]),
            ("GFL + fixed C1", row["candidate_png"]),
        ]
        record = {
            "uid": uid,
            "source_cohort": row["source_cohort"],
            "delta_unseen_fg_ciede2000": row["delta_fg_ciede2000_candidate"],
            "delta_unseen_fg_psnr": row["delta_fg_psnr_candidate"],
            "delta_unseen_fg_lpips": row["delta_fg_lpips"],
            "delta_unseen_lstar_ssim_to_gt": row["delta_foreground_lstar_ssim_to_gt"],
            "source_delta_fg_ciede2000": row["delta_fg_ciede2000_candidate"],
            "applied_delta_a_star": row["applied_delta_a_star"],
            "applied_delta_b_star": row["applied_delta_b_star"],
        }
        compose_page(pdf, uid, record, panels, row["source_cohort"])
        records.append(record)
    return records


def holdout_selection() -> tuple[list[dict], list[dict]]:
    objects = read_csv(HOLDOUT_OBJECTS)
    per_view = read_csv(HOLDOUT_PAIRED)
    lock = json.loads(HOLDOUT_LOCK.read_text())
    cutpoints = [float(x) for x in lock["texture_strata"]["cutpoints"]]
    by_uid = {row["uid"]: row for row in objects}
    selected = []
    for q in range(4):
        subset = []
        for row in objects:
            value = float(row["gt_fg_lap_var"])
            assigned = int(np.searchsorted(cutpoints, value, side="right")) + 1
            if assigned == q + 1:
                subset.append(row)
        median = float(np.median([float(row["gt_fg_lap_var"]) for row in subset]))
        chosen = min(subset, key=lambda row: (abs(float(row["gt_fg_lap_var"]) - median), row["uid"]))
        selected.append(chosen)
    ranked = sorted(objects, key=lambda row: float(row["delta_unseen_fg_ciede2000"]))
    candidate_rows = selected + ranked[:3] + ranked[-3:]
    deduped = []
    seen = set()
    for row in candidate_rows:
        if row["uid"] not in seen:
            deduped.append(row)
            seen.add(row["uid"])
    view0 = {row["uid"]: row for row in per_view if row["view_idx"] == "0"}
    for row in deduped:
        row["_source_record"] = view0[row["uid"]]
    return selected, deduped


def holdout_pages(pdf: PdfPages) -> list[dict]:
    reps, selected = holdout_selection()
    prior = {row["uid"]: row for row in read_csv(PRIOR_RESULTS) if row["cohort"] == "FreshB"}
    records = []
    reps_by_uid = {row["uid"]: i + 1 for i, row in enumerate(reps)}
    for row in selected:
        uid = row["uid"]
        source = row["_source_record"]
        base_row = prior[uid]
        llh_path = Path(base_row["llh_prediction_png"])
        if not llh_path.exists():
            raise FileNotFoundError(f"Fresh B LLH image is missing for {uid}")
        for image_path, image_sha in (
            (source["source_condition_png"], source["source_condition_png_sha256"]),
            (source["gt_sixview_png"], source["gt_sixview_png_sha256"]),
            (base_row["gfl_prediction_png"], base_row["gfl_prediction_sha256"]),
            (base_row["llh_prediction_png"], base_row["llh_prediction_sha256"]),
            (source["baseline_png"], source["baseline_png_sha256"]),
            (source["candidate_png"], source["candidate_png_sha256"]),
        ):
            verify_image(image_path, image_sha)
        panels = [
            ("Transformed source condition", source["source_condition_png"]),
            ("GT unique6", source["gt_sixview_png"]),
            ("GFL", base_row["gfl_prediction_png"]),
            ("LLH", base_row["llh_prediction_png"]),
            ("GFL + fixed C1", source["candidate_png"]),
        ]
        subtitle = (
            f"Fresh B; GT-texture quartile representative Q{reps_by_uid[uid]}" if uid in reps_by_uid
            else "Fresh B; outcome-ranked casebook example (illustrative, not a new validation subset)"
        )
        compose_page(pdf, uid, row, panels, subtitle)
        record = {k: v for k, v in row.items() if k != "_source_record"}
        record["selection"] = subtitle
        record["gfl_png_sha256"] = base_row["gfl_prediction_sha256"]
        record["llh_png_sha256"] = base_row["llh_prediction_sha256"]
        record["candidate_png_sha256"] = source["candidate_png_sha256"]
        records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "BEFORE_AFTER_COLOR_CASEBOOK.pdf")
    args = parser.parse_args()
    if not DEV_PAIRED.exists() or not HOLDOUT_PAIRED.exists():
        raise RuntimeError("both development and independent Fresh B C1 results are required")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(args.output) as pdf:
        dev_records = dev_pages(pdf)
        holdout_records = holdout_pages(pdf)
    (HERE / "BEFORE_AFTER_COLOR_CASEBOOK_SELECTION.json").write_text(json.dumps({
        "selection_rule": "All four locked development objects; Fresh B GT-only texture quartile median-nearest representative per Q; plus three largest wins and three largest regressions for failure casebook coverage.",
        "freshb_visual_representatives": [r["uid"] for r in holdout_selection()[0]],
        "pages": dev_records + holdout_records,
    }, indent=2) + "\n")
    print(json.dumps({"pdf": str(args.output.resolve()), "development_cases": len(dev_records),
                      "freshb_cases": len(holdout_records)}, indent=2))


if __name__ == "__main__":
    main()
