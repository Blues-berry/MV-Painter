#!/usr/bin/env python3
"""Extract illustrative input/output thumbnails from the archived 01549 Fig. 1."""
from __future__ import annotations

import subprocess
import tempfile
import csv
import hashlib
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "source_01549" / "fig1.pdf"
OUTPUT = ROOT / "fig1_assets"

# Pixel boxes measured on the original 1800 x 1110 preview, then scaled to the
# embedded raster's native resolution. The original PDF is retained unchanged.
PREVIEW_SIZE = (1800, 1110)
CROPS = {
    "reference.png": (75, 220, 220, 288),
    "normal.png": (75, 505, 220, 577),
    "depth.png": (75, 682, 220, 781),
    "mask.png": (75, 875, 220, 982),
    "target_views.png": (1493, 216, 1662, 333),
}


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fig1_01549_") as tmp:
        prefix = Path(tmp) / "source"
        subprocess.run(["pdfimages", "-png", str(SOURCE), str(prefix)], check=True)
        rasters = sorted(Path(tmp).glob("source-*.png"))
        if len(rasters) != 1:
            raise RuntimeError(f"Expected one raster in the archived Fig. 1; found {len(rasters)}")
        crop_rows = []
        with Image.open(rasters[0]) as original:
            sx = original.width / PREVIEW_SIZE[0]
            sy = original.height / PREVIEW_SIZE[1]
            for filename, box in CROPS.items():
                crop = tuple(round(v * (sx if i % 2 == 0 else sy))
                             for i, v in enumerate(box))
                output = OUTPUT / filename
                original.crop(crop).save(output, optimize=True)
                crop_rows.append((filename, ",".join(map(str, box)),
                                  hashlib.sha256(output.read_bytes()).hexdigest()))
        manifest = OUTPUT / "FIG1_THUMBNAIL_PROVENANCE.csv"
        with manifest.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["asset", "source_pdf", "source_pdf_sha256",
                             "crop_box_preview_1800x1110", "asset_sha256",
                             "role"])
            source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
            for filename, box, crop_hash in crop_rows:
                role = "illustrative reference/geometry input" if filename != "target_views.png" else "illustrative six target views"
                writer.writerow([filename, "source_01549/fig1.pdf", source_hash,
                                 box, crop_hash, role])
    print(f"Extracted {len(CROPS)} illustrative crops into {OUTPUT}")


if __name__ == "__main__":
    main()
