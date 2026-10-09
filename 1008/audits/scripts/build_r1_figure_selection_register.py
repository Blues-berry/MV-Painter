#!/usr/bin/env python3
"""Hash-check Fresh C figure candidates and write a rights-aware selection CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


SELECTED_ROLES = {
    "c76ac44df995482185077da81939b306": (
        "main_candidate_c3_gfl_favorable",
        "C3-GFL FG-PSNR +2.644 dB and FG-LPIPS -0.00183; both endpoints favor C3.",
    ),
    "0c8e1199b7b64ad2ac1c6ff784139dec": (
        "main_candidate_typical_c3_gfl",
        "Pre-ranked near-median C3-GFL FG-PSNR example; illustrative typical-effect panel.",
    ),
    "d0e116a62bfc4cdd9edf60671073b306": (
        "supplement_candidate_c3_gfl_adverse",
        "C3-GFL FG-PSNR -2.034 dB and FG-LPIPS +0.00631; both endpoints favor GFL.",
    ),
    "0571e6db30c84b1593bc55a8e145a430": (
        "main_candidate_c3_gfh_endpoint_tradeoff",
        "C3-GFH FG-LPIPS -0.02954 favors C3 while Edge-SSIM -0.00471 favors GFH.",
    ),
    "06fa4974f8cd4d4ea792e98fa1521457": (
        "main_candidate_generic_linear_counterexample",
        "C3-generic-linear FG-PSNR -3.491 dB and FG-LPIPS +0.08172; both favor generic linear.",
    ),
    "f6979d7ff8e54c4daf00fee46f09a139": (
        "supplement_candidate_color_pattern_detail_failure",
        "Visually reviewed for muted color/detail mismatch and saturated repeated stripes in the no-adapter column; not a C3-specific purple-shift claim.",
    ),
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--fresh-gallery", type=Path, required=True)
    parser.add_argument("--rights-csv", type=Path, required=True)
    parser.add_argument("--attribution-csv", type=Path, required=True)
    parser.add_argument("--input-manifest", type=Path, required=True)
    parser.add_argument("--cohort-manifest", type=Path, required=True)
    parser.add_argument("--primary-gate", type=Path, required=True)
    parser.add_argument("--addendum-gate", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    args = parser.parse_args()

    gallery = args.fresh_gallery
    manifest_path = gallery / "gallery_manifest.json"
    source_hash_path = gallery / "gallery_asset_sha256.csv"
    index_path = gallery / "six_method_complete_object_index.csv"
    manifest = json.loads(manifest_path.read_text())
    embedding_manifest = json.loads(args.input_manifest.read_text())
    cohort_manifest = json.loads(args.cohort_manifest.read_text())
    primary_gate = json.loads(args.primary_gate.read_text())
    addendum_gate = json.loads(args.addendum_gate.read_text())

    groups = manifest["selected_groups"]
    if len(groups) != 20:
        raise SystemExit(f"expected 20 candidate groups, got {len(groups)}")

    rights = {row["asset_uid"]: row for row in read_csv(args.rights_csv)}
    attribution = {row["asset_uid"]: row for row in read_csv(args.attribution_csv)}
    asset_rows = read_csv(source_hash_path)
    source_by_uid: dict[str, list[dict[str, str]]] = {}
    for row in asset_rows:
        source_by_uid.setdefault(row["object_uid"], []).append(row)

    object_index: dict[str, dict[str, dict[str, str]]] = {}
    for row in read_csv(index_path):
        object_index.setdefault(row["object_uid"], {})[row["method_label"]] = row

    panel_hashes = {
        Path(row["path"]).name: row["sha256"]
        for row in manifest["generated_file_hashes"]
        if "/panels/" in row["path"]
    }
    if len(panel_hashes) != 20:
        raise SystemExit(f"expected 20 hashed panel outputs, got {len(panel_hashes)}")

    output_rows = []
    verified_panels = 0
    verified_source_assets = 0
    for group in groups:
        order = int(group["panel_order"])
        uid = group["object_uid"]
        panel_name = f"panel_{order:02d}_{uid}.png"
        panel_path = gallery / "panels" / panel_name
        expected_panel_hash = panel_hashes.get(panel_name)
        if not panel_path.is_file() or digest(panel_path) != expected_panel_hash:
            raise SystemExit(f"panel absent or hash mismatch: {panel_path}")
        verified_panels += 1

        rights_row = rights.get(uid)
        attribution_row = attribution.get(uid)
        if not rights_row or not attribution_row:
            raise SystemExit(f"missing rights or attribution row for {uid}")
        if rights_row["final_disposition"] != "FIGURE_ONLY":
            raise SystemExit(f"unexpected publication disposition for {uid}: {rights_row['final_disposition']}")
        if rights_row["publication_figure_allowed"] != "YES_WITH_ATTRIBUTION":
            raise SystemExit(f"figure permission not confirmed for {uid}")
        if attribution_row["status"] != "VERIFIED_CC_BY_ATTRIBUTION_REQUIRED":
            raise SystemExit(f"attribution not verified for {uid}")

        object_assets = source_by_uid.get(uid, [])
        if len(object_assets) != 12:
            raise SystemExit(f"expected 12 source-image hashes for {uid}, got {len(object_assets)}")
        for asset in object_assets:
            path = args.project_root / asset["path"]
            if not path.is_file() or digest(path) != asset["sha256"]:
                raise SystemExit(f"source image absent or hash mismatch: {path}")
            verified_source_assets += 1

        references = {
            row["view"]: row["sha256"]
            for row in object_assets
            if row["condition"] == "Reference"
        }
        method_grids = {
            row["condition"]: row["sha256"]
            for row in object_assets
            if row["role"] == "method_prediction"
        }
        if sorted(references) != ["0", "12", "13", "14", "15", "16"] or len(method_grids) != 6:
            raise SystemExit(f"incomplete six-view source hashes for {uid}")

        methods = object_index[uid]
        c3, gfl, gfh, linear = (
            methods["C3"],
            methods["GFL"],
            methods["GFH"],
            methods["Generic linear"],
        )
        role, reason = SELECTED_ROLES.get(
            uid,
            (
                "reserve_candidate",
                "In the frozen 20-object visual pool; not advanced to a figure slot in this audit.",
            ),
        )

        output_rows.append(
            {
                "panel_order": order,
                "object_uid": uid,
                "candidate_role": role,
                "selection_reason": reason,
                "pool_selection_status": group["selection_stratum"],
                "pool_focal_contrast": group["focal_contrast"],
                "pool_delta_fg_psnr": group["delta_fg_psnr_focal_a_minus_b"],
                "pool_delta_fg_lpips": group["delta_fg_lpips_focal_a_minus_b"],
                "delta_c3_minus_gfl_fg_psnr": float(c3["fg_psnr"]) - float(gfl["fg_psnr"]),
                "delta_c3_minus_gfl_fg_lpips": float(c3["fg_lpips"]) - float(gfl["fg_lpips"]),
                "delta_c3_minus_gfh_edge_ssim": float(c3["edge_ssim"]) - float(gfh["edge_ssim"]),
                "delta_c3_minus_gfh_fg_lpips": float(c3["fg_lpips"]) - float(gfh["fg_lpips"]),
                "delta_c3_minus_generic_linear_fg_psnr": float(c3["fg_psnr"]) - float(linear["fg_psnr"]),
                "delta_c3_minus_generic_linear_fg_lpips": float(c3["fg_lpips"]) - float(linear["fg_lpips"]),
                "candidate_panel_path": f"1008/audits/figure_candidates/{role}.png",
                "source_panel_path": str(panel_path),
                "source_panel_sha256": expected_panel_hash,
                "source_reference_view_sha256s_json": json.dumps(references, sort_keys=True),
                "source_method_grid_sha256s_json": json.dumps(method_grids, sort_keys=True),
                "gallery_manifest_sha256": digest(manifest_path),
                "gallery_asset_hash_table_sha256": digest(source_hash_path),
                "fresh_c_uid_list_sha256": cohort_manifest["selected_uid_list_sha256"],
                "fresh_c_cohort_manifest_sha256": digest(args.cohort_manifest),
                "primary_integrity_gate_sha256": digest(args.primary_gate),
                "addendum_integrity_gate_sha256": digest(args.addendum_gate),
                "primary_gate_status": primary_gate["status"],
                "addendum_gate_status": addendum_gate["status"],
                "checkpoint_sha256": embedding_manifest["checkpoint_sha256"],
                "seed": 42,
                "view_ids": "0;15;12;16;13;14",
                "view_camera_policy": "same frozen target-view IDs for all conditions within object; 2D view comparison",
                "conditions_shown": "Reference;GFL;GFH;No adapter;C3;LLH;Generic linear",
                "original_uv": "not_applicable_2d_output",
                "material_sampler_semantics": "not_applicable_2d_output",
                "gt_source": "Frozen Fresh C target-view RGB/reference images; see source reference hashes and cohort manifest.",
                "source_license": rights_row["license"],
                "source_license_tag": rights_row["source_license_tag"],
                "publication_figure_allowed": rights_row["publication_figure_allowed"],
                "creator": attribution_row["creator"],
                "asset_title": attribution_row["title"],
                "source_url": attribution_row["source_url"],
                "credit_line": attribution_row["credit_line"],
                "visual_status": "Illustrative selection, not a representative cohort estimate; no 3D, seam, PBR, or human-preference claim.",
            }
        )

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    print(
        json.dumps(
            {
                "output_csv": str(args.output_csv),
                "candidate_rows": len(output_rows),
                "verified_panel_pngs": verified_panels,
                "verified_source_images": verified_source_assets,
                "rights_and_attribution_rows": len(output_rows),
                "status": "PASS",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
