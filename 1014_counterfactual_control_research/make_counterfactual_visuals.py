#!/usr/bin/env python3
"""Create contact sheets of the actual native-EGL unseen-view outputs."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/4T/CXY/MV-Painter/1014_counterfactual_control_research")
UIDS = [
    "1dc2c857f7614caeb6c2aa0559ccf973",
    "21678bd623654182b52c11d013de4e71",
    "238ff3e41c964655b83aa9c8770cc766",
    "2dd9bc8172c6461797947cc7214db399",
    "2f6c94487ee54cb88021f4643409d849",
    "e261c0fe85af46388260e2359a9bfc92",
]
METHODS = ("counterfactual_b0", "counterfactual_bplus", "counterfactual_bminus")
LABELS = {"counterfactual_b0": "B0", "counterfactual_bplus": "B+", "counterfactual_bminus": "B-"}
RENDERS = ROOT / "bake" / "native_egl_unseen"
OUT = ROOT / "visuals"
TILE = 160
HEADER = 34
DETAIL_TILE = 384


def load_view(uid: str, method: str, view: int) -> Image.Image:
    path = RENDERS / method / uid / "unseen_renders" / f"view_{view:03d}.png"
    with Image.open(path) as image:
        return image.convert("RGB").resize((TILE, TILE), Image.Resampling.LANCZOS)


def load_texture(uid: str, method: str) -> Image.Image:
    path = ROOT / "bake" / method / uid / f"{uid}_{method}_texture.png"
    with Image.open(path) as image:
        return image.convert("RGB").resize((DETAIL_TILE, DETAIL_TILE), Image.Resampling.LANCZOS)


def load_generation_panel(uid: str, method: str) -> Image.Image:
    path = ROOT / "generation" / "predictions" / method / f"{uid}.png"
    with Image.open(path) as image:
        return image.convert("RGB").resize((DETAIL_TILE, DETAIL_TILE * 2 // 3), Image.Resampling.LANCZOS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    object_index = {uid: index for index, uid in enumerate(UIDS)}
    width = 3 * 4 * TILE
    row_height = HEADER + 3 * TILE + 24
    sheet = Image.new("RGB", (width, len(UIDS) * row_height), "white")
    draw = ImageDraw.Draw(sheet)
    for uid in UIDS:
        top = object_index[uid] * row_height
        draw.text((4, top + 4), f"{object_index[uid]}  {uid}", fill="black")
        for method_index, method in enumerate(METHODS):
            x0 = method_index * 4 * TILE
            draw.text((x0 + 4, top + 4), LABELS[method], fill="black")
            for i, view in enumerate(range(1, 12)):
                row, col = divmod(i, 4)
                x, y = x0 + col * TILE, top + HEADER + row * TILE
                sheet.paste(load_view(uid, method, view), (x, y))
                draw.rectangle((x, y, x + TILE - 1, y + TILE - 1), outline=(210, 210, 210))
                draw.text((x + 3, y + 3), f"v{view}", fill="white", stroke_width=1, stroke_fill="black")

        # A full-height three-column grid for each object, with all 11 camera renders.
        detail = Image.new("RGB", (3 * TILE, HEADER + 11 * TILE), "white")
        dd = ImageDraw.Draw(detail)
        for mi, method in enumerate(METHODS):
            dd.text((mi * TILE + 4, 6), LABELS[method], fill="black")
            for view in range(1, 12):
                x, y = mi * TILE, HEADER + (view - 1) * TILE
                detail.paste(load_view(uid, method, view), (x, y))
                dd.rectangle((x, y, x + TILE - 1, y + TILE - 1), outline=(210, 210, 210))
                dd.text((x + 3, y + 3), f"raw view {view}", fill="white", stroke_width=1, stroke_fill="black")
        detail.save(OUT / f"UNSEEN_11VIEW_COMPARE_{uid}.png", optimize=True)

        texture_sheet = Image.new("RGB", (3 * DETAIL_TILE, HEADER + DETAIL_TILE), "white")
        texture_draw = ImageDraw.Draw(texture_sheet)
        panel_sheet = Image.new("RGB", (3 * DETAIL_TILE, HEADER + DETAIL_TILE * 2 // 3), "white")
        panel_draw = ImageDraw.Draw(panel_sheet)
        for mi, method in enumerate(METHODS):
            texture_draw.text((mi * DETAIL_TILE + 4, 6), LABELS[method], fill="black")
            x, y = mi * DETAIL_TILE, HEADER
            texture_sheet.paste(load_texture(uid, method), (x, y))
            texture_draw.rectangle((x, y, x + DETAIL_TILE - 1, y + DETAIL_TILE - 1), outline=(210, 210, 210))
            panel_draw.text((mi * DETAIL_TILE + 4, 6), LABELS[method], fill="black")
            panel_sheet.paste(load_generation_panel(uid, method), (mi * DETAIL_TILE, HEADER))
        texture_sheet.save(OUT / f"UV_TEXTURES_{uid}.png", optimize=True)
        panel_sheet.save(OUT / f"GENERATED_SIX_VIEW_PANELS_{uid}.png", optimize=True)

    sheet.save(OUT / "ALL_OBJECTS_ALL_CONDITIONS_11VIEWS.png", optimize=True)
    uids = "\n".join(
        f"- `{uid}`: [11 unseen views](UNSEEN_11VIEW_COMPARE_{uid}.png) · "
        f"[baked UV maps](UV_TEXTURES_{uid}.png) · "
        f"[six-view generation panels](GENERATED_SIX_VIEW_PANELS_{uid}.png)"
        for uid in UIDS
    )
    (OUT / "README.md").write_text(
        "# Actual baked-object views\n\n"
        "The 11-view sheets contain untouched native-EGL camera renders of the baked GLBs. "
        "The UV sheets compare the actual baked textures; the panel sheets show the six generated views. "
        "Original 512×512 renders, textured GLBs and 1024×1024 UV textures remain under `../bake/`.\n\n"
        "## Per object\n\n" + uids + "\n"
    )
    print(f"Wrote {len(UIDS)} detailed sheets and {OUT / 'ALL_OBJECTS_ALL_CONDITIONS_11VIEWS.png'}")


if __name__ == "__main__":
    main()
