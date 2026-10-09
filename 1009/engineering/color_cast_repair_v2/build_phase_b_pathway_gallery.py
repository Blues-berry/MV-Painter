#!/usr/bin/env python3
"""Build a SHA-verified development gallery for the Phase B appearance pathway."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

HERE = Path(__file__).resolve().parent
RUN = HERE / "runs/phase_b"
DEV = HERE / "runs/phase_c/dev"
OUT = HERE / "A_COLOR_PATHWAY_GALLERY.pdf"
CONDITIONS = (
    ("no_adapter", "No Adapter"),
    ("gfl_baseline", "GFL"),
    ("global_embedding_recomputed", "GFL, recomputed global embedding"),
    ("layer_llh", "LLH"),
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def sha_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def add(ax, path: str, title: str) -> None:
    ax.imshow(Image.open(path).convert("RGB"))
    ax.set_title(title, fontsize=11)
    ax.set_xticks([])
    ax.set_yticks([])


def main() -> None:
    b_rows = rows(RUN / "COLOR_INTERVENTION_RESULTS.csv")
    c_rows = rows(DEV / "C_REPAIR_PAIRED_RESULTS.csv")
    by_uid = {row["uid"]: row for row in c_rows if row["view_idx"] == "0"}
    selection = []
    with PdfPages(OUT) as pdf:
        for uid in sorted(by_uid):
            c = by_uid[uid]
            panels = [
                ("Transformed `cond_imgs`", c["source_condition_png"], c["source_condition_png_sha256"]),
                ("GT unique6; first tile is reference view", c["gt_sixview_png"], c["gt_sixview_png_sha256"]),
            ]
            for condition, label in CONDITIONS:
                matches = [row for row in b_rows if row["uid"] == uid
                           and row["condition"] == condition and row["target_tile_index"] == "0"]
                if len(matches) != 1:
                    raise ValueError(f"{uid}/{condition}: expected one reference-tile row")
                row = matches[0]
                panels.append((label, row["prediction_png"], row["prediction_png_sha256"]))
            for _, path, expected in panels:
                if sha_file(path) != expected:
                    raise ValueError(f"image SHA mismatch: {path}")
            fig, axes = plt.subplots(2, 3, figsize=(17, 12))
            for ax, (title, path, _) in zip(axes.ravel(), panels):
                add(ax, path, title)
            fig.suptitle(f"{uid}\n{c['source_cohort']} — development only", fontsize=14, y=0.99)
            fig.tight_layout(rect=(0.02, 0.02, 0.98, 0.94))
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
            selection.append({
                "uid": uid,
                "source_cohort": c["source_cohort"],
                "panels": [{"title": title, "path": path, "sha256": expected}
                           for title, path, expected in panels],
            })
    manifest = {
        "scope": "four locked Phase B development objects; no Fresh B prediction or repair metric opened",
        "pdf": str(OUT.resolve()),
        "pdf_sha256": sha_file(OUT),
        "pages": selection,
    }
    OUT.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": "complete", "pages": len(selection), "pdf": str(OUT.resolve())}, indent=2))


if __name__ == "__main__":
    main()
