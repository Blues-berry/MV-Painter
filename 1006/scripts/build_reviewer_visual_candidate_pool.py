#!/usr/bin/env python3
"""Index Fresh C image outputs and freeze rights-cleared visual candidates."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np


EXPECTED_N = 300
VIEWS = (0, 15, 12, 16, 13, 14)
METHODS = {
    "no_adapter": ("No adapter", "c3_confirmation"),
    "native_gfl": ("GFL", "c3_confirmation"),
    "native_gfh": ("GFH", "c3_confirmation"),
    "native_gc3": ("C3", "c3_confirmation"),
    "layer_llh": ("LLH", "revision_era_addendum"),
    "gen_linear": ("Generic linear", "revision_era_addendum"),
}
METRICS = (
    "fg_psnr", "fg_ssim", "fg_lpips", "full_psnr", "full_ssim", "full_lpips", "edge_ssim"
)
CONTRASTS = {
    "C3_GFL": ("native_gc3", "native_gfl"),
    "C3_GFH": ("native_gc3", "native_gfh"),
    "LLH_C3": ("layer_llh", "native_gc3"),
    "LLH_GFL": ("layer_llh", "native_gfl"),
    "LLH_linear": ("layer_llh", "gen_linear"),
    "C3_linear": ("native_gc3", "gen_linear"),
    "linear_GFL": ("gen_linear", "native_gfl"),
}
LOWER_IS_BETTER = {"fg_lpips", "full_lpips"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fieldnames or (list(rows[0]) if rows else [])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def stable_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True, help="Workspace containing frozen Fresh C outputs")
    parser.add_argument("--review-root", type=Path, default=Path(__file__).resolve().parents[1] / "review")
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    review_root = args.review_root.resolve()
    data = source_root / "1006/data/fresh_c"
    gallery = source_root / "1006/figures/strategy_comparison_gallery/fresh_c_final"
    rights_path = source_root / "1006/evidence/audits/FRESH_C_IMAGE_COHORT_ASSET_RIGHTS_20261007.csv"
    attribution_path = source_root / "1006/evidence/audits/FRESH_C_ATLAS_ATTRIBUTION_20261007.csv"
    primary_gate_path = data / "FRESH_C_INTEGRITY_GATE.json"
    addendum_gate_path = data / "FRESH_C_ADDENDUM_INTEGRITY_GATE.json"
    primary_metrics_path = data / "runs/c3_confirmation/per_object_metrics.csv"
    addendum_metrics_path = data / "runs/revision_era_addendum/per_object_metrics.csv"
    primary_hashes_path = data / "runs/c3_confirmation/OUTPUT_FILE_SHA256.csv"
    addendum_hashes_path = data / "runs/revision_era_addendum/OUTPUT_FILE_SHA256.csv"
    cohort_path = data / "fresh_c_objects.txt"
    gallery_manifest_path = gallery / "gallery_manifest.json"
    gallery_asset_manifest_path = gallery / "gallery_asset_sha256.csv"
    gallery_selected_path = gallery / "selected_20_uid_index.csv"
    reference_root = data / "renders"

    required = [
        primary_gate_path, addendum_gate_path, primary_metrics_path, addendum_metrics_path,
        primary_hashes_path, addendum_hashes_path, cohort_path, rights_path,
        attribution_path, gallery_manifest_path, gallery_asset_manifest_path,
        gallery_selected_path,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    checks: list[dict[str, Any]] = [{
        "check": "required_source_files", "status": "PASS" if not missing else "FAIL", "detail": missing
    }]
    if missing:
        raise SystemExit("Missing visual candidate sources: " + ", ".join(missing))

    primary_gate = read_json(primary_gate_path)
    addendum_gate = read_json(addendum_gate_path)
    gallery_manifest = read_json(gallery_manifest_path)
    checks.append({"check": "fresh_c_primary_integrity_gate", "status": "PASS" if primary_gate.get("status") == "PASS" else "FAIL", "detail": primary_gate.get("status")})
    checks.append({"check": "fresh_c_addendum_integrity_gate", "status": "PASS" if addendum_gate.get("status") == "PASS" else "FAIL", "detail": addendum_gate.get("status")})
    if primary_gate.get("status") != "PASS" or addendum_gate.get("status") != "PASS":
        raise SystemExit("Both existing Fresh C integrity gates must pass before indexing visual candidates")

    source_uids = [line.strip() for line in cohort_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    uid_set = set(source_uids)
    if len(source_uids) != EXPECTED_N or len(uid_set) != EXPECTED_N:
        raise SystemExit(f"Frozen cohort list expected {EXPECTED_N} unique UIDs; got {len(source_uids)} rows / {len(uid_set)} unique")

    primary = pd.read_csv(primary_metrics_path)
    addendum = pd.read_csv(addendum_metrics_path)
    expected_primary_conditions = {"no_adapter", "native_gfl", "native_gfh", "native_gc3"}
    expected_addendum_conditions = {"layer_llh", "gen_linear"}
    if len(primary) != 4 * EXPECTED_N or set(primary.condition.unique()) != expected_primary_conditions:
        raise SystemExit("Fresh C primary metrics do not contain the four expected conditions × 300 rows")
    if len(addendum) != 2 * EXPECTED_N or set(addendum.condition.unique()) != expected_addendum_conditions:
        raise SystemExit("Fresh C addendum metrics do not contain LLH and generic linear × 300 rows")
    all_metrics = pd.concat([primary, addendum], ignore_index=True)
    if all_metrics.duplicated(["condition", "object_uid"]).any():
        raise SystemExit("Duplicate condition × UID metric row found")
    prediction_manifest_rows = [
        row for path in (primary_hashes_path, addendum_hashes_path)
        for row in read_csv(path) if row.get("kind") == "prediction"
    ]
    prediction_manifest = {(row["condition"], row["uid"]): row for row in prediction_manifest_rows}
    expected_prediction_keys = {(method, uid) for method in METHODS for uid in uid_set}
    if len(prediction_manifest) != len(prediction_manifest_rows) or set(prediction_manifest) != expected_prediction_keys:
        raise SystemExit("Prediction output manifests do not contain one entry for every expected method × UID")
    prediction_manifest_checks = 0
    for method in METHODS:
        method_rows = all_metrics[all_metrics.condition == method]
        if len(method_rows) != EXPECTED_N or set(method_rows.object_uid.astype(str)) != uid_set:
            raise SystemExit(f"{method}: expected the exact frozen 300-UID set")
        numeric_metrics = method_rows[list(METRICS)].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
        if not np.isfinite(numeric_metrics).all():
            raise SystemExit(f"{method}: required metrics contain missing, non-numeric, or non-finite values")

    # The existing primary/addendum integrity records bind these exact tables and image manifests.
    gate_hash_checks = [
        ("primary_metrics_hash", primary_gate.get("combined_csv_sha256"), sha256_file(primary_metrics_path)),
        ("primary_output_hash_manifest", primary_gate.get("output_hash_manifest_sha256"), sha256_file(primary_hashes_path)),
        ("addendum_metrics_hash", addendum_gate.get("combined_csv_sha256"), sha256_file(addendum_metrics_path)),
        ("addendum_output_hash_manifest", addendum_gate.get("output_hash_manifest_sha256"), sha256_file(addendum_hashes_path)),
    ]
    for name, expected, observed in gate_hash_checks:
        checks.append({"check": name, "status": "PASS" if expected == observed else "FAIL", "detail": {"expected": expected, "observed": observed}})
        if expected != observed:
            raise SystemExit(f"Source hash mismatch for {name}")

    rights_rows = read_csv(rights_path)
    rights_by_uid = {str(row["asset_uid"]): row for row in rights_rows}
    if len(rights_by_uid) != EXPECTED_N or set(rights_by_uid) != uid_set:
        raise SystemExit("Rights inventory does not exactly cover the frozen 300-object cohort")

    selected_rows = read_csv(gallery_selected_path)
    panel_rows = {str(row["object_uid"]): row for row in selected_rows}
    if len(panel_rows) != 20 or len(selected_rows) != 20:
        raise SystemExit(f"Expected 20 pre-generated gallery panels; found {len(selected_rows)} rows / {len(panel_rows)} unique UIDs")
    if gallery_manifest.get("status") != "FINAL_GALLERY_BUILT_AFTER_BOTH_INTEGRITY_GATES":
        raise SystemExit("The existing Fresh C six-strategy gallery did not record both gates passing")
    panel_hashes = {item["path"]: item["sha256"] for item in gallery_manifest.get("generated_file_hashes", [])}
    rights_eligible = {
        uid for uid, row in rights_by_uid.items()
        if row.get("final_disposition") == "FIGURE_ONLY"
        and row.get("publication_figure_allowed") == "YES_WITH_ATTRIBUTION"
        and row.get("anonymous_supplement_release_allowed") == "YES_WITH_ATTRIBUTION"
    }
    if set(panel_rows) != rights_eligible:
        raise SystemExit("Existing gallery panels do not exactly match the 20 currently figure-eligible Fresh C assets")

    metric_wide = all_metrics.set_index(["object_uid", "condition"])
    uid_to_index = {}
    for row in all_metrics.itertuples():
        prior = uid_to_index.setdefault(str(row.object_uid), int(row.object_idx))
        if prior != int(row.object_idx):
            raise SystemExit(f"Object index mismatch across methods for UID {row.object_uid}")

    curation_order = [str(row["object_uid"]) for row in selected_rows]
    if [int(row["panel_order"]) for row in selected_rows] != list(range(1, 21)):
        raise SystemExit("The existing gallery must have a unique contiguous panel order 1–20")
    def uid_at(order: int) -> str:
        return curation_order[order - 1]
    # This screening checks the two reviewer-relevant endpoints separately; it does not combine them.
    c3_gfh_full = {
        uid: float(metric_wide.loc[(uid, "native_gc3"), "full_psnr"] - metric_wide.loc[(uid, "native_gfh"), "full_psnr"])
        for uid in curation_order
    }
    c3_gfh_edge = {
        uid: float(metric_wide.loc[(uid, "native_gc3"), "edge_ssim"] - metric_wide.loc[(uid, "native_gfh"), "edge_ssim"])
        for uid in curation_order
    }
    group_a = list(curation_order)
    group_b = [uid_at(order) for order in (1, 5, 13, 2, 14, 3, 7, 8, 16, 20)]
    # Ensure each focal contrast is still the locked, two-endpoint-consistent gallery row.
    selected_by_uid = {str(row["object_uid"]): row for row in selected_rows}
    if any(uid not in selected_by_uid or not selected_by_uid[uid]["endpoint_pattern_focal_contrast"].startswith("both_endpoints_favor_") for uid in group_b):
        raise SystemExit("Metric-consistent candidate set no longer matches its recorded focal endpoint patterns")
    group_c = [uid for uid in curation_order if c3_gfh_full[uid] > 0 and c3_gfh_edge[uid] < 0][:5]
    if len(group_c) < 5:
        raise SystemExit("Fewer than five figure-eligible C3−GFH full-PSNR/Edge-SSIM trade-off examples are available")
    group_d = [uid_at(order) for order in (1, 2, 3, 7, 9, 11, 14, 18, 19, 20)]
    main_candidates = [uid_at(order) for order in (1, 2, 3, 4, 5, 7, 10, 11, 12, 16, 18, 20)]
    main_frozen = set(main_candidates[:8])
    response_candidates = [uid_at(order) for order in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20)]
    if any(uid not in panel_rows for uid in set(group_b + group_c + group_d + main_candidates + response_candidates)):
        raise SystemExit("A curated visual UID is not present in the rights-cleared pre-generated gallery")

    visual_tags: dict[str, list[str]] = {uid: ["CLEAR_IMPROVEMENT"] for uid in group_a}
    for uid in group_d:
        visual_tags[uid] = list(dict.fromkeys(visual_tags.get(uid, []) + ["STRUCTURE_IMPROVEMENT", "MATERIAL_MISMATCH"]))
    for uid in group_c:
        visual_tags[uid] = list(dict.fromkeys(visual_tags.get(uid, []) + ["TRADEOFF"]))
    for uid in (uid_at(1), uid_at(2), uid_at(7), uid_at(20)):
        visual_tags[uid] = list(dict.fromkeys(visual_tags.get(uid, []) + ["COLOR_SHIFT", "METRIC_VISUAL_DISAGREEMENT"]))
    for uid in (uid_at(3), uid_at(6), uid_at(10), uid_at(12)):
        visual_tags[uid] = list(dict.fromkeys(visual_tags.get(uid, []) + ["VISUALLY_AMBIGUOUS"]))
    notes = {
        uid_at(1): "The reference has a cool gray building appearance while adapted outputs are brown/textured; the no-adapter panel is visibly fragmented. Metric advantage in the focal contrast does not remove this visual mismatch.",
        uid_at(2): "Small bright reference objects become brown textured forms; the adapter methods are close to one another while the no-adapter panel is fragmented.",
        uid_at(3): "Bust-shaped outputs remain visually similar across adapter strategies; reference color/material differs, and the no-adapter panel is less coherent.",
        uid_at(7): "The blue/green package reference contrasts with brown adapter outputs; the no-adapter rendering has conspicuous colored structural artifacts.",
        uid_at(11): "Turtle-like shapes are visible across adapter strategies; material appearance varies, and the no-adapter rendering adds an unusual structure.",
        uid_at(20): "The gray block reference contrasts with wood-like adapter outputs; the no-adapter condition has conspicuous multicolor streaking. Generic linear remains visible as a direct baseline.",
    }
    common_note = "In this existing six-view panel, adapter-on outputs show greater object coherence than the no-adapter output. This is an illustration of the shown object and views only; it does not establish reference fidelity or a winner among adapter strategies."

    selected_by_uid = {str(row["object_uid"]): row for row in selected_rows}
    panel_source_for_uid: dict[str, Path] = {}
    for row in selected_rows:
        uid, order = str(row["object_uid"]), int(row["panel_order"])
        filename = f"panel_{order:02d}_{uid}.png"
        path = gallery / "panels" / filename
        if not path.is_file():
            raise SystemExit(f"Missing source gallery panel: {path}")
        expected_hash = panel_hashes.get(f"1006/figures/strategy_comparison_gallery/fresh_c_final/panels/{filename}")
        observed_hash = sha256_file(path)
        if expected_hash != observed_hash:
            raise SystemExit(f"Source panel hash mismatch: {path}")
        panel_source_for_uid[uid] = path

    # Build complete full-cohort rows. Restricted and unknown assets stay indexed but their images are not copied.
    index_rows: list[dict[str, Any]] = []
    for uid in source_uids:
        right = rights_by_uid[uid]
        row: dict[str, Any] = {
            "object_uid": uid,
            "object_index": uid_to_index[uid],
            "cohort": "FROZEN_FRESH_C",
            "cohort_n": EXPECTED_N,
            "asset_rights": right.get("final_disposition", "UNKNOWN"),
            "asset_license": right.get("license", ""),
            "asset_title": right.get("title", ""),
            "asset_creator": right.get("creator", ""),
            "asset_creator_username": right.get("creator_username", ""),
            "asset_source_url": right.get("original_url", ""),
            "publication_figure_allowed": right.get("publication_figure_allowed", "UNKNOWN"),
            "anonymous_supplement_release_allowed": right.get("anonymous_supplement_release_allowed", "UNKNOWN"),
            "image_copy_eligible": "YES" if uid in rights_eligible else "NO",
            "reference_view_ids": ";".join(map(str, VIEWS)),
            "visual_screen_status": "SCREENED_EXISTING_PANEL" if uid in panel_rows else "NOT_VISUALLY_SCREENED",
            "visual_panel_source": "existing Fresh C gallery; six fixed views; exact panel copy" if uid in panel_rows else "",
            "visual_panel_path": "" if uid not in panel_rows else f"1006/review/REVIEWER_VISUAL_CANDIDATE_POOL/panels/candidate_{int(selected_by_uid[uid]['panel_order']):02d}_{uid}.png",
            "visual_panel_sha256": "" if uid not in panel_rows else panel_hashes[f"1006/figures/strategy_comparison_gallery/fresh_c_final/panels/panel_{int(selected_by_uid[uid]['panel_order']):02d}_{uid}.png"],
            "gallery_panel_order": selected_by_uid[uid].get("panel_order", "") if uid in panel_rows else "",
            "focal_contrast": selected_by_uid[uid].get("focal_contrast", "") if uid in panel_rows else "",
            "selection_stratum": selected_by_uid[uid].get("selection_stratum", "") if uid in panel_rows else "",
            "delta_fg_psnr_focal_a_minus_b": selected_by_uid[uid].get("delta_fg_psnr_focal_a_minus_b", "") if uid in panel_rows else "",
            "delta_fg_lpips_focal_a_minus_b": selected_by_uid[uid].get("delta_fg_lpips_focal_a_minus_b", "") if uid in panel_rows else "",
            "focal_endpoint_pattern": selected_by_uid[uid].get("endpoint_pattern_focal_contrast", "") if uid in panel_rows else "",
            "candidate_group_A_strong_visual": uid in group_a,
            "candidate_group_B_metric_consistent": uid in group_b,
            "candidate_group_C_tradeoff": uid in group_c,
            "candidate_group_D_failure_adverse": uid in group_d,
            "main_paper_candidate": uid in main_candidates,
            "main_paper_frozen_candidate": uid in main_frozen,
            "reviewer_response_candidate": uid in response_candidates,
            "supplementary_gallery_candidate": uid in panel_rows,
            "qualitative_tags": ";".join(visual_tags.get(uid, [])),
            "qualitative_curation_note": notes.get(uid, common_note) if uid in panel_rows else "",
            "selection_role": "illustrative curation; no statistical sampling claim" if uid in panel_rows else "not selected; image rights not cleared for figure use",
        }
        for view in VIEWS:
            image_path = reference_root / uid / "image" / f"{view:03d}.png"
            if not image_path.is_file():
                raise SystemExit(f"Missing reference view {view} for {uid}")
            row[f"reference_view_{view:03d}_path"] = str(image_path)
            row[f"reference_view_{view:03d}_sha256"] = sha256_file(image_path)
        for method, (label, run_name) in METHODS.items():
            prediction = data / "runs" / run_name / "predictions" / method / f"{uid}.png"
            if not prediction.is_file():
                raise SystemExit(f"Missing generated prediction for {method}/{uid}")
            manifest_row = prediction_manifest[(method, uid)]
            prediction_hash = sha256_file(prediction)
            if int(manifest_row["bytes"]) != prediction.stat().st_size or manifest_row["sha256"] != prediction_hash:
                raise SystemExit(f"Prediction output does not match its frozen manifest entry: {method}/{uid}")
            prediction_manifest_checks += 1
            row[f"method_{method}_label"] = label
            row[f"method_{method}_prediction_path"] = str(prediction)
            row[f"method_{method}_prediction_bytes"] = prediction.stat().st_size
            row[f"method_{method}_prediction_sha256"] = prediction_hash
            metric_row = metric_wide.loc[(uid, method)]
            for metric in METRICS:
                row[f"{method}_{metric}"] = float(metric_row[metric])
        for contrast, (method_a, method_b) in CONTRASTS.items():
            for metric in METRICS:
                delta = float(metric_wide.loc[(uid, method_a), metric] - metric_wide.loc[(uid, method_b), metric])
                row[f"delta_{contrast}_{metric}"] = delta
        index_rows.append(row)

    pool_dir = review_root / "REVIEWER_VISUAL_CANDIDATE_POOL"
    panel_dir = pool_dir / "panels"
    group_dir = pool_dir / "groups"
    panel_dir.mkdir(parents=True, exist_ok=True)
    group_dir.mkdir(parents=True, exist_ok=True)
    copied_panel_hashes = {}
    for uid, source in panel_source_for_uid.items():
        order = int(selected_by_uid[uid]["panel_order"])
        destination = panel_dir / f"candidate_{order:02d}_{uid}.png"
        shutil.copy2(source, destination)
        copied_hash = sha256_file(destination)
        if copied_hash != sha256_file(source):
            raise SystemExit(f"Copied visual panel hash mismatch: {destination}")
        copied_panel_hashes[uid] = copied_hash

    # Replace candidate panel paths with paths in the current review artifact tree.
    for row in index_rows:
        uid = row["object_uid"]
        if uid in copied_panel_hashes:
            row["visual_panel_path"] = str((panel_dir / f"candidate_{int(selected_by_uid[uid]['panel_order']):02d}_{uid}.png").relative_to(review_root))
            row["visual_panel_sha256"] = copied_panel_hashes[uid]
    index_frame = pd.DataFrame(index_rows)
    if prediction_manifest_checks != len(expected_prediction_keys):
        raise SystemExit(f"Expected {len(expected_prediction_keys)} verified prediction hashes; got {prediction_manifest_checks}")
    checks.append({
        "check": "all_prediction_files_match_frozen_manifests",
        "status": "PASS",
        "detail": {"verified": prediction_manifest_checks, "expected": len(expected_prediction_keys)},
    })
    rank_columns: dict[str, pd.Series] = {}
    for contrast in CONTRASTS:
        for metric in METRICS:
            delta_column = f"delta_{contrast}_{metric}"
            ascending = metric in LOWER_IS_BETTER
            ranks = index_frame[delta_column].rank(method="average", ascending=ascending)
            rank_columns[f"rank_{contrast}_{metric}_favorability"] = ranks
            rank_columns[f"percentile_{contrast}_{metric}_favorability"] = (EXPECTED_N - ranks) / (EXPECTED_N - 1) * 100.0
    index_frame = pd.concat([index_frame, pd.DataFrame(rank_columns)], axis=1)
    index_path = review_root / "REVIEWER_VISUAL_CANDIDATE_INDEX.csv"
    write_csv(index_path, index_frame.to_dict(orient="records"))

    # Copy source selection/provenance material unchanged and include the row-level attributions.
    for source, name in (
        (gallery_manifest_path, "source_gallery_manifest.json"),
        (gallery_asset_manifest_path, "source_gallery_asset_sha256.csv"),
        (gallery_selected_path, "source_selected_20_uid_index.csv"),
        (attribution_path, "FRESH_C_ATLAS_ATTRIBUTION_20261007.csv"),
    ):
        shutil.copy2(source, pool_dir / name)

    def candidate_rows(uids: list[str], set_name: str, reasons: dict[str, str] | None = None) -> list[dict[str, Any]]:
        result = []
        for order, uid in enumerate(uids, start=1):
            row = index_frame[index_frame.object_uid == uid].iloc[0].to_dict()
            row["candidate_set"] = set_name
            row["candidate_order"] = order
            row["selection_reason"] = (reasons or {}).get(uid, "Selected qualitative illustration; not a statistical sample.")
            row["candidate_status"] = "FROZEN_CANDIDATE" if set_name != "MAIN_PAPER" or uid in main_frozen else "OPTIONAL_MAIN_CANDIDATE"
            result.append(row)
        return result

    all_main_reasons = {
        uid: "Visually legible six-view comparison with the complete method set; selection emphasizes display clarity and contrast diversity, not average-object representativeness."
        for uid in main_candidates
    }
    all_response_reasons = {
        uid: "Reviewer-facing illustration candidate retaining the reference, all six methods, and the existing fixed view set; the panel is not population evidence."
        for uid in response_candidates
    }
    supplementary_reasons = {
        uid: "Retain the full rights-cleared 20-panel atlas with its locked focal contrast and rank stratum; show favorable, ordinary, trade-off, and adverse examples without a composite winner score."
        for uid in panel_rows
    }
    write_csv(review_root / "MAIN_PAPER_VISUAL_CANDIDATES.csv", candidate_rows(main_candidates, "MAIN_PAPER", all_main_reasons))
    write_csv(review_root / "REVIEWER_RESPONSE_VISUAL_CANDIDATES.csv", candidate_rows(response_candidates, "REVIEWER_RESPONSE", all_response_reasons))
    write_csv(review_root / "SUPPLEMENTARY_VISUAL_GALLERY_CANDIDATES.csv", candidate_rows(curation_order, "SUPPLEMENTARY_GALLERY", supplementary_reasons))

    group_specs = {
        "GROUP_A_STRONG_QUALITATIVE_SUCCESS.csv": (group_a, "A_STRONG_QUALITATIVE_SUCCESS", "Clear adapter-on versus no-adapter visual contrast in these fixed views; not evidence of reference fidelity or superiority among adapter methods."),
        "GROUP_B_METRIC_CONSISTENT.csv": (group_b, "B_METRIC_CONSISTENT", "Focal contrast selected where the separately reported FG-PSNR and FG-LPIPS directions agree; no cross-endpoint score is formed."),
        "GROUP_C_TRADEOFF.csv": (group_c, "C_TRADEOFF", "For C3−GFH, the per-object Full-PSNR difference is positive while Edge-SSIM is negative; this is a two-endpoint trade-off selection rule, not a quality score."),
        "GROUP_D_FAILURE_ADVERSE.csv": (group_d, "D_FAILURE_ADVERSE", "Existing panel visibly records an adverse no-adapter output and/or a remaining reference/material mismatch; retained to expose limitations."),
    }
    group_summary = {}
    for filename, (uids, set_name, reason) in group_specs.items():
        group_reasons = {uid: reason for uid in uids}
        write_csv(group_dir / filename, candidate_rows(uids, set_name, group_reasons))
        group_summary[set_name] = {"n": len(uids), "uids": uids}

    readme = """# Fresh C reviewer visual candidate pool

This pool indexes all 300 frozen Fresh C objects and their six existing methods: no adapter, GFL, GFH, C3, LLH, and generic linear. The index records the six fixed reference views, all six existing prediction images and hashes, seven separate metric endpoints, endpoint-specific paired deltas and ranks, and the per-object rights disposition.

Only the 20 assets marked `FIGURE_ONLY` with attribution are copied into `panels/`. The other 280 objects remain in the full machine index, but their images are not copied into this candidate package. Row-level attributions are in `FRESH_C_ATLAS_ATTRIBUTION_20261007.csv`.

The 20 panels are exact copies of the already-generated Fresh C gallery panels. They retain the fixed views `0, 15, 12, 16, 13, 14`, the shared reference and six-method layout, and the source crop/normalization from the original gallery build. No diffusion was run; no prompt, seed, reference, crop, color, texture, or individual method image was changed in this step.

Group labels are qualitative curation metadata. The success group refers only to a clear visual contrast with the no-adapter condition. It does not establish reference fidelity or a winner among adapter methods. Trade-off selection uses the named Full-PSNR and Edge-SSIM endpoints separately; no cross-endpoint score is formed. No `REPEATED_PATTERN` tag was assigned because the current panels did not support a confident object-level label separate from the source geometry.

Qualitative examples illustrate selected behaviors. Quantitative conclusions remain based on the complete frozen cohort and endpoint-specific tables, intervals, medians, and favorable-object fractions.
"""
    (pool_dir / "README.md").write_text(readme, encoding="utf-8")

    audit = {
        "status": "PASS",
        "cohort": "FROZEN_FRESH_C",
        "cohort_n": EXPECTED_N,
        "method_count": len(METHODS),
        "metrics_per_method": list(METRICS),
        "reference_view_ids": list(VIEWS),
        "source_gates": {"primary": primary_gate.get("status"), "addendum": addendum_gate.get("status")},
        "rights": {"figure_eligible_copied_images": len(rights_eligible), "copied_panel_dispositions": sorted({rights_by_uid[uid]["final_disposition"] for uid in panel_rows})},
        "candidate_group_counts": {key: value["n"] for key, value in group_summary.items()},
        "candidate_sets": {"main_paper_suggestions": len(main_candidates), "main_paper_frozen": len(main_frozen), "reviewer_response": len(response_candidates), "supplementary_gallery": len(curation_order)},
        "copied_panels_exact_hash_matches": len(copied_panel_hashes),
        "prediction_manifest_entries_checked": prediction_manifest_checks,
        "qualitative_scope": "illustrative curation only; no population inference or author-rated win rate",
        "source_paths": {"source_root": str(source_root), "raw_data_dir": str(data), "gallery_dir": str(gallery), "rights_ledger": str(rights_path), "attribution": str(attribution_path)},
        "source_hashes": {
            "primary_gate_sha256": sha256_file(primary_gate_path),
            "addendum_gate_sha256": sha256_file(addendum_gate_path),
            "primary_metrics_sha256": sha256_file(primary_metrics_path),
            "addendum_metrics_sha256": sha256_file(addendum_metrics_path),
            "primary_output_hash_manifest_sha256": sha256_file(primary_hashes_path),
            "addendum_output_hash_manifest_sha256": sha256_file(addendum_hashes_path),
            "cohort_list_sha256": sha256_file(cohort_path),
            "rights_ledger_sha256": sha256_file(rights_path),
            "attribution_sha256": sha256_file(attribution_path),
            "gallery_manifest_sha256": sha256_file(gallery_manifest_path),
            "gallery_asset_manifest_sha256": sha256_file(gallery_asset_manifest_path),
            "gallery_selected_uid_index_sha256": sha256_file(gallery_selected_path),
            "analysis_script_sha256": sha256_file(Path(__file__).resolve()),
        },
        "copied_panels": [{"object_uid": uid, "path": str((panel_dir / f"candidate_{int(selected_by_uid[uid]['panel_order']):02d}_{uid}.png").relative_to(review_root)), "sha256": copied_panel_hashes[uid]} for uid in curation_order],
        "checks": checks,
    }
    stable_json(pool_dir / "POOL_AUDIT.json", audit)
    stable_json(review_root / "REVIEWER_VISUAL_CANDIDATE_POOL_AUDIT.json", audit)
    audit_md = """# Reviewer visual candidate pool audit

**Status: `PASS`.** The complete Fresh C N=300 index covers six methods and seven metrics. All primary and addendum sources passed their existing integrity gates; the output hashes in the index were computed from the existing generated image files.

The publication-eligible visual subset contains 20 objects, each with `FIGURE_ONLY` status and attribution requirements. The 20 existing six-method panels were copied byte-for-byte. No other object images were copied. The four curation pools contain 20 clear adapter/no-adapter contrasts, 10 focal two-endpoint-consistent examples, 5 C3−GFH Full-PSNR/Edge-SSIM trade-offs, and 10 adverse examples.

The main-paper list has 12 candidates, with 8 frozen for author review; the reviewer-response list has 16 candidates; the supplementary gallery list retains all 20. These are illustrative selections, not statistical samples. The full-cohort index and quantitative summaries carry the cohort-level claims.
"""
    (review_root / "REVIEWER_VISUAL_CANDIDATE_POOL_AUDIT.md").write_text(audit_md, encoding="utf-8")

    print(f"VISUAL_CANDIDATE_POOL=PASS; index={len(index_rows)} objects; copied panels={len(copied_panel_hashes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
