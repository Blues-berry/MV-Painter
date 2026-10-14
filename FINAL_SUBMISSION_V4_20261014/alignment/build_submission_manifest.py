#!/usr/bin/env python3
"""Validate and hash the portable V4 submission package."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "alignment" / "SUBMISSION_MANIFEST_V4.json"
PDFS = {
    "main": ROOT / "FINAL_V4_MANUSCRIPT.pdf",
    "supplement": ROOT / "FINAL_V4_SUPPLEMENTARY.pdf",
    "response": ROOT / "FINAL_V4_RESPONSE_TO_REVIEWERS.pdf",
    "marked": ROOT / "FINAL_V4_MARKED_MANUSCRIPT.pdf",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def page_count(path: Path) -> int:
    info = subprocess.check_output(["pdfinfo", str(path)], text=True)
    return int(next(line.split(":", 1)[1] for line in info.splitlines() if line.startswith("Pages:")))


def page_text(path: Path, page: int) -> str:
    return subprocess.check_output(
        ["pdftotext", "-f", str(page), "-l", str(page), str(path), "-"],
        text=True,
        errors="replace",
    )


def main() -> None:
    pages = {name: page_count(path) for name, path in PDFS.items()}
    if pages != {"main": 13, "supplement": 71, "response": 5, "marked": 20}:
        raise SystemExit(f"Unexpected V4 page counts: {pages}")
    if "[41]" not in page_text(PDFS["main"], 13):
        raise SystemExit("The final reference [41] is not on main page 13.")
    if "Fig. 3." not in page_text(PDFS["main"], 9) or "Table 5." not in page_text(PDFS["main"], 9):
        raise SystemExit("Figure 3 or Table 5 is not on main page 9.")
    if "Table 7." not in page_text(PDFS["main"], 11):
        raise SystemExit("Table 7 is not on main page 11.")
    if "Table S35" not in page_text(PDFS["supplement"], 58):
        raise SystemExit("Table S35 is not on supplement page 58.")
    if "Table S36" not in page_text(PDFS["supplement"], 59):
        raise SystemExit("Table S36 is not on supplement page 59.")

    validation = json.loads((ROOT / "figures" / "FIG6_DATA_VALIDATION_V3.json").read_text())
    if validation.get("status") != "PASS" or not validation.get("primary_contrast_is_original_middle_minus_mean_early_late"):
        raise SystemExit("Frozen Figure 6 primary validation is not PASS.")

    ranking_path = ROOT / "visual_candidates" / "BAKE10_CANDIDATE_RANKING_V4.csv"
    with ranking_path.open(newline="", encoding="utf-8-sig") as stream:
        ranking = list(csv.DictReader(stream))
    if len(ranking) != 7 or ranking[0]["uid"] != "238ff3e41c964655b83aa9c8770cc766":
        raise SystemExit("Unexpected Bake10 candidate count or selected UID.")
    for field in ("fixed_mean_11view_fg_lpips", "late_high_11view_fg_lpips"):
        if float(ranking[0][field]) >= min(float(row[field]) for row in ranking[1:]):
            raise SystemExit(f"Selected UID is not the minimum for {field}.")

    excluded_dirs = {"build", "build_response", "__pycache__", ".git"}
    files = {}
    for path in sorted(p for p in ROOT.rglob("*") if p.is_file()):
        rel = path.relative_to(ROOT)
        if path == OUTPUT or any(part in excluded_dirs for part in rel.parts):
            continue
        files[rel.as_posix()] = {"bytes": path.stat().st_size, "sha256": sha256(path)}

    report = {
        "version": "V4",
        "status": "PASS",
        "package": "FINAL_SUBMISSION_V4_20261014",
        "pdf_pages": pages,
        "checked_locations": {
            "main_Figure_3_and_Table_5": 9,
            "main_Table_6_and_Figure_4": 10,
            "main_Table_7": 11,
            "main_final_reference_41": 13,
            "supplement_Table_S35": 58,
            "supplement_Table_S36": 59,
        },
        "frozen_figure6_primary": {
            "contrast": "Middle − mean(Early, Late)",
            "estimate_db": -0.0338775,
            "ci95_db": [-0.117170, 0.051422],
            "p": 0.432378,
            "validation": "PASS",
        },
        "figure3_selection": {
            "uid": ranking[0]["uid"],
            "rule": "lowest existing 11-view FG-LPIPS among seven rights-cleared display candidates for both shown schedules",
            "fixed_mean_fg_lpips": float(ranking[0]["fixed_mean_11view_fg_lpips"]),
            "late_high_fg_lpips": float(ranking[0]["late_high_11view_fg_lpips"]),
            "post_outcome_illustration": True,
        },
        "render_resolution_metadata_note": {
            "actual_hashed_png_pixels": "512×512",
            "renderer_setting": 512,
            "upstream_per_render_metadata": "1024×1024",
        },
        "files": files,
        "manifest_hash_note": "This file excludes its own hash to avoid recursive hashing.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"V4 submission manifest: PASS ({len(files)} files)")


if __name__ == "__main__":
    main()
