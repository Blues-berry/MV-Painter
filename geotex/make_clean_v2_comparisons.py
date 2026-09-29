"""Create paper-ready contact sheets from the frozen clean-v2 PNG outputs."""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "final/round2/main_adapter_clean_v2/comparisons"
PRED = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/eval300_clean_v2_unique6/predictions"
COHORT = ROOT / "final/round2/main_adapter_clean_v2/exact_baking_cohort_manifest.csv"
METHODS = ("ground_truth", "no_adapter", "fixed_low", "fixed_high", "c3")
LABELS = {"ground_truth": "GT", "no_adapter": "No adapter", "fixed_low": "Fixed low", "fixed_high": "Fixed high", "c3": "C3"}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    rows = list(csv.DictReader(COHORT.open()))
    for row in rows:
        object_id = row["object"]
        images = [Image.open(PRED / method / f"{object_id}.png").convert("RGB") for method in METHODS]
        w, h = images[0].size
        strip = Image.new("RGB", (w * len(images), h + 24), "white")
        draw = ImageDraw.Draw(strip)
        for index, (method, image) in enumerate(zip(METHODS, images)):
            strip.paste(image, (index * w, 24))
            draw.text((index * w + 6, 6), LABELS[method], fill="black", font=font)
        strip.save(OUT / f"{object_id}_full_object_comparison.png")

    # A compact contact sheet using the three most interpretable conditions.
    thumbs = []
    for row in rows:
        object_id = row["object"]
        base = Image.open(PRED / "ground_truth" / f"{object_id}.png").convert("RGB")
        c3 = Image.open(PRED / "c3" / f"{object_id}.png").convert("RGB")
        no = Image.open(PRED / "no_adapter" / f"{object_id}.png").convert("RGB")
        thumb_w, thumb_h = 256, 384
        card = Image.new("RGB", (thumb_w * 3, thumb_h + 20), "white")
        draw = ImageDraw.Draw(card)
        for i, (label, image) in enumerate((("GT", base), ("No", no), ("C3", c3))):
            card.paste(image.resize((thumb_w, thumb_h)), (i * thumb_w, 20))
            draw.text((i * thumb_w + 4, 4), label, fill="black", font=font)
        thumbs.append(card)
    cols = 2
    rows_n = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (thumbs[0].width * cols, thumbs[0].height * rows_n), "white")
    for i, card in enumerate(thumbs):
        sheet.paste(card, ((i % cols) * card.width, (i // cols) * card.height))
    sheet.save(OUT / "exact_cohort_contact_sheet.png")
    print(f"wrote {len(rows)} comparison strips and one contact sheet to {OUT}")


if __name__ == "__main__":
    main()
