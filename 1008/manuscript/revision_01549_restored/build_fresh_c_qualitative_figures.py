#!/usr/bin/env python3
"""Rebuild compact 01549-style qualitative figures from authenticated Fresh C RGB outputs.

The script only extracts the frozen target view from saved Fresh C image grids,
composites the transparent reference onto white, and lays out one shared ROI.
It does not run inference, alter image color, or apply generative enhancement.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CHECKPOINT_SHA256 = "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0"
RUNNER_SHA256 = "e5c28e915ba137d3541eb4c032daaf62a798332d63b32917b749fe1bcc74e9e3"
VIEW_ORDER = (0, 15, 12, 16, 13, 14)
GRID_BBOX = {
    0: (0, 0, 256, 256),
    15: (256, 0, 512, 256),
    12: (0, 256, 256, 512),
    16: (256, 256, 512, 512),
    13: (0, 512, 256, 768),
    14: (256, 512, 512, 768),
}
ROI_BBOX = {
    "c76ac44df995482185077da81939b306": (48, 90, 208, 210),
    "d0e116a62bfc4cdd9edf60671073b306": (48, 90, 208, 210),
    "0571e6db30c84b1593bc55a8e145a430": (48, 90, 208, 210),
    "06fa4974f8cd4d4ea792e98fa1521457": (48, 90, 208, 210),
    "f6979d7ff8e54c4daf00fee46f09a139": (48, 90, 208, 210),
}
METHODS = {
    "Reference": ("reference", "reference"),
    "No Adapter": ("primary", "no_adapter"),
    "GFL": ("primary", "native_gfl"),
    "GFH": ("primary", "native_gfh"),
    "C3": ("primary", "native_gc3"),
    "LLH": ("addendum", "layer_llh"),
    "Generic Linear": ("addendum", "gen_linear"),
}
EXAMPLES = {
    "fig4": [
        ("c76ac44df995482185077da81939b306", "C3--GFL favorable endpoint example",
         ("Reference", "GFL", "GFH", "C3")),
        ("d0e116a62bfc4cdd9edf60671073b306", "C3--GFL adverse endpoint example",
         ("Reference", "GFL", "GFH", "C3")),
    ],
    "fig5": [
        ("0571e6db30c84b1593bc55a8e145a430", "C3 versus fixed-scale comparison",
         ("Reference", "GFL", "GFH", "C3")),
        ("06fa4974f8cd4d4ea792e98fa1521457", "Generic Linear counterexample",
         ("Reference", "GFL", "C3", "Generic Linear")),
    ],
    "fig6_color_diagnostic": [
        ("f6979d7ff8e54c4daf00fee46f09a139",
         "Selected Fresh C color/detail example; not selected for color",
         ("Reference", "No Adapter", "GFL", "LLH")),
    ],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pixel_sha256(image: Image.Image) -> str:
    return hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def verify_protocol(data_root: Path) -> tuple[dict, dict[str, dict[str, dict[str, str]]]]:
    primary_gate = json.loads((data_root / "FRESH_C_INTEGRITY_GATE.json").read_text())
    addendum_gate = json.loads((data_root / "FRESH_C_ADDENDUM_INTEGRITY_GATE.json").read_text())
    if primary_gate.get("status") != "PASS" or addendum_gate.get("status") != "PASS":
        raise RuntimeError("Fresh C primary and addendum integrity gates must both pass")

    manifests = {
        name: json.loads((data_root / "runs" / run / "run_manifest_shard0.json").read_text())
        for name, run in (("primary", "c3_confirmation"),
                          ("addendum", "revision_era_addendum"))
    }
    for name, manifest in manifests.items():
        if manifest.get("checkpoint_sha256") != CHECKPOINT_SHA256:
            raise RuntimeError(f"{name} checkpoint hash does not match the frozen Fresh C record")
        if manifest.get("runner_script_sha256") != RUNNER_SHA256:
            raise RuntimeError(f"{name} runner hash does not match the frozen Fresh C record")
    if manifests["primary"]["checkpoint_sha256"] != manifests["addendum"]["checkpoint_sha256"]:
        raise RuntimeError("primary and addendum checkpoint identities differ")
    if manifests["primary"]["runner_script_sha256"] != manifests["addendum"]["runner_script_sha256"]:
        raise RuntimeError("primary and addendum runner identities differ")

    tables: dict[str, dict[str, dict[str, str]]] = {"primary": {}, "addendum": {}}
    run_files = {
        "primary": data_root / "runs/c3_confirmation/per_object_metrics.csv",
        "addendum": data_root / "runs/revision_era_addendum/per_object_metrics.csv",
    }
    for group, path in run_files.items():
        for row in read_csv(path):
            tables[group].setdefault(row["condition"], {})[row["object_uid"]] = row
    return manifests, tables


def reference_tile(data_root: Path, uid: str, view_id: int) -> tuple[Image.Image, Path]:
    source = data_root / "renders" / uid / "image" / f"{view_id:03d}.png"
    rgba = Image.open(source).convert("RGBA")
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    white.alpha_composite(rgba)
    return white.convert("RGB").resize((256, 256), Image.Resampling.LANCZOS), source


def method_tile(data_root: Path, uid: str, condition: str, view_id: int) -> tuple[Image.Image, Path]:
    group, source_condition = METHODS[condition]
    run_dir = "c3_confirmation" if group == "primary" else "revision_era_addendum"
    source = data_root / "runs" / run_dir / "predictions" / source_condition / f"{uid}.png"
    panel = Image.open(source).convert("RGB")
    if panel.size != (512, 768):
        raise RuntimeError(f"unexpected saved Fresh C panel size {panel.size}: {source}")
    return panel.crop(GRID_BBOX[view_id]), source


def draw_panel(
    figure_id: str,
    data_root: Path,
    source_manifest: dict[tuple[str, str, str], dict[str, str]],
    manifests: dict,
    tables: dict[str, dict[str, dict[str, str]]],
    output_dir: Path,
    selection_record: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    scale = 2
    col_w, context_h = 320, 320
    crop_w, crop_h = 320, 240
    methods_h, case_h, crop_label_h, gap = 44, 30, 24, 14
    examples = EXAMPLES[figure_id]
    width = 4 * col_w
    height = len(examples) * (case_h + methods_h + context_h + crop_label_h + crop_h + gap)
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    label_font, small_font = font(17), font(15)
    display_names = {
        "Reference": "Reference",
        "No Adapter": "No Adapter",
        "GFL": "Fixed Low (GFL)",
        "GFH": "Fixed High (GFH)",
        "C3": "TCAS (C3)",
        "LLH": "Layer L-L-H (LLH)",
        "Generic Linear": "Generic Linear",
    }

    manifest_rows: list[dict[str, str]] = []
    y = 0
    for case_index, (uid, case_title, conditions) in enumerate(examples):
        if len(conditions) != 4:
            raise RuntimeError("each example must show exactly four conditions")
        roi = ROI_BBOX[uid]
        draw.rectangle((0, y, width - 1, y + case_h - 1), fill=(250, 250, 250))
        draw.text((7, y + 5), f"({chr(97 + case_index)}) {case_title} | target view 0",
                  fill=(25, 25, 25), font=small_font)
        y += case_h
        for column, method in enumerate(conditions):
            x = column * col_w
            draw.rectangle((x, y, x + col_w - 1, y + methods_h - 1), fill=(245, 245, 245))
            label = display_names[method]
            box = draw.textbbox((0, 0), label, font=label_font)
            draw.text((x + (col_w - (box[2] - box[0])) / 2, y + 11),
                      label, fill=(20, 20, 20), font=label_font)
        y += methods_h

        # The source target view is 256x256 in the saved prediction grid.
        for column, method in enumerate(conditions):
            x = column * col_w
            if method == "Reference":
                tile, input_path = reference_tile(data_root, uid, 0)
                input_key = (uid, "Reference", "0")
                source_hash_row = source_manifest[input_key]
                expected_hash = source_hash_row["sha256"]
            else:
                tile, input_path = method_tile(data_root, uid, method, 0)
                group, source_condition = METHODS[method]
                input_key = (uid, source_condition, "six-view-grid")
                source_hash_row = source_manifest[input_key]
                expected_hash = source_hash_row["sha256"]
            actual_hash = sha256(input_path)
            if actual_hash != expected_hash:
                raise RuntimeError(f"source image hash mismatch for {input_path}")

            # Draw the identical pixel ROI on every full-object context tile.
            context = tile.resize((col_w, context_h), Image.Resampling.LANCZOS)
            ctx_draw = ImageDraw.Draw(context)
            factor = col_w / 256
            box = tuple(round(v * factor) for v in roi)
            ctx_draw.rectangle(box, outline=(205, 35, 45), width=3)
            canvas.paste(context, (x, y))
            crop = tile.crop(roi).resize((crop_w, crop_h), Image.Resampling.LANCZOS)
            y_crop = y + context_h + crop_label_h
            canvas.paste(crop, (x, y_crop))

            if method == "Reference":
                group, condition = "reference", "Reference"
                row = tables["primary"]["native_gc3"][uid]
            else:
                group, condition = METHODS[method]
                row = tables[group][condition][uid]
            protocol_group = "primary" if group == "reference" else group
            shared_rows = [
                tables["primary"][condition_name][uid]
                for condition_name in ("native_gfl", "native_gfh", "native_gc3", "no_adapter")
            ] + [
                tables["addendum"][condition_name][uid]
                for condition_name in ("layer_llh", "gen_linear")
            ]
            identity_fields = (
                "object_idx", "seed_base", "input_cond_sha256", "input_depth_sha256",
                "input_global_embeds_sha256", "input_init_latent_sha256",
                "input_normal_sha256", "input_target_sha256",
            )
            for field in identity_fields:
                if len({item[field] for item in shared_rows}) != 1:
                    raise RuntimeError(f"Fresh C paired identity mismatch for {uid}/{field}")
            object_idx = int(row["object_idx"])
            seed = int(row["seed_base"]) + object_idx
            manifest_rows.append({
                "figure_id": figure_id,
                "panel_id": f"{figure_id}({chr(97 + case_index)})",
                "object_uid": uid,
                "view_id": "0",
                "method": method,
                "checkpoint_sha256": manifests["primary"]["checkpoint_sha256"],
                "runner_sha256": manifests["primary"]["runner_script_sha256"],
                "seed": str(seed),
                "object_idx": str(object_idx),
                "input_path": str(input_path.relative_to(data_root.parents[2])),
                "input_sha256": actual_hash,
                "tile_bbox": "0,0,512,512" if method == "Reference" else ",".join(map(str, GRID_BBOX[0])),
                "crop_bbox": ",".join(map(str, roi)),
                "crop_coordinate_space": "256x256 target-view RGB pixels",
                "seed_policy": "42 + object_idx",
                "latent_seed": str(manifests[protocol_group]["latent_seed"]),
                "context_pixel_sha256": pixel_sha256(tile),
                "roi_pixel_sha256": pixel_sha256(tile.crop(roi)),
                "source_metric_row_sha256": "" if method == "Reference" else hashlib.sha256(
                    json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ).hexdigest(),
                "source_metric_table_sha256": sha256(
                    data_root / "runs" /
                    ("c3_confirmation" if protocol_group == "primary" else "revision_era_addendum") /
                    "per_object_metrics.csv"
                ),
                "source_run_manifest_sha256": sha256(
                    data_root / "runs" /
                    ("c3_confirmation" if protocol_group == "primary" else "revision_era_addendum") /
                    "run_manifest_shard0.json"
                ),
                "source_integrity_gate_sha256": sha256(
                    data_root / (
                        "FRESH_C_INTEGRITY_GATE.json" if protocol_group == "primary"
                        else "FRESH_C_ADDENDUM_INTEGRITY_GATE.json"
                    )
                ),
                "output_sha256": "",
                "figure_pdf_sha256": "",
                "condition_group": group,
                "condition": condition,
                "inference_protocol": "Fresh C saved output; matched UID, frozen checkpoint, runner, shared object seed, reference and target-view camera",
                "selection_record": selection_record.get("selection_record_source", "") if selection_record else "",
                "selection_sample_id": selection_record.get("sample_id", "") if selection_record else "",
                "selection_focal_contrast": selection_record.get("focal_contrast", "") if selection_record else "",
                "selection_stratum": selection_record.get("selection_stratum", "") if selection_record else "",
                "selection_previously_viewed": selection_record.get("previously_viewed", "") if selection_record else "",
                "selection_independent_confirmation": selection_record.get("independent_confirmation", "") if selection_record else "",
                "selection_use": selection_record.get("figure_use", "") if selection_record else "",
            })

        # Keep the crop label below context, with a small marker in each cell.
        y_label = y + context_h
        draw.text((7, y_label + 4),
                  "Zoomed crop from the same pixel ROI in all columns (red box above)",
                  fill=(50, 50, 50), font=font(13))
        y += context_h + crop_label_h + crop_h + gap

    canvas = canvas.resize((width * scale, height * scale), Image.Resampling.LANCZOS)
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / f"{figure_id}_freshc_context_roi.png"
    pdf_path = output_dir / f"{figure_id}_freshc_context_roi.pdf"
    canvas.save(png_path, optimize=True)
    canvas.save(pdf_path, "PDF", resolution=300.0)
    png_sha, pdf_sha = sha256(png_path), sha256(pdf_path)
    for row in manifest_rows:
        row["output_sha256"] = png_sha
        row["figure_pdf_sha256"] = pdf_sha
    return manifest_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fresh-c-root", type=Path, required=True)
    parser.add_argument("--manifest-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    data_root = args.fresh_c_root.resolve()
    manifests, tables = verify_protocol(data_root)

    if not (data_root / "fresh_c_objects.txt").is_file():
        raise FileNotFoundError(data_root / "fresh_c_objects.txt")
    cohort = {line.strip() for line in (data_root / "fresh_c_objects.txt").read_text().splitlines() if line.strip()}
    selection_rows = read_csv(args.manifest_dir / "FRESH_C_COLOR_FIGURE_SELECTION.csv")
    if len(selection_rows) != 1:
        raise RuntimeError("expected one frozen Fresh C color-figure selection record")
    selection = selection_rows[0]
    expected_selection = {
        "sample_id": "freshc_panel_13",
        "uid": "f6979d7ff8e54c4daf00fee46f09a139",
        "focal_contrast": "C3-GFL",
        "selection_stratum": "lowest_focal_FG_LPIPS",
        "reverse_orientation": "False",
        "previously_viewed": "True",
        "independent_confirmation": "False",
        "output_action": "reuse_existing_identity_verified_rgb",
    }
    for field, expected in expected_selection.items():
        if selection.get(field) != expected:
            raise RuntimeError(f"unexpected frozen color-figure selection {field}: {selection.get(field)!r}")
    selection_source = Path(selection["selection_record_source"])
    if not selection_source.is_file() or sha256(selection_source) != selection["selection_source_sha256"]:
        raise RuntimeError("frozen color-figure selection source hash mismatch")
    gallery_rows = read_csv(args.manifest_dir / "gallery_asset_sha256.csv")
    source_manifest: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in gallery_rows:
        uid = row["object_uid"]
        view = row["view"]
        key = (uid, row["condition"], str(view))
        source_manifest[key] = row

    all_rows = []
    for figure_id, examples in EXAMPLES.items():
        for uid, _, _ in examples:
            if uid not in cohort:
                raise RuntimeError(f"selected UID is not in the frozen Fresh C cohort: {uid}")
            for group, condition in (("primary", "no_adapter"), ("primary", "native_gfl"),
                                     ("primary", "native_gfh"), ("primary", "native_gc3"),
                                     ("addendum", "layer_llh"), ("addendum", "gen_linear")):
                if uid not in tables[group].get(condition, {}):
                    raise RuntimeError(f"missing Fresh C metric row: {uid}/{condition}")
        all_rows.extend(draw_panel(
            figure_id, data_root, source_manifest, manifests, tables, args.output_dir,
            selection if figure_id == "fig6_color_diagnostic" else None,
        ))

    manifest_path = args.output_dir / "FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(all_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"created {len(EXAMPLES)} Fresh C figures and {len(all_rows)} provenance rows")
    print(manifest_path)


if __name__ == "__main__":
    main()
