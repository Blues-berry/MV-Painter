#!/usr/bin/env python3
"""Summarize the locked same-noise color intervention without mixing runs."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
RUN = HERE / "runs/phase_b"
LOCK = HERE / "protocol/B_PROTOCOL_LOCK.json"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows to write: {path}")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def float_or_none(value: str | None) -> float | None:
    return None if value in (None, "", "nan", "None") else float(value)


def check_shared_inputs(rows: list[dict[str, str]], uid: str) -> dict:
    records = [r for r in rows if r["uid"] == uid]
    keys = ("initial_latent_sha256", "geometry_feature_sha256", "posterior_rng_before_sha256")
    results = {}
    for key in keys:
        vals = {r[key] for r in records}
        results[key] = {"unique_values": len(vals), "shared": len(vals) == 1, "values": sorted(vals)}
    return results


def object_direction_response(group: list[dict[str, str]]) -> dict:
    input_da = float(group[0]["effective_input_delta_a_star"])
    input_db = float(group[0]["effective_input_delta_b_star"])
    input_norm = float(np.hypot(input_da, input_db))
    if input_norm <= 1e-8:
        raise ValueError("perturbation arm has zero effective Lab displacement")
    projections = np.asarray([float(r["response_projection_on_input_direction"]) for r in group])
    magnitudes = projections * input_norm
    return {
        "input_delta_a_star": input_da,
        "input_delta_b_star": input_db,
        "source_projection": float(projections[0]),
        "source_response_magnitude_lab": float(magnitudes[0]),
        "source_directional_pass": bool(projections[0] > 0 and magnitudes[0] > 1.0),
        "unseen_directional_views_n": int(np.sum(projections[1:] > 0)),
        "unseen_mean_projection": float(projections[1:].mean()),
        "unseen_mean_response_magnitude_lab": float(magnitudes[1:].mean()),
        "unseen_directional_pass": bool(np.sum(projections[1:] > 0) >= 4 and magnitudes[1:].mean() > 1.0),
        "unseen_output_delta_a_star": float(np.mean([float(r["output_delta_a_star_vs_gfl"]) for r in group[1:]])),
        "unseen_output_delta_b_star": float(np.mean([float(r["output_delta_b_star_vs_gfl"]) for r in group[1:]])),
    }


def main() -> None:
    manifest = json.loads((RUN / "run_manifest.json").read_text())
    runtime = json.loads((RUN / "runtime.json").read_text())
    if manifest.get("status") != "complete" or manifest.get("gpu_generation_count") != 64:
        raise RuntimeError("Phase B manifest is not the complete locked 64-call run")
    rows = read_rows(RUN / "COLOR_INTERVENTION_RESULTS.csv")
    if len(rows) != 64 * 6:
        raise RuntimeError(f"expected 384 per-view records for 64 calls, found {len(rows)}")

    uids = sorted({r["uid"] for r in rows})
    if len(uids) != 4:
        raise RuntimeError(f"expected four development objects, found {len(uids)}")
    shared = {uid: check_shared_inputs(rows, uid) for uid in uids}
    all_shared = all(v[k]["shared"] for v in shared.values()
                     for k in ("initial_latent_sha256", "geometry_feature_sha256", "posterior_rng_before_sha256"))

    conditions = {(r["uid"], r["condition"]): [] for r in rows}
    for row in rows:
        conditions[(row["uid"], row["condition"])].append(row)
    long_rows = []
    responses = {}
    for (uid, condition), group in sorted(conditions.items()):
        if len(group) != 6:
            raise ValueError(f"{uid}/{condition}: expected six view rows, found {len(group)}")
        arm = group[0]["arm"]
        da = float(group[0]["requested_input_delta_a_star"])
        db = float(group[0]["requested_input_delta_b_star"])
        if arm in {"vae_only", "embedding_only", "vae_and_embedding"}:
            response = object_direction_response(group)
            responses[(uid, arm, da, db)] = response
        else:
            response = {}
        for row in group:
            long_rows.append({
                "uid": uid,
                "condition": condition,
                "arm": arm,
                "requested_input_delta_a_star": da,
                "requested_input_delta_b_star": db,
                "effective_input_delta_a_star": row["effective_input_delta_a_star"],
                "effective_input_delta_b_star": row["effective_input_delta_b_star"],
                "view_idx": row["target_tile_index"],
                "target_view_id": row["target_view_id"],
                "is_source_view": row["is_source_view"],
                "output_delta_a_star": row["output_delta_a_star_vs_gfl"],
                "output_delta_b_star": row["output_delta_b_star_vs_gfl"],
                "response_projection": row["response_projection_on_input_direction"],
                "response_magnitude_lab": (
                    float(row["response_projection_on_input_direction"])
                    * float(np.hypot(float(row["effective_input_delta_a_star"]),
                                     float(row["effective_input_delta_b_star"])))
                ),
                "ciede_delta_to_gt": row["delta_ciede2000_vs_gt"],
                "lstar_ssim_vs_gfl": row["foreground_lstar_ssim_vs_gfl"],
                "geometry_feature_sha256": row["geometry_feature_sha256"],
                "initial_latent_sha256": row["initial_latent_sha256"],
                "posterior_rng_before_sha256": row["posterior_rng_before_sha256"],
                "posterior_noise_sha256": row["posterior_noise_sha256"],
                "prediction_png": row["prediction_png"],
                "prediction_png_sha256": row["prediction_png_sha256"],
            })
    write_rows(RUN / "B_CHANNEL_ABLATION_RESULTS.csv", long_rows)

    channel_results = []
    gate = json.loads(LOCK.read_text())["channel_control_rule"]
    gate_text = "locked rule: directional response on >=3/4 objects for both signs; unseen view response on >=4/5 views; output magnitude >1 Lab per 6-unit input"
    for arm in ("vae_only", "embedding_only", "vae_and_embedding"):
        for axis, directions in (("a", ((6.0, 0.0), (-6.0, 0.0))),
                                 ("b", ((0.0, 6.0), (0.0, -6.0)))):
            for requested in directions:
                selected = [responses[(uid, arm, *requested)] for uid in uids]
                source_pass = sum(x["source_directional_pass"] for x in selected)
                unseen_pass = sum(x["unseen_directional_pass"] for x in selected)
                channel_results.append({
                    "arm": arm,
                    "axis": axis,
                    "requested_sign": 1 if requested[0] + requested[1] > 0 else -1,
                    "requested_delta_a_star": requested[0],
                    "requested_delta_b_star": requested[1],
                    "source_objects_pass_n": source_pass,
                    "unseen_objects_pass_n": unseen_pass,
                    "source_mean_response_lab": float(np.mean([x["source_response_magnitude_lab"] for x in selected])),
                    "unseen_mean_response_lab": float(np.mean([x["unseen_mean_response_magnitude_lab"] for x in selected])),
                    "source_rule_pass": source_pass >= 3,
                    "unseen_rule_pass": unseen_pass >= 3,
                    "gate": gate_text,
                })
    write_rows(RUN / "B_CHANNEL_RESPONSE_RULE.csv", channel_results)

    axis_verdicts = {}
    for arm in ("vae_only", "embedding_only"):
        for axis in ("a", "b"):
            pair = [r for r in channel_results if r["arm"] == arm and r["axis"] == axis]
            axis_verdicts[f"{arm}_{axis}"] = {
                "both_signs_source_pass": all(r["source_rule_pass"] for r in pair),
                "both_signs_unseen_pass": all(r["unseen_rule_pass"] for r in pair),
                "source_identified": all(r["source_rule_pass"] for r in pair),
                "unseen_identified": all(r["unseen_rule_pass"] for r in pair),
            }
    result = {
        "protocol_sha256": manifest["protocol_sha256"],
        "run_manifest_sha256": __import__("hashlib").sha256((RUN / "run_manifest.json").read_bytes()).hexdigest(),
        "runtime_sha256": manifest["runtime_sha256"],
        "generation_calls": manifest["gpu_generation_count"],
        "generation_wall_seconds": manifest["gpu_generation_wall_seconds"],
        "source_set": uids,
        "shared_factor_checks": shared,
        "all_shared_factors_match_within_object": all_shared,
        "directional_response": axis_verdicts,
        "both_appearance_channels_fail_all_unseen_axes": all(
            not v["unseen_identified"] for v in axis_verdicts.values()
        ),
        "interpretation_limit": "A repeatable output response identifies a causal color control channel. It does not by itself demonstrate correction toward GT or validate a repair.",
    }
    (RUN / "B_CAUSAL_ANALYSIS.json").write_text(json.dumps(result, indent=2) + "\n")

    _plot_responses(responses, uids)
    _write_reports(result, channel_results)
    print(json.dumps({"status": "complete", "all_shared_factors_match": all_shared,
                      "channel_results": str((RUN / 'B_CHANNEL_RESPONSE_RULE.csv').resolve()),
                      "verdict": str((RUN / 'B_CAUSAL_VERDICT.md').resolve())}, indent=2))


def _plot_responses(responses: dict, uids: list[str]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, (axis, arms, signs) in zip(axes.flat, (
        ("a*", ("vae_only", "embedding_only", "vae_and_embedding"), (6.0, 0.0)),
        ("a*", ("vae_only", "embedding_only", "vae_and_embedding"), (-6.0, 0.0)),
        ("b*", ("vae_only", "embedding_only", "vae_and_embedding"), (0.0, 6.0)),
        ("b*", ("vae_only", "embedding_only", "vae_and_embedding"), (0.0, -6.0)),
    )):
        da, db = signs
        for arm in arms:
            vals = [responses[(uid, arm, da, db)]["unseen_mean_response_magnitude_lab"] for uid in uids]
            ax.scatter([arm] * len(vals), vals, alpha=0.8)
            ax.plot([arm], [float(np.mean(vals))], marker="_", markersize=20, color="black")
        ax.axhline(1.0, color="gray", linestyle="--", linewidth=1)
        ax.set_ylabel("Mean aligned response on five unseen views (Lab)")
        ax.set_title(f"Input {axis} shift {da:+g} a*, {db:+g} b*")
        ax.tick_params(axis="x", rotation=15)
        ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(RUN / "B_COLOR_RESPONSE_CURVES.pdf", bbox_inches="tight")
    plt.close(fig)


def _write_reports(result: dict, channel_rows: list[dict]) -> None:
    lines = [
        "# Phase B color-response intervention",
        "",
        f"Generation calls: {result['generation_calls']}; measured sampler wall time: {result['generation_wall_seconds']:.1f} s.",
        "The four locked development objects and all 64 conditions use the same checkpoint, geometry, object order, initial latent, scheduler, and posterior RNG seed.",
        "",
        "## Shared-factor integrity",
        "",
        f"All per-object initial-latent, geometry-feature, and pre-posterior RNG hashes agree across conditions: **{result['all_shared_factors_match_within_object']}**.",
        "",
        "## Directional response by appearance channel",
        "",
        "| Arm | Axis | Sign | Source pass (objects) | Unseen pass (objects) | Mean unseen aligned response (Lab) |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in channel_rows:
        lines.append(
            f"| {row['arm']} | {row['axis']}* | {row['requested_sign']:+d} | "
            f"{row['source_objects_pass_n']}/4 | {row['unseen_objects_pass_n']}/4 | "
            f"{row['unseen_mean_response_lab']:.3f} |"
        )
    lines.extend([
        "",
        "The locked response criterion is shown with the result CSV. A response is evidence of causal color control only; it is not evidence that the shift reduces GT-relative color error.",
        "",
        "## Cache-refresh control",
        "",
        "Compare `global_embedding_recomputed` against `gfl_baseline` in the paired CSV. It isolates current-condition cache refresh from the color-direction arms and must not be merged with them.",
    ])
    (RUN / "B_COLOR_RESPONSE_INTERVENTION.md").write_text("\n".join(lines) + "\n")

    verdict_lines = [
        "# Phase B causal verdict",
        "",
        f"Shared-factor identity within each object: **{'PASS' if result['all_shared_factors_match_within_object'] else 'FAIL'}**.",
        "",
        "## Channel-level calls",
        "",
    ]
    for name, verdict in result["directional_response"].items():
        verdict_lines.append(
            f"- `{name}`: source response {'identified' if verdict['source_identified'] else 'not identified'}; "
            f"unseen-view response {'identified' if verdict['unseen_identified'] else 'not identified'}."
        )
    verdict_lines.extend([
        "",
        "A positive response is not a repair result. It only establishes that an input appearance channel can move generated chroma under the locked same-noise comparison.",
        "",
        "## Repair gate",
        "",
        "Proceed with the locked C1 development trial only if at least one appearance channel shows repeatable directional response on the five unseen views. Otherwise C1 is a prespecified falsification check and must not proceed to Fresh B.",
    ])
    (RUN / "B_CAUSAL_VERDICT.md").write_text("\n".join(verdict_lines) + "\n")


if __name__ == "__main__":
    main()
