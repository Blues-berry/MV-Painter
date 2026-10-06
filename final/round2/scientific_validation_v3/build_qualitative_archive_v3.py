#!/usr/bin/env python3
"""Experiment D — formal qualitative archive builder.

For the frozen 24-object visualization set, composes per-object panels and a
full 24-object contact sheet from:
  * GT: the six target views of the fresh render tree (unique6 order)
  * conditions: byte-frozen prediction grids from the formal campaigns

Selection rule (pre-registered): the 24 objects were frozen BEFORE method
metrics (visualization_24.txt); no representative/cherry-picked imagery.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path("/4T/CXY/MV-Painter")
V3 = ROOT / "final/round2/scientific_validation_v3"
FORMAL = V3 / "formal"
RENDER_ROOT = ROOT / "data/fresh_confirm_v3_renders"
TARGET_VIEWS = [0, 15, 12, 16, 13, 14]  # unique6 generation order

CONDITIONS = [
    ("no_adapter", "campaign_B3"),
    ("native_gfl", "campaign_B3"),
    ("native_gfh", "campaign_B3"),
    ("native_gc3", "campaign_B3"),
    ("lfm_exact", "campaign_B1B2"),
    ("layer_lhl", "campaign_B1B2"),
    ("layer_llh", "campaign_B1B2"),
]

PANEL_W, PANEL_H, ROW_H = 512, 768, 30


def gt_grid(uid: str) -> Image.Image:
    """GT panel: unique6 target views in the same 3x2 slot layout."""
    canvas = Image.new("RGB", (PANEL_W, PANEL_H))
    for slot, v in enumerate(TARGET_VIEWS):
        col, row = slot % 2, slot // 2
        img = Image.open(RENDER_ROOT / uid / "image" / f"{v:03d}.png").convert("RGB")
        # composite over white using alpha (GT renders are RGBA)
        rgba = Image.open(RENDER_ROOT / uid / "image" / f"{v:03d}.png").convert("RGBA")
        bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        bg.alpha_composite(rgba)
        canvas.paste(bg.convert("RGB"), (col * 256, row * 256))
    return canvas


def pred_panel(uid: str, cond: str, campaign: str) -> Image.Image | None:
    p = FORMAL / campaign / "predictions" / cond / f"{uid}.png"
    if not p.exists():
        return None
    return Image.open(p).convert("RGB")


def labeled(img: Image.Image, text: str) -> Image.Image:
    out = Image.new("RGB", (img.width, img.height + ROW_H), (255, 255, 255))
    out.paste(img, (0, ROW_H))
    ImageDraw.Draw(out).text((6, 7), text, fill=(0, 0, 0))
    return out


def main() -> None:
    viz24 = [l.strip() for l in (V3 / "visualization_24.txt").open() if l.strip()]
    out_dir = V3 / "formal_qualitative_archive"
    out_dir.mkdir(exist_ok=True)

    missing = 0
    contact = Image.new("RGB", (PANEL_W * 8, (PANEL_H + ROW_H) * len(viz24)), (255, 255, 255))
    for i, uid in enumerate(viz24):
        rows = [("GT (views 0,15,12,16,13,14)", gt_grid(uid))]
        for cond, campaign in CONDITIONS:
            img = pred_panel(uid, cond, campaign)
            if img is None:
                missing += 1
                rows.append((cond, Image.new("RGB", (PANEL_W, PANEL_H), (200, 200, 200))))
            else:
                rows.append((cond, img))
        y = i * (PANEL_H + ROW_H)
        for j, (label, img) in enumerate(rows):
            contact.paste(labeled(img, f"{uid[:12]} | {label}"), (j * PANEL_W, y))
        # per-object panel file
        panel = Image.new("RGB", (PANEL_W * 8, PANEL_H + ROW_H), (255, 255, 255))
        for j, (label, img) in enumerate(rows):
            panel.paste(labeled(img, label), (j * PANEL_W, 0))
        panel.save(out_dir / f"panel_{i:02d}_{uid}.png")

    contact.save(out_dir / "contact_sheet_24.png")
    (out_dir / "archive_manifest.json").write_text(json.dumps({
        "objects": viz24,
        "conditions": [c for c, _ in CONDITIONS],
        "missing_panels": missing,
        "selection": "frozen visualization_24.txt (GT-only stratification, seed 20261002, pre-outcome)",
    }, indent=2) + "\n")
    print(f"wrote {out_dir}/contact_sheet_24.png + 24 panels; missing: {missing}")


if __name__ == "__main__":
    sys.exit(main())
