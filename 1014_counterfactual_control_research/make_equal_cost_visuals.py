#!/usr/bin/env python3
"""Visualize both Fixed Mean latent candidates for each study object."""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path("/4T/CXY/MV-Painter/1014_counterfactual_control_research")
ALT = Path("/4T/tmp/MV-Painter-local-excluded-20261013/1014_counterfactual_control_research")
UIDS = [
    "1dc2c857f7614caeb6c2aa0559ccf973",
    "21678bd623654182b52c11d013de4e71",
    "238ff3e41c964655b83aa9c8770cc766",
    "2dd9bc8172c6461797947cc7214db399",
    "2f6c94487ee54cb88021f4643409d849",
    "e261c0fe85af46388260e2359a9bfc92",
]
OUT = ROOT / "visuals"
TILE = 256
HEADER = 48


def load(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGB").resize(size, Image.Resampling.LANCZOS)


def main() -> None:
    gen42 = ALT / "generation/predictions/counterfactual_b0"
    gen43 = ALT / "generation_equal_cost_b0_seed43/predictions/counterfactual_b0"
    render42 = ALT / "bake/native_egl_unseen/counterfactual_b0"
    render43 = ALT / "bake_equal_cost_b0_seed43/native_egl_unseen/counterfactual_b0_seed43"
    result_rows = {r["object_uid"]: r for r in csv.DictReader(
        (ROOT / "EQUAL_COST_CANDIDATE_SELECTION_RESULTS.csv").open()
    )}
    for uid in UIDS:
        row = result_rows[uid]
        panels = Image.new("RGB", (2 * 384, HEADER + 256), "white")
        draw = ImageDraw.Draw(panels)
        draw.text((4, 4), f"seed42  reference MAE {float(row['seed42_reference_mae']):.4f}", fill="black")
        draw.text((388, 4), f"seed43  reference MAE {float(row['seed43_reference_mae']):.4f}", fill="black")
        panels.paste(load(gen42 / f"{uid}.png", (384, 256)), (0, HEADER))
        panels.paste(load(gen43 / f"{uid}.png", (384, 256)), (384, HEADER))
        panels.save(OUT / f"EQUAL_COST_GENERATION_PANELS_{uid}.png", optimize=True)

        renders = Image.new("RGB", (2 * TILE, HEADER + 11 * TILE), "white")
        draw = ImageDraw.Draw(renders)
        draw.text((4, 4), f"seed42  baked LPIPS {float(row['fixed_mean_seed42_bake_lpips']):.4f}", fill="black")
        draw.text((TILE + 4, 4), f"seed43  baked LPIPS {float(row['fixed_mean_seed43_bake_lpips']):.4f}", fill="black")
        for view in range(1, 12):
            y = HEADER + (view - 1) * TILE
            for col, directory in enumerate((render42, render43)):
                path = directory / uid / "unseen_renders" / f"view_{view:03d}.png"
                x = col * TILE
                renders.paste(load(path, (TILE, TILE)), (x, y))
                draw.rectangle((x, y, x + TILE - 1, y + TILE - 1), outline=(210, 210, 210))
                draw.text((x + 4, y + 4), f"view {view}", fill="white", stroke_width=1, stroke_fill="black")
        renders.save(OUT / f"EQUAL_COST_UNSEEN_11VIEW_{uid}.png", optimize=True)

    readme = OUT / "README.md"
    with readme.open("a") as stream:
        stream.write("\n## Equal-cost Fixed Mean candidate views\n\n")
        for uid in UIDS:
            stream.write(
                f"- `{uid}`: [seed-42/seed-43 generated panels](EQUAL_COST_GENERATION_PANELS_{uid}.png) · "
                f"[11 baked views](EQUAL_COST_UNSEEN_11VIEW_{uid}.png)\n"
            )
    print(f"Wrote equal-cost candidate views for {len(UIDS)} objects.")


if __name__ == "__main__":
    main()
