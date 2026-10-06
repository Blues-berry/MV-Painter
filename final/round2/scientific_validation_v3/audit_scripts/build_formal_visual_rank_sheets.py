#!/usr/bin/env python3
"""Apply the frozen visual rank rule and build deterministic evidence sheets."""
from __future__ import annotations

import csv
import hashlib
import json
import statistics
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
V3 = ROOT / "final/round2/scientific_validation_v3"
ARCHIVE = V3 / "formal_qualitative_archive"
OUT = V3 / "formal_visual_evidence"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_condition(run_dir: Path, condition: str) -> dict[str, dict]:
    csv_path = run_dir / f"{condition}_per_object_metrics.csv"
    if csv_path.exists():
        with csv_path.open() as f:
            return {r["object_uid"]: r for r in csv.DictReader(f)}
    result = {}
    for p in sorted(run_dir.glob("rows_shard*.json")):
        for row in json.loads(p.read_text()):
            if row["condition"] == condition:
                result[row["object_uid"]] = row
    return result


def label_panel(uid: str, title: str) -> Image.Image:
    manifest = json.loads((ARCHIVE / "archive_manifest.json").read_text())
    index = manifest["objects"].index(uid)
    panel = Image.open(ARCHIVE / f"panel_{index:02d}_{uid}.png").convert("RGB")
    strip = Image.new("RGB", (panel.width, 62), "white")
    draw = ImageDraw.Draw(strip)
    draw.text((16, 12), f"{title} — {uid}", fill="black", font=ImageFont.load_default(size=32))
    out = Image.new("RGB", (panel.width, panel.height + strip.height), "white")
    out.paste(strip, (0, 0)); out.paste(panel, (0, strip.height))
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    uid_file = V3 / "visualization_24.txt"
    uids = uid_file.read_text().splitlines()
    archive = json.loads((ARCHIVE / "archive_manifest.json").read_text())
    if uids != archive["objects"] or len(uids) != 24:
        raise RuntimeError("frozen visualization cohort/order mismatch")

    llh = read_condition(V3 / "formal/campaign_B1B2", "layer_llh")
    gfl = read_condition(V3 / "formal/campaign_B3", "native_gfl")
    if len(llh) != 300 or len(gfl) != 300 or not set(uids) <= set(llh) & set(gfl):
        raise RuntimeError("rank metrics do not cover all 24 frozen visual UIDs")
    deltas = {u: float(llh[u]["fg_psnr"]) - float(gfl[u]["fg_psnr"]) for u in uids}
    ordered = sorted(uids, key=lambda u: (deltas[u], u))
    median_value = statistics.median(deltas.values())
    median_uid = min(uids, key=lambda u: (abs(deltas[u] - median_value), u))
    selected = {
        "median_effect": median_uid,
    }
    # Apply the explicit lexicographic tie-break, including extreme ties.
    selected["strongest_win"] = min((u for u in uids if deltas[u] == max(deltas.values())))
    selected["strongest_loss"] = min((u for u in uids if deltas[u] == min(deltas.values())))

    gt = json.loads((V3 / "gt_stats.json").read_text())
    lap = gt["gt_fg_lap_var"]
    texture_rich = sorted(uids, key=lambda u: (-float(lap[u]), u))[:6]
    manifest = {
        "rule": "FORMAL_VISUAL_RANK_PROTOCOL.md",
        "rank_metric": "FG-PSNR(layer_llh) - FG-PSNR(native_gfl), higher favors LLH",
        "cohort": str(uid_file.relative_to(ROOT)),
        "cohort_n": len(uids),
        "source_metric_ledgers": {
            "LLH": {"path": str((V3 / "formal/campaign_B1B2/per_object_metrics.csv").relative_to(ROOT)),
                    "sha256": sha(V3 / "formal/campaign_B1B2/per_object_metrics.csv")},
            "GFL": {"path": str((V3 / "formal/campaign_B3/per_object_metrics.csv").relative_to(ROOT)),
                    "sha256": sha(V3 / "formal/campaign_B3/per_object_metrics.csv")},
            "GT_statistics": {"path": str((V3 / "gt_stats.json").relative_to(ROOT)),
                              "sha256": sha(V3 / "gt_stats.json")},
        },
        "ranked_examples": {
            rank: {"uid": uid, "llh_minus_gfl_fg_psnr_db": deltas[uid],
                   "rank_position_ascending": ordered.index(uid) + 1}
            for rank, uid in selected.items()
        },
        "median_score": median_value,
        "texture_rich_failure_uids_gt_laplacian_top6": [
            {"uid": u, "gt_fg_lap_var": float(lap[u])} for u in texture_rich
        ],
        "interpretation": "rank-selected examples from the already frozen 24; illustrative only, not an independent estimate",
    }
    (OUT / "VISUAL_RANK_SELECTIONS.json").write_text(json.dumps(manifest, indent=2) + "\n")

    for rank, uid in selected.items():
        panel = label_panel(uid, f"{rank}; delta FG-PSNR LLH-GFL = {deltas[uid]:+.3f} dB")
        panel.save(OUT / f"{rank}.png", optimize=False)

    labeled = [label_panel(u, f"GT Laplacian Q4; GT LapVar={float(lap[u]):.4g}") for u in texture_rich]
    width = max(im.width for im in labeled); height = max(im.height for im in labeled)
    sheet = Image.new("RGB", (2 * width, 3 * height), "white")
    for i, im in enumerate(labeled):
        sheet.paste(im, ((i % 2) * width, (i // 2) * height))
    sheet.save(OUT / "texture_rich_failure_sheet.png", optimize=False)

    print(json.dumps({"selected": manifest["ranked_examples"],
                      "texture_rich_uids": [x["uid"] for x in manifest["texture_rich_failure_uids_gt_laplacian_top6"]]}, indent=2))


if __name__ == "__main__":
    main()
