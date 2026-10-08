#!/usr/bin/env python3
"""Lock the R1 color-diagnostic objects before running any new condition."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

METHODS = ("no_adapter", "native_gfl", "native_gfh", "native_gc3", "gen_linear", "layer_llh")
METHOD_SOURCES = {
    "no_adapter": "c3_confirmation",
    "native_gfl": "c3_confirmation",
    "native_gfh": "c3_confirmation",
    "native_gc3": "c3_confirmation",
    "gen_linear": "revision_era_addendum",
    "layer_llh": "revision_era_addendum",
}
FIGURE_CASES = (
    ("fig4_row1", 4, "antique potion chest"),
    ("fig4_row2", 3, "classical stone bust"),
    ("fig4_row3", 12, "colored chest"),
    ("fig6_row1", 1, "blue-roof object"),
    ("fig6_row2", 15, "white object"),
    ("fig6_row3", 7, "red-accented backpack"),
)
DECLARED_VIEW_IDS = (0, 15, 12, 16, 13, 14)
EXPECTED_RUNNER = "e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3"
EXPECTED_CHECKPOINT = "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0"
EXPECTED_CONFIG = "295311ba717b2e360a6ab1eb54306afcfaa5ac66a7441410868b69714818ba8b"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def effective_views(data_root: Path, uid: str) -> tuple[list[int], bool, list[int]]:
    from PIL import Image
    import numpy as np

    image_dir = data_root / uid / "image"
    first = np.asarray(Image.open(image_dir / "000.png").convert("RGBA"))[:, :, 3]
    fourth = np.asarray(Image.open(image_dir / "014.png").convert("RGBA"))[:, :, 3]
    reverse = int((first == 0).sum()) > int((fourth == 0).sum())
    if reverse:
        return [14, 15, 0, 16, 12, 13], True, [1, 3]
    return list(DECLARED_VIEW_IDS), False, []


def check_grid(path: Path) -> None:
    from PIL import Image

    if not path.is_file():
        raise SystemExit(f"missing RGB grid: {path}")
    with Image.open(path) as image:
        if image.mode != "RGB" or image.size != (512, 768):
            raise SystemExit(f"unexpected RGB grid {path}: {image.mode} {image.size}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path("/4T/CXY/MV-Painter"))
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    root = args.project_root.resolve()
    out = args.output_dir.resolve()
    gallery = root / "1006/figures/strategy_comparison_gallery/fresh_c_final"
    fresh_root = root / "1006/data/fresh_c"
    fresh_data = fresh_root / "renders"
    fresh_objects_path = fresh_root / "fresh_c_objects.txt"
    legacy_data = root / "data/train_data/rendered_full"
    legacy_objects_path = legacy_data / "test_objects_300.txt"
    methods = list(METHODS)

    gallery_manifest_path = gallery / "gallery_manifest.json"
    asset_manifest_path = gallery / "gallery_asset_sha256.csv"
    gallery_manifest = json.loads(gallery_manifest_path.read_text())
    groups = sorted(gallery_manifest["selected_groups"], key=lambda row: int(row["panel_order"]))
    if len(groups) != 20:
        raise SystemExit(f"expected 20 frozen gallery panels, found {len(groups)}")
    asset_rows = read_csv(asset_manifest_path)
    assets: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in asset_rows:
        assets[(row["object_uid"], row["condition"], row["view"])] = row

    fresh_uids = [line.strip() for line in fresh_objects_path.read_text().splitlines() if line.strip()]
    legacy_uids = [line.strip() for line in legacy_objects_path.read_text().splitlines() if line.strip()]
    if len(fresh_uids) != 300 or len(legacy_uids) != 300:
        raise SystemExit("expected the frozen 300-object source lists")

    c3_manifest = json.loads((fresh_root / "runs/c3_confirmation/LAUNCH_IDENTITY.json").read_text())
    addendum_manifest = json.loads((fresh_root / "runs/revision_era_addendum/LAUNCH_IDENTITY.json").read_text())
    for identity in (c3_manifest, addendum_manifest):
        hashes = identity["source_hashes"]
        if hashes["runner"] != EXPECTED_RUNNER or hashes["checkpoint"] != EXPECTED_CHECKPOINT:
            raise SystemExit("Fresh C run identity does not match the frozen runner/checkpoint")
        if identity["cohort_n"] != 300:
            raise SystemExit("Fresh C cohort size changed")
    if set(c3_manifest["conditions"]) != set(METHODS[:4]):
        raise SystemExit("Fresh C primary conditions changed")
    if set(addendum_manifest["conditions"]) != set(METHODS[4:]):
        raise SystemExit("Fresh C addendum conditions changed")
    if (c3_manifest["cohort_manifest_sha256"] != addendum_manifest["cohort_manifest_sha256"]
            or c3_manifest["cohort_uid_list_sha256"] != addendum_manifest["cohort_uid_list_sha256"]
            or c3_manifest["input_embeddings_manifest_sha256"] != addendum_manifest["input_embeddings_manifest_sha256"]):
        raise SystemExit("Fresh C primary and addendum inputs are not the same frozen cohort")

    run_rows: dict[tuple[str, str], dict[str, str]] = {}
    metric_sources = {
        "c3_confirmation": fresh_root / "runs/c3_confirmation/per_object_metrics.csv",
        "revision_era_addendum": fresh_root / "runs/revision_era_addendum/per_object_metrics.csv",
    }
    for source, path in metric_sources.items():
        for row in read_csv(path):
            run_rows[(row["object_uid"], row["condition"])] = row

    frozen = []
    for group in groups:
        uid = group["object_uid"]
        if uid not in fresh_uids:
            raise SystemExit(f"gallery UID is absent from the frozen Fresh C list: {uid}")
        object_idx = fresh_uids.index(uid)
        object_rows = [run_rows.get((uid, method)) for method in methods]
        if any(row is None for row in object_rows):
            raise SystemExit(f"incomplete six-condition run rows for {uid}")
        input_fields = sorted(k for k in object_rows[0] if k.startswith("input_") and k.endswith("_sha256"))
        baseline_input_identity = tuple(object_rows[0][k] for k in input_fields)
        if any(tuple(row[k] for k in input_fields) != baseline_input_identity for row in object_rows[1:]):
            raise SystemExit(f"shared-input hashes differ across conditions for {uid}")
        if any(int(row["object_idx"]) != object_idx or int(row["seed_base"]) != 42
               for row in object_rows):
            raise SystemExit(f"object order/seed mismatch for {uid}")

        method_paths = {}
        for method in methods:
            row = assets.get((uid, method, "six-view-grid"))
            if row is None:
                raise SystemExit(f"gallery hash row missing for {uid}/{method}")
            source_path = root / row["path"]
            if sha256(source_path) != row["sha256"]:
                raise SystemExit(f"gallery output hash mismatch: {source_path}")
            check_grid(source_path)
            method_paths[method] = {
                "path": str(source_path),
                "sha256": row["sha256"],
            }
        reference_rows = []
        for view_id in DECLARED_VIEW_IDS:
            row = assets.get((uid, "Reference", str(view_id)))
            if row is None:
                raise SystemExit(f"reference hash row missing for {uid}/view{view_id}")
            source_path = root / row["path"]
            if sha256(source_path) != row["sha256"]:
                raise SystemExit(f"reference hash mismatch: {source_path}")
            reference_rows.append({"view": view_id, "path": str(source_path), "sha256": row["sha256"]})
        view_order, reverse, rotate_slots = effective_views(fresh_data, uid)
        frozen.append({
            "sample_id": f"freshc_panel_{int(group['panel_order']):02d}",
            "uid": uid,
            "source": "existing_formal_fresh_c_gallery",
            "object_idx": object_idx,
            "object_seed": 42 + object_idx,
            "focal_contrast": group["focal_contrast"],
            "selection_stratum": group["selection_stratum"],
            "previously_viewed": True,
            "independent_confirmation": False,
            "data_root": str(fresh_data),
            "object_list": str(fresh_objects_path),
            "declared_view_ids": list(DECLARED_VIEW_IDS),
            "effective_view_order": view_order,
            "reverse_orientation": reverse,
            "rotate_output_slots_90deg": rotate_slots,
            "input_hashes": {k: object_rows[0][k] for k in input_fields},
            "reference_views": reference_rows,
            "method_grids": method_paths,
            "output_action": "reuse_existing_identity_verified_rgb",
        })

    historical_source_paths = {}
    for filename in ("fig4.pdf", "fig6.pdf"):
        path = root / "01549_BASELINE_BACKUP_20261008" / filename
        historical_source_paths[filename] = {"path": str(path), "sha256": sha256(path)}
    for script_name in ("make_fig4_v3_crop.py", "make_fig6_v2_crop.py"):
        path = root / "scripts" / script_name
        historical_source_paths[script_name] = {"path": str(path), "sha256": sha256(path)}

    for sample_id, object_idx, description in FIGURE_CASES:
        uid = legacy_uids[object_idx]
        object_dir = legacy_data / uid
        selected = []
        for view_id in DECLARED_VIEW_IDS:
            for channel in ("image", "normal", "depth_png", "embeddings"):
                folder = object_dir / channel
                if not folder.is_dir() or not any(folder.iterdir()):
                    raise SystemExit(f"missing {channel} input for historical object {uid}")
            image_path = object_dir / "image" / f"{view_id:03d}.png"
            selected.append({"view": view_id, "path": str(image_path), "sha256": sha256(image_path)})
        old_index = f"obj_{object_idx:04d}.png"
        old_predictions = {}
        for label in ("GT", "s_1.25", "s_2.50", "C3_TCAS"):
            path = root / "mvpoutput/revision_clipiqa/images" / label / old_index
            if not path.is_file():
                raise SystemExit(f"historical figure source image missing: {path}")
            old_predictions[label] = {"path": str(path), "sha256": sha256(path)}
        view_order, reverse, rotate_slots = effective_views(legacy_data, uid)
        frozen.append({
            "sample_id": sample_id,
            "uid": uid,
            "source": "01549_fig4_fig6_original_object",
            "figure_object_index": object_idx,
            "object_idx": object_idx,
            "object_seed": 42 + object_idx,
            "description": description,
            "selected_by": "frozen original Fig. 4/6 crop scripts",
            "previously_viewed": True,
            "independent_confirmation": False,
            "data_root": str(legacy_data),
            "object_list": str(legacy_objects_path),
            "declared_view_ids": list(DECLARED_VIEW_IDS),
            "effective_view_order": view_order,
            "reverse_orientation": reverse,
            "rotate_output_slots_90deg": rotate_slots,
            "reference_views": selected,
            "historical_pre_revision_images": old_predictions,
            "output_action": "run_six_conditions_with_frozen_validation_v3_identity",
        })

    if len(frozen) != 26 or len({row["uid"] for row in frozen}) != 26:
        raise SystemExit("the diagnostic set must contain 26 unique objects")
    lock = {
        "title": "R1 color failure diagnostic set",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "sample_count": len(frozen),
        "purpose": "failure-enriched development diagnosis; not an independent confirmation cohort",
        "selection_rule": (
            "Use the six exact historical objects named by the original 01549 Fig. 4/6 crop scripts, "
            "plus all 20 pre-existing Fresh C formal comparison panels. The gallery objects were "
            "previously viewed and metric-ranked; they are retained as descriptive diagnostics, not "
            "treated as blinded or independent."
        ),
        "fixed_methods": methods,
        "endpoint_lock": {
            "primary": "mean foreground CIEDE2000 across six target views, object is the unit; lower is better",
            "secondary": ["FG-LPIPS", "FG-PSNR", "Edge-SSIM"],
            "purple_cast_flag": "object-level mean foreground delta a* >= 5 and delta b* <= -5, with mean foreground CIEDE2000 >= 5",
            "threshold_status": "diagnostic threshold frozen before new historical-object generation; no inferential claim",
            "visual_failures": ["purple cast", "repeated pattern", "fine-detail destruction", "structure damage"],
            "laplacian_variance_is_not_a_fidelity_endpoint": True,
        },
        "protocol_identity": {
            "runner_sha256": EXPECTED_RUNNER,
            "checkpoint_sha256": EXPECTED_CHECKPOINT,
            "config_sha256": EXPECTED_CONFIG,
            "target_view_mode": "unique6",
            "declared_target_views": list(DECLARED_VIEW_IDS),
            "resolution": 256,
            "steps": 50,
            "sampler": "EulerDiscreteScheduler",
            "latent_seed": 42,
            "object_seed_rule": "42 + object_idx in the frozen source-list order",
            "methods": methods,
        },
        "source_artifacts": {
            "gallery_manifest": {"path": str(gallery_manifest_path), "sha256": sha256(gallery_manifest_path)},
            "gallery_asset_hashes": {"path": str(asset_manifest_path), "sha256": sha256(asset_manifest_path)},
            "fresh_c_object_list": {"path": str(fresh_objects_path), "sha256": sha256(fresh_objects_path)},
            "legacy_object_list": {"path": str(legacy_objects_path), "sha256": sha256(legacy_objects_path)},
            "historical_01549_sources": historical_source_paths,
            "fresh_c_primary_launch": {
                "path": str(fresh_root / "runs/c3_confirmation/LAUNCH_IDENTITY.json"),
                "sha256": sha256(fresh_root / "runs/c3_confirmation/LAUNCH_IDENTITY.json"),
            },
            "fresh_c_addendum_launch": {
                "path": str(fresh_root / "runs/revision_era_addendum/LAUNCH_IDENTITY.json"),
                "sha256": sha256(fresh_root / "runs/revision_era_addendum/LAUNCH_IDENTITY.json"),
            },
        },
        "samples": frozen,
    }

    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "SAMPLE_FREEZE.json"
    json_path.write_text(json.dumps(lock, indent=2) + "\n")
    csv_path = out / "SAMPLE_FREEZE.csv"
    columns = ("sample_id", "uid", "source", "object_idx", "object_seed",
               "figure_object_index", "focal_contrast", "selection_stratum",
               "reverse_orientation", "effective_view_order", "previously_viewed",
               "independent_confirmation", "output_action")
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in frozen:
            writer.writerow({key: json.dumps(row.get(key), ensure_ascii=False)
                             if isinstance(row.get(key), (list, dict)) else row.get(key)
                             for key in columns})
    print(f"locked {len(frozen)} diagnostic objects: {json_path}")


if __name__ == "__main__":
    main()
