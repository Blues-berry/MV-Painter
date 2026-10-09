#!/usr/bin/env python3
"""Build an internal-only contact sheet from already stored GLB-native renders.

The script does not render, bake, or alter experiment outputs. It verifies the
stored image/GLB hashes and camera pairing before arranging untouched tiles.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


METHODS = [
    ("gt", "GT/reference texture"),
    ("no_adapter", "No adapter"),
    ("native_gfl", "GFL"),
    ("native_gfh", "GFH"),
    ("native_gc3", "C3 / TCAS"),
]
VIEWS = [1, 11]
TILE = 256
ROW_LABEL_W = 112
HEADER_H = 116
FONT = ImageFont.load_default(size=22)
SMALL = ImageFont.load_default(size=16)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def choose_examples(results: list[dict[str, str]]) -> list[tuple[str, str, float]]:
    rows = [
        r for r in results
        if r["row_type"] == "paired_object"
        and r["method_a"] == "native_gc3"
        and r["method_b"] == "native_gfl"
        and r["metric"] == "fg_psnr"
    ]
    if len(rows) != 20:
        raise SystemExit(f"expected 20 paired C3-GFL object rows, got {len(rows)}")
    rows.sort(key=lambda r: (float(r["delta_a_minus_b"]), r["object_uid"]))
    values = [float(r["delta_a_minus_b"]) for r in rows]
    median = statistics.median(values)
    median_row = min(rows, key=lambda r: (abs(float(r["delta_a_minus_b"]) - median), r["object_uid"]))
    chosen = [
        ("Strongest loss", rows[0]),
        ("Closest to median", median_row),
        ("Strongest win", rows[-1]),
    ]
    if len({r["object_uid"] for _, r in chosen}) != 3:
        raise SystemExit("extreme/median selection did not yield three distinct objects")
    return [(role, row["object_uid"], float(row["delta_a_minus_b"])) for role, row in chosen]


def load_context_tile(panel_path: Path) -> Image.Image:
    """Crop the first frozen GT target view (view 0) from a six-view panel."""
    panel = Image.open(panel_path).convert("RGB")
    # Archive layout is 2 columns x 3 rows of 256px GT views under a small label.
    if panel.size != (4096, 798):
        raise SystemExit(f"unexpected formal panel dimensions {panel.size}: {panel_path}")
    tile = panel.crop((0, 30, 256, 286))
    if tile.size != (256, 256):
        raise SystemExit("failed to extract the frozen 256x256 view-0 context")
    return tile


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence-root", type=Path, required=True)
    ap.add_argument("--native-render-root", type=Path, required=True)
    ap.add_argument("--paired-results", type=Path, required=True)
    ap.add_argument("--formal-panel-root", type=Path, required=True)
    ap.add_argument("--glb-lineage", type=Path, required=True)
    ap.add_argument("--b3-campaign-manifest", type=Path, required=True)
    ap.add_argument("--renderer-script", type=Path, required=True)
    ap.add_argument("--output-png", type=Path, required=True)
    ap.add_argument("--output-csv", type=Path, required=True)
    args = ap.parse_args()

    manifest_path = args.native_render_root / "GLB_NATIVE_EGL_RENDER_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    lineage = json.loads(args.glb_lineage.read_text())
    campaign = json.loads(args.b3_campaign_manifest.read_text())
    metrics_hash = sha256(args.evidence_root / "bake_handoff/GLB_NATIVE_EGL_RENDER_V1/UNSEEN_OBJECT_METRICS.csv")
    renderer_hash = sha256(args.renderer_script)
    if renderer_hash != manifest["renderer_script_sha256"]:
        raise SystemExit("renderer script hash does not match the frozen render manifest")
    if manifest["raw_views"] != list(range(1, 12)) or manifest["render_count"] != 1760:
        raise SystemExit("unexpected render protocol/count")
    if lineage.get("status") != "PASS" or lineage.get("generation_seed") != 42:
        raise SystemExit("GLB source-output lineage is not verified for seed 42")
    if campaign.get("checkpoint_sha256") != "0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0":
        raise SystemExit("B3 checkpoint hash does not match the frozen C3 lineage")
    lineage_objects = {obj["uid"]: obj for obj in lineage["objects"]}

    records: dict[tuple[str, str, int], dict] = {}
    for row in manifest["renders"]:
        records[(row["object"], row["method"], int(row["raw_view"]))] = row
    deltas = choose_examples(load_rows(args.paired_results))

    context_manifest = json.loads((args.formal_panel_root / "archive_manifest.json").read_text())
    context_objects = set(context_manifest["objects"])
    methods = [m for m, _ in METHODS]
    labels = dict(METHODS)
    rows_out: list[dict[str, str | int | float]] = []

    group_w = ROW_LABEL_W + TILE * 3
    figure_y0 = 82
    canvas_h = figure_y0 + HEADER_H + 30 + TILE * (1 + len(METHODS))
    canvas = Image.new("RGB", (group_w * len(deltas), canvas_h), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 12), "Unlit base-color renders of stored baked GLBs", fill="black", font=FONT)
    draw.text(
        (16, 44),
        "Internal review only: N=20 historical UV-supported subset; selected by C3-GFL unseen FG-PSNR loss / median / win.",
        fill=(60, 60, 60), font=SMALL,
    )

    verified_pngs = verified_glbs = 0
    for group_idx, (role, uid, delta) in enumerate(deltas):
        if uid not in context_objects:
            raise SystemExit(f"no frozen six-view context panel for {uid}")
        if uid not in lineage_objects or lineage_objects[uid].get("glb_disposition") != "baked_and_rendered":
            raise SystemExit(f"no verified source-output-to-GLB lineage for {uid}")
        generated = {r["condition"]: r for r in lineage_objects[uid]["generated_conditions"]}
        if not {"no_adapter", "native_gfl", "native_gfh", "native_gc3"} <= set(generated):
            raise SystemExit(f"lineage missing a requested method for {uid}")
        for cond in ("no_adapter", "native_gfl", "native_gfh", "native_gc3"):
            if generated[cond]["seed_base"] != 42:
                raise SystemExit(f"unexpected generation seed in lineage for {uid}/{cond}")
        x0 = group_idx * group_w
        panel_name = f"panel_{context_manifest['objects'].index(uid):02d}_{uid}.png"
        context_path = args.formal_panel_root / panel_name
        context_hash = sha256(context_path)
        context_tile = load_context_tile(context_path)
        draw.text(
            (x0 + 8, figure_y0),
            f"{role}: {uid} | C3-GFL FG-PSNR {delta:+.3f} dB",
            fill="black", font=SMALL,
        )

        table_y = figure_y0 + HEADER_H
        # Reference context is a single, frozen view-0 target image. The two
        # render columns below are unseen camera IDs 1 and 11 for all methods.
        draw.text((x0 + ROW_LABEL_W + 12, table_y + 8), "Seen target context", fill="black", font=SMALL)
        draw.text((x0 + ROW_LABEL_W + TILE + 12, table_y + 8), "Unseen raw_view 1", fill="black", font=SMALL)
        draw.text((x0 + ROW_LABEL_W + 2 * TILE + 12, table_y + 8), "Unseen raw_view 11", fill="black", font=SMALL)
        context_cell = Image.new("RGB", (TILE, TILE), "white")
        context_cell.paste(context_tile, ((TILE - 256) // 2, (TILE - 256) // 2))
        canvas.paste(context_cell, (x0 + ROW_LABEL_W, table_y + 30))

        for method_idx, (method, label) in enumerate(METHODS):
            y = table_y + 30 + TILE + method_idx * TILE
            draw.text((x0 + 8, y + TILE // 2 - 12), label, fill="black", font=SMALL)
            for view_idx, view in enumerate(VIEWS):
                record = records.get((uid, method, view))
                if record is None:
                    raise SystemExit(f"missing render manifest row for {uid}/{method}/view_{view:03d}")
                render_path = args.native_render_root / record["render_path"]
                if sha256(render_path) != record["render_sha256"]:
                    raise SystemExit(f"render hash mismatch: {render_path}")
                glb_path = Path(record["source_glb"])
                if sha256(glb_path) != record["source_glb_sha256"]:
                    raise SystemExit(f"GLB hash mismatch: {glb_path}")
                metadata_path = glb_path.parent / "bake_metadata.json"
                if sha256(metadata_path) != record["source_bake_metadata_sha256"]:
                    raise SystemExit(f"bake metadata hash mismatch: {metadata_path}")
                camera_peers = [
                    records[(uid, peer, view)]["camera_sha256"] for peer in methods
                ]
                if len(set(camera_peers)) != 1:
                    raise SystemExit(f"camera mismatch for {uid}/view_{view:03d}")
                if record["sampler"] != {"magFilter": 9729, "minFilter": 9987, "wrapS": 10497, "wrapT": 10497}:
                    raise SystemExit(f"unexpected sampler semantics for {uid}/{method}")
                tile = Image.open(render_path).convert("RGB")
                if tile.size != (512, 512):
                    raise SystemExit(f"unexpected render dimensions {tile.size}: {render_path}")
                tile = tile.resize((TILE, TILE), Image.Resampling.LANCZOS)
                canvas.paste(tile, (x0 + ROW_LABEL_W + TILE * (1 + view_idx), y))
                verified_pngs += 1
                verified_glbs += 1
                rows_out.append({
                    "selection_role": role,
                    "object_uid": uid,
                    "selection_rule": "C3-GFL object-level mean FG-PSNR over 11 frozen unseen views: minimum, closest to sample median, maximum; UID lexical tie-break",
                    "delta_c3_minus_gfl_fg_psnr_db": f"{delta:.12g}",
                    "method": method,
                    "render_view_id": view,
                    "render_path": str(render_path),
                    "render_sha256": record["render_sha256"],
                    "source_glb_path": str(glb_path),
                    "source_glb_sha256": record["source_glb_sha256"],
                    "bake_metadata_sha256": record["source_bake_metadata_sha256"],
                    "camera_sha256": record["camera_sha256"],
                    "sampler_json": json.dumps(record["sampler"], sort_keys=True),
                    "seed": 42,
                    "source_checkpoint_sha256": campaign["checkpoint_sha256"],
                    "source_campaign_manifest_sha256": sha256(args.b3_campaign_manifest),
                    "glb_lineage_sha256": sha256(args.glb_lineage),
                    "original_uv_status": "preserved by historical CPU bake; see GLB-native render audit; no new bake",
                    "gt_context_panel_path": str(context_path),
                    "gt_context_panel_sha256": context_hash,
                    "gt_context_view_id": 0,
                    "render_scope": "unlit base-color only; no PBR, human fidelity, or seam endpoint",
                    "redistribution_status": "UNKNOWN; INTERNAL REVIEW ONLY; do not publish until mesh/image rights are cleared",
                    "paired_results_csv_sha256": sha256(args.paired_results),
                    "render_manifest_sha256": sha256(manifest_path),
                    "renderer_script_sha256": renderer_hash,
                    "metrics_source_csv_sha256": metrics_hash,
                    "figure_output_path": str(args.output_png),
                })

    args.output_png.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output_png, format="PNG", optimize=False)
    figure_hash = sha256(args.output_png)
    for row in rows_out:
        row["figure_output_sha256"] = figure_hash
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_out[0]))
        writer.writeheader()
        writer.writerows(rows_out)

    print(json.dumps({
        "status": "PASS_INTERNAL_CANDIDATE",
        "selected_objects": [{"role": role, "uid": uid, "delta_db": delta} for role, uid, delta in deltas],
        "verified_render_pngs": verified_pngs,
        "verified_glb_references": verified_glbs,
        "output_png": str(args.output_png),
        "output_sha256": figure_hash,
        "redistribution": "UNKNOWN; output is internal-only",
    }, indent=2))


if __name__ == "__main__":
    main()
