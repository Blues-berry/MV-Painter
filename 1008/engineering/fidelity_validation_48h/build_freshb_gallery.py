#!/usr/bin/env python3
"""Build an illustrative Fresh B gallery from GT-only, fixed-stratum picks."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from recompute_paired_rgb_metrics import load_json, reconstruct_target, sha256_file, write_csv


HERE = Path(__file__).resolve().parent
FRESHB_ROOT = Path("/4T/CXY/MV-Painter/final/round2/scientific_validation_v3")
RUN = FRESHB_ROOT / "formal/campaign_FRESH_CONFIRM_B_20261005"
MANIFEST = FRESHB_ROOT / "fresh_confirm_b/FRESH_CONFIRM_B_MANIFEST.json"
OUTPUT_PDF = HERE / "B_FAILURE_AND_SUCCESS_GALLERY.pdf"
OUTPUT_SELECTION = HERE / "B_GALLERY_SELECTION.csv"
OUTPUT_RULE = HERE / "B_GALLERY_SELECTION_RULE.json"


def load_table(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def save_panel(rgb_tensor, path: Path) -> None:
    rgb = rgb_tensor.permute(1, 2, 0).cpu().numpy()
    array = np.floor(np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(array, "RGB").save(path, compress_level=6)


def main() -> None:
    wide = [r for r in load_table(HERE / "B_OBJECT_LEVEL_RESULTS.csv")]
    lap = np.asarray([float(r["gt_fg_lap_var"]) for r in wide])
    cutpoints = np.quantile(lap, [0.25, 0.50, 0.75])
    for row in wide:
        row["quartile"] = int(np.digitize(float(row["gt_fg_lap_var"]), cutpoints)) + 1

    picks = []
    for quartile in (1, 3, 4):
        subset = [r for r in wide if int(r["quartile"]) == quartile]
        center = float(np.median([float(r["gt_fg_lap_var"]) for r in subset]))
        pick = min(subset, key=lambda r: (abs(float(r["gt_fg_lap_var"]) - center), r["uid"]))
        picks.append((quartile, pick))

    render_objects = {obj["source_uid"]: obj for obj in load_json(MANIFEST)["objects"]}
    selection_rows = []
    gt_dir = HERE / "B_GALLERY_GT_PANELS"
    gt_dir.mkdir(exist_ok=True)
    page_size = letter
    pdf = canvas.Canvas(str(OUTPUT_PDF), pagesize=page_size, pageCompression=1)

    for quartile, row in picks:
        uid = row["uid"]
        obj = render_objects[uid]
        gt_tensor, mask, target_views, reverse, source_digest = reconstruct_target(Path(obj["render_root"]))
        gt_panel = gt_dir / f"{uid}_gt_panel.png"
        save_panel(gt_tensor, gt_panel)
        panels = [
            ("GT", gt_panel, sha256_file(gt_panel)),
            ("GFL", Path(row["gfl_prediction_png"]), row["gfl_prediction_sha256"]),
            ("LLH", Path(row["llh_prediction_png"]), row["llh_prediction_sha256"]),
        ]
        for label, path, expected_sha in panels:
            if not path.is_file() or sha256_file(path) != expected_sha:
                raise ValueError(f"Fresh B gallery image hash mismatch: {uid}/{label}")

        selection_rows.append({
            "scope": "illustrative only; not an inferential sample",
            "selection_rule": "nearest GT-only Laplacian-variance median in fixed Fresh B Q1, Q3, or Q4; UID ascending tie-break",
            "quartile": quartile,
            "uid": uid,
            "object_idx": row["object_idx"],
            "object_seed": row["object_seed"],
            "gt_fg_lap_var": row["gt_fg_lap_var"],
            "target_view_ids": row["target_view_ids"],
            "reverse_view_rotation": row["reverse_view_rotation"],
            "gt_selected_source_files_digest_sha256": source_digest,
            "gt_panel_png": str(gt_panel),
            "gt_panel_sha256": sha256_file(gt_panel),
            "gfl_prediction_png": str(Path(row["gfl_prediction_png"]).resolve()),
            "gfl_prediction_sha256": row["gfl_prediction_sha256"],
            "llh_prediction_png": str(Path(row["llh_prediction_png"]).resolve()),
            "llh_prediction_sha256": row["llh_prediction_sha256"],
            "delta_llh_minus_gfl_ciede2000": row["delta_llh_minus_gfl_fg_ciede2000_rgb"],
            "delta_llh_minus_gfl_fg_psnr_db": row["delta_llh_minus_gfl_fg_psnr_recorded"],
            "delta_llh_minus_gfl_fg_lpips": row["delta_llh_minus_gfl_fg_lpips_recorded"],
            "delta_llh_minus_gfl_gt_relative_laplacian_error": row["delta_llh_minus_gfl_gt_relative_laplacian_error_rgb"],
            "checkpoint_sha256": row["checkpoint_sha256"],
            "runner_sha256_gfl": row["runner_sha256_gfl"],
            "runner_sha256_llh": row["runner_sha256_llh"],
            "target_tensor_sha256_logged": row["target_tensor_sha256_logged"],
        })

        pdf.setFont("Helvetica-Bold", 15)
        pdf.drawString(24, 760, f"Fresh B illustrative pair — GT texture quartile Q{quartile}")
        pdf.setFont("Helvetica", 8.5)
        pdf.drawString(24, 743, f"UID {uid} | idx {row['object_idx']} | seed {row['object_seed']} | GT LapVar {float(row['gt_fg_lap_var']):.6f}")
        pdf.drawString(24, 730, "Selected before image inspection by GT-only stratum rule; display is an illustration, not a subgroup estimate.")
        panel_y, panel_h, gap = 470, 170, 12
        panel_w = (page_size[0] - 48 - 2 * gap) / 3
        for i, (label, path, _) in enumerate(panels):
            x = 24 + i * (panel_w + gap)
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(x, panel_y + panel_h + 8, label)
            pdf.drawImage(ImageReader(str(path)), x, panel_y, width=panel_w, height=panel_h, preserveAspectRatio=True, anchor="c", mask="auto")
            pdf.setFont("Helvetica", 6.8)
            pdf.drawString(x, panel_y - 10, f"SHA-256 {sha256_file(path)[:16]}…")
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(24, 438, "LLH − GFL paired endpoint deltas")
        pdf.setFont("Helvetica", 9)
        pdf.drawString(24, 420, f"FG-CIEDE2000: {float(row['delta_llh_minus_gfl_fg_ciede2000_rgb']):+.3f}  |  FG-PSNR: {float(row['delta_llh_minus_gfl_fg_psnr_recorded']):+.3f} dB")
        pdf.drawString(24, 405, f"FG-LPIPS: {float(row['delta_llh_minus_gfl_fg_lpips_recorded']):+.4f}  |  GT-relative Laplacian error: {float(row['delta_llh_minus_gfl_gt_relative_laplacian_error_rgb']):+.5f}")
        pdf.setFont("Helvetica", 8)
        pdf.drawString(24, 375, "Lower is better for CIEDE2000, LPIPS, and GT-relative Laplacian error; higher is better for PSNR.")
        pdf.drawString(24, 360, "All panels use the same six target views and unmodified frozen PNG outputs. No GT-based recoloring or correction is applied.")
        pdf.drawString(24, 345, f"GT source-view IDs: {row['target_view_ids']} | reverse rotation: {reverse}")
        pdf.drawString(24, 330, f"Prediction hashes and target tensor identity are listed in {OUTPUT_SELECTION.name}.")
        pdf.showPage()

    pdf.save()
    write_csv(OUTPUT_SELECTION, selection_rows)
    OUTPUT_RULE.write_text(json.dumps({
        "selection_protocol": "FreshB descriptive gallery, no inferential use",
        "selection_rule": "For Q1, Q3, Q4 under the Fresh B frozen-cohort GT Laplacian-variance quartiles, choose the object nearest that quartile's median GT Laplacian variance; break ties by ascending UID. No generated RGB or outcome metric is used to choose objects.",
        "fixed_cutpoints": cutpoints.tolist(),
        "selected_uids_by_quartile": {f"Q{q}": r["uid"] for q, r in picks},
        "output_pdf": str(OUTPUT_PDF),
        "source_image_policy": "Original saved prediction PNGs and white-composited target panels reconstructed with the frozen six-view protocol; only PDF display scaling is applied.",
    }, indent=2) + "\n")
    print(json.dumps({"pages": len(picks), "output_pdf": str(OUTPUT_PDF), "selection_csv": str(OUTPUT_SELECTION), "rule": str(OUTPUT_RULE)}, indent=2))


if __name__ == "__main__":
    main()
