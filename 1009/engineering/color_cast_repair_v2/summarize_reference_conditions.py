#!/usr/bin/env python3
"""Object-paired comparison of Phase B reference conditions, using dev outputs only."""

from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from pathlib import Path
from statistics import mean

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
RUN = HERE / "runs/phase_b"
INPUT = RUN / "COLOR_INTERVENTION_RESULTS.csv"
CONDITIONS = ("gfl_baseline", "global_embedding_recomputed", "no_adapter", "layer_llh")


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    rows = read_rows(INPUT)
    if len(rows) != 384 or len({row["uid"] for row in rows}) != 4:
        raise ValueError(f"unexpected Phase B result shape: rows={len(rows)}")
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["uid"], row["condition"])].append(row)

    output = []
    object_ids = sorted({row["uid"] for row in rows})
    for uid in object_ids:
        baseline = sorted(grouped[(uid, "gfl_baseline")], key=lambda row: int(row["target_tile_index"]))
        if len(baseline) != 6:
            raise ValueError(f"{uid}: expected six baseline views")
        source_indexes = [i for i, row in enumerate(baseline) if row["is_source_view"] == "True"]
        if len(source_indexes) != 1:
            raise ValueError(f"{uid}: expected one source view")
        source_index = source_indexes[0]
        unseen_indexes = [i for i in range(6) if i != source_index]
        baseline_path = Path(baseline[0]["prediction_png"])
        baseline_sha = baseline[0]["prediction_png_sha256"]
        if sha_file(baseline_path) != baseline_sha:
            raise ValueError(f"{uid}: baseline PNG SHA mismatch")
        baseline_rgb = np.asarray(Image.open(baseline_path).convert("RGB"), dtype=np.int16)

        for condition in CONDITIONS:
            current = sorted(grouped[(uid, condition)], key=lambda row: int(row["target_tile_index"]))
            if len(current) != 6:
                raise ValueError(f"{uid}/{condition}: expected six views")
            for old, new in zip(baseline, current):
                for key in ("initial_latent_sha256", "geometry_feature_sha256", "posterior_rng_before_sha256"):
                    if old[key] != new[key]:
                        raise ValueError(f"{uid}/{condition}: shared factor differs: {key}")
            image_path = Path(current[0]["prediction_png"])
            image_sha = current[0]["prediction_png_sha256"]
            if sha_file(image_path) != image_sha:
                raise ValueError(f"{uid}/{condition}: prediction PNG SHA mismatch")
            current_rgb = np.asarray(Image.open(image_path).convert("RGB"), dtype=np.int16)
            if current_rgb.shape != baseline_rgb.shape:
                raise ValueError(f"{uid}/{condition}: prediction grid shape changed")
            difference = np.abs(current_rgb - baseline_rgb)
            source = current[source_index]
            unseen = [current[i] for i in unseen_indexes]
            output.append({
                "uid": uid,
                "cohort": current[0]["cohort"],
                "condition": condition,
                "source_view_id": source["target_view_id"],
                "source_ciede2000_vs_gt": float(source["condition_ciede2000_vs_gt"]),
                "source_delta_ciede2000_vs_gfl": float(source["delta_ciede2000_vs_gt"]),
                "unseen_mean_ciede2000_vs_gt": mean(float(row["condition_ciede2000_vs_gt"]) for row in unseen),
                "unseen_mean_delta_ciede2000_vs_gfl": mean(float(row["delta_ciede2000_vs_gt"]) for row in unseen),
                "unseen_mean_output_delta_a_star": mean(float(row["output_delta_a_star_vs_gfl"]) for row in unseen),
                "unseen_mean_output_delta_b_star": mean(float(row["output_delta_b_star_vs_gfl"]) for row in unseen),
                "unseen_mean_abs_delta_l_star": mean(float(row["mean_abs_delta_l_star_vs_gfl"]) for row in unseen),
                "unseen_mean_lstar_ssim_vs_gfl": mean(float(row["foreground_lstar_ssim_vs_gfl"]) for row in unseen),
                "cache_recompute_max_abs_delta": float(source["cache_recompute_max_abs_delta"]),
                "cache_recompute_identity_within_0p03": source["cache_recompute_identity_within_0p03"],
                "prediction_png": str(image_path),
                "prediction_png_sha256": image_sha,
                "rgb_mae_vs_gfl_0_255": float(difference.mean()),
                "changed_rgb_pixel_fraction_vs_gfl": float(np.any(difference > 0, axis=2).mean()),
                "max_channel_difference_vs_gfl": int(difference.max()),
                "shared_factors_match": True,
            })

    out = RUN / "B_REFERENCE_CONDITION_COMPARISON.csv"
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)

    lines = [
        "# Phase B reference-condition comparison",
        "",
        "Object-paired analysis of the four locked development objects; each unseen-view value equally averages five views.",
        "The RGB difference is a descriptive full-grid uint8 comparison against the same object's GFL PNG, not a GT quality metric.",
        "No Fresh B prediction or repair metric is read.",
        "",
        "| Condition vs GFL | Mean unseen ΔCIEDE2000 | Object wins / losses | Mean unseen L* SSIM vs GFL | Mean RGB MAE |",
        "|---|---:|---:|---:|---:|",
    ]
    for condition in CONDITIONS:
        selected = [row for row in output if row["condition"] == condition]
        deltas = [row["unseen_mean_delta_ciede2000_vs_gfl"] for row in selected]
        wins = sum(value < 0 for value in deltas)
        losses = sum(value > 0 for value in deltas)
        lines.append(
            f"| {condition} | {mean(deltas):+.3f} | {wins} / {losses} | "
            f"{mean(row['unseen_mean_lstar_ssim_vs_gfl'] for row in selected):.3f} | "
            f"{mean(row['rgb_mae_vs_gfl_0_255'] for row in selected):.3f} |"
        )
    lines.extend([
        "",
        "## Interpretation limits",
        "",
        "No Adapter has a large CIEDE2000 penalty relative to GFL on these four objects, but its geometry is substantially different; this does not isolate a pure adapter-induced color cast.",
        "LLH changes lightness/structure strongly and has mixed object-level color effects. These locked readouts do not establish a fine-detail benefit.",
        "Recomputing the global embedding changes the two Fig. 4 failure outputs in opposite GT-relative directions, while the two Fresh C development outputs are pixel-identical to GFL. This shows the cached-vs-current embedding can causally affect failure outputs, but the effect is not a consistent correction.",
        "",
        f"Source CSV SHA-256: `{sha_file(INPUT)}`.",
    ])
    (RUN / "B_REFERENCE_CONDITION_COMPARISON.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {out} with {len(output)} object-condition rows")


if __name__ == "__main__":
    main()
