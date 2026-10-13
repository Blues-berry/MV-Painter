#!/usr/bin/env python3
"""Build a labeled layout prototype, then a gate-controlled Fresh C gallery.

The prototype is deliberately retrospective and is never used to choose the
final Fresh C examples. The final mode refuses to run until both integrity
gates and the locked Fresh C analyses exist.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
V3 = ROOT / "final/round2/scientific_validation_v3"
DATA = ROOT / "1006/data/fresh_c"
FIGURES = ROOT / "1006/figures/strategy_comparison_gallery"
VIEWS = (0, 15, 12, 16, 13, 14)
CONDITIONS = (
    ("Reference", "__reference__"),
    ("GFL", "native_gfl"),
    ("GFH", "native_gfh"),
    ("No adapter", "no_adapter"),
    ("C3", "native_gc3"),
    ("LLH", "layer_llh"),
    ("Generic linear", "gen_linear"),
)
OLD_SOURCE = {
    "native_gfl": "campaign_B3",
    "native_gfh": "campaign_B3",
    "no_adapter": "campaign_B3",
    "native_gc3": "campaign_B3",
    "layer_llh": "campaign_B1B2",
    "gen_linear": "campaign_C",
}
PANEL_W, PANEL_H, LABEL_H = 512, 768, 38


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def font(size: int = 19) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"):
        if Path(path).is_file():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def text_fit(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str,
             max_width: int, face: ImageFont.ImageFont) -> None:
    while draw.textbbox((0, 0), value, font=face)[2] > max_width and len(value) > 5:
        value = value[:-4] + "..."
    draw.text(xy, value, fill=(20, 20, 20), font=face)


def reference_grid(render_root: Path, uid: str) -> Image.Image:
    canvas = Image.new("RGB", (PANEL_W, PANEL_H), "white")
    for slot, view in enumerate(VIEWS):
        path = render_root / uid / "image" / f"{view:03d}.png"
        if not path.is_file():
            raise FileNotFoundError(f"missing reference render: {path}")
        rgba = Image.open(path).convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        background.alpha_composite(rgba)
        tile = background.convert("RGB").resize((256, 256), Image.Resampling.LANCZOS)
        canvas.paste(tile, ((slot % 2) * 256, (slot // 2) * 256))
    return canvas


def load_panel(path: Path) -> Image.Image:
    if not path.is_file():
        raise FileNotFoundError(path)
    image = Image.open(path).convert("RGB")
    if image.size != (PANEL_W, PANEL_H):
        raise RuntimeError(f"unexpected comparison panel size {image.size}: {path}")
    return image


def compose(uid: str, panels: dict[str, Image.Image], title: str) -> Image.Image:
    out = Image.new("RGB", (PANEL_W * len(CONDITIONS), PANEL_H + 2 * LABEL_H), "white")
    draw = ImageDraw.Draw(out)
    for index, (label, condition) in enumerate(CONDITIONS):
        x = index * PANEL_W
        draw.rectangle((x, 0, x + PANEL_W - 1, LABEL_H - 1), fill=(247, 247, 247))
        text_fit(draw, (x + 7, 3), label, PANEL_W - 14, font(20))
        cell = panels[condition]
        out.paste(cell, (x, LABEL_H))
        ImageDraw.Draw(out).rectangle((x, LABEL_H, x + PANEL_W - 1, LABEL_H + PANEL_H - 1),
                                      outline=(210, 210, 210), width=1)
    draw.rectangle((0, LABEL_H + PANEL_H, out.width - 1, out.height - 1), fill=(250, 250, 250))
    text_fit(draw, (8, LABEL_H + PANEL_H + 7), f"{title} | UID {uid} | views {','.join(map(str, VIEWS))}",
             out.width - 16, font(18))
    return out


def historical_rows(uid: str) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    import csv as csv_module

    source_rows: dict[str, dict[str, Any]] = {}
    identities: dict[str, str] = {}
    for condition, campaign in OLD_SOURCE.items():
        path = V3 / "formal" / campaign / "rows_shard0.json"
        row_sets = []
        for ledger in sorted((V3 / "formal" / campaign).glob("rows_shard*.json")):
            for row in json.loads(ledger.read_text()):
                if row.get("condition") == condition and str(row.get("object_uid") or row.get("object")) == uid:
                    row_sets.append(row)
        if not row_sets:
            # Some compact campaign directories expose condition CSVs without
            # their raw shard ledger; use the frozen per-object table if needed.
            candidates = [V3 / "formal" / campaign / f"{condition}_per_object_metrics.csv",
                          V3 / "formal" / campaign / "per_object_metrics.csv"]
            for csv_path in candidates:
                if not csv_path.is_file():
                    continue
                with csv_module.DictReader(csv_path.open(newline="")) as reader:
                    row_sets = [r for r in reader if r.get("condition") == condition and
                                str(r.get("object_uid") or r.get("object")) == uid]
                if row_sets:
                    break
        if not row_sets:
            raise RuntimeError(f"no source row for historical prototype {condition}/{uid}")
        normalized = []
        for row in row_sets:
            normalized.append({k: v for k, v in row.items() if k != "elapsed_seconds"})
        if any(row != normalized[0] for row in normalized[1:]):
            raise RuntimeError(f"conflicting duplicate raw rows for {condition}/{uid}")
        row = row_sets[0]
        source_rows[condition] = row
        identities[condition] = campaign
    first = next(iter(source_rows.values()))
    shared_keys = ("object_idx", "seed_base", "input_hashes")
    for condition, row in source_rows.items():
        for key in shared_keys:
            if row.get(key) != first.get(key):
                raise RuntimeError(f"historical prototype sources differ at {condition}/{key}")
    if not isinstance(first.get("input_hashes"), dict):
        raise RuntimeError("historical prototype source rows lack six-input hashes")
    return source_rows, identities


def build_prototype() -> dict[str, Any]:
    uids = [line.strip() for line in (V3 / "visualization_24.txt").read_text().splitlines() if line.strip()]
    if len(uids) != 24 or len(set(uids)) != 24:
        raise RuntimeError("frozen Visualization-24 list is not 24 unique UIDs")
    uid = uids[0]  # frozen list order; selected before looking at this comparison
    rows, sources = historical_rows(uid)
    render_root = ROOT / "data/fresh_confirm_v3_renders"
    panels: dict[str, Image.Image] = {"__reference__": reference_grid(render_root, uid)}
    assets = {"reference": []}
    for view in VIEWS:
        assets["reference"].append({"view": view,
                                    "path": str((render_root / uid / "image" / f"{view:03d}.png").relative_to(ROOT)),
                                    "sha256": sha256(render_root / uid / "image" / f"{view:03d}.png")})
    for condition, campaign in sources.items():
        path = V3 / "formal" / campaign / "predictions" / condition / f"{uid}.png"
        panels[condition] = load_panel(path)
        assets[condition] = {"campaign": campaign, "path": str(path.relative_to(ROOT)),
                             "sha256": sha256(path)}
    image = compose(uid, panels, "LAYOUT QA ONLY — historical retrospective same-input cohort; not Fresh C")
    out_dir = FIGURES / "prototype"
    out_dir.mkdir(parents=True, exist_ok=True)
    image_path = out_dir / f"layout_qa_{uid}.png"
    image.save(image_path, optimize=False)
    manifest = {
        "status": "LAYOUT_QA_ONLY_NOT_FINAL_EVIDENCE",
        "selection": "first UID in the pre-outcome frozen Visualization-24 list; no outcome-based selection",
        "uid": uid, "n_frozen_visualization_uids": len(uids), "views": list(VIEWS),
        "conditions": [condition for _, condition in CONDITIONS],
        "source_cohort": "historical same-object/same-seed experiment rows; retrospective and cross-campaign",
        "source_campaign_by_condition": sources,
        "source_identity_checks": {
            "same_uid_and_object_index": True,
            "same_seed": True,
            "same_six_input_hashes": True,
            "runner_and_checkpoint_match_from_prior_audit": True,
            "legacy_config_hash_missing": True,
        },
        "metric_values_not_drawn_on_single_object_panel": True,
        "single_object_significance_claim": False,
        "output": str(image_path.relative_to(ROOT)),
        "assets": assets,
    }
    (out_dir / "layout_qa_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def rows_by_condition(path: Path) -> dict[str, dict[str, dict[str, Any]]]:
    result: dict[str, dict[str, dict[str, Any]]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            result.setdefault(row["condition"], {})[row["object_uid"]] = row
    return result


def load_fresh_rows() -> tuple[list[str], dict[str, dict[str, dict[str, Any]]]]:
    primary_gate = DATA / "FRESH_C_INTEGRITY_GATE.json"
    addendum_gate = DATA / "FRESH_C_ADDENDUM_INTEGRITY_GATE.json"
    primary_analysis = DATA / "fresh_c_c3_minus_gfl_analysis.json"
    addendum_analysis = DATA / "FRESH_C_ADDENDUM_ANALYSIS.json"
    for path in (primary_gate, addendum_gate, primary_analysis, addendum_analysis):
        if not path.is_file():
            raise RuntimeError(f"final Fresh C gallery prerequisite missing: {path}")
    for path in (primary_gate, addendum_gate):
        if json.loads(path.read_text()).get("status") != "PASS":
            raise RuntimeError(f"final Fresh C gallery refuses non-PASS integrity gate: {path}")
    uids = [line.strip() for line in (DATA / "fresh_c_objects.txt").read_text().splitlines() if line.strip()]
    primary_run = DATA / "runs/c3_confirmation"
    addendum_run = DATA / "runs/revision_era_addendum"
    all_rows = {}
    for condition, table in rows_by_condition(primary_run / "per_object_metrics.csv").items():
        all_rows[condition] = table
    for condition, table in rows_by_condition(addendum_run / "per_object_metrics.csv").items():
        if condition in all_rows:
            raise RuntimeError(f"condition duplicated across Fresh C primary/addendum: {condition}")
        all_rows[condition] = table
    expected = {condition for _, condition in CONDITIONS if condition != "__reference__"}
    if set(all_rows) != expected:
        raise RuntimeError(f"Fresh C condition coverage mismatch: {sorted(set(all_rows) ^ expected)}")
    for condition, table in all_rows.items():
        if set(table) != set(uids):
            raise RuntimeError(f"Fresh C metric UID coverage mismatch for {condition}")
    return uids, all_rows


def endpoint_class(psnr: float, lpips: float) -> str:
    a_psnr = psnr > 0
    a_lpips = lpips < 0
    if a_psnr and a_lpips:
        return "both_endpoints_favor_A"
    if psnr < 0 and lpips > 0:
        return "both_endpoints_favor_B"
    if psnr == 0 and lpips == 0:
        return "exact_tie"
    return "metric_tradeoff_or_partial_tie"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise RuntimeError(f"refusing to write empty table {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def plot_contrast_forest(rows: list[dict[str, Any]], path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    contrasts = ["C3-GFL", "LLH-C3", "LLH-linear", "C3-linear"]
    labels = {"C3-GFL": "C3 − GFL", "LLH-C3": "LLH − C3",
              "LLH-linear": "LLH − linear", "C3-linear": "C3 − linear"}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), constrained_layout=True)
    for ax, metric, xlabel in zip(axes, ("fg_psnr", "fg_lpips"),
                                  ("FG-PSNR difference (dB)", "FG-LPIPS difference")):
        selected = [row for row in rows if row["metric"] == metric and row["contrast"] in contrasts]
        selected.sort(key=lambda row: contrasts.index(row["contrast"]))
        for y, row in enumerate(selected):
            mean = float(row["mean_delta"])
            low, high = float(row["ci95_low"]), float(row["ci95_high"])
            color = "#0072B2" if row["contrast"] == "C3-GFL" else "#CC79A7"
            ax.errorbar(mean, y, xerr=[[mean - low], [high - mean]], fmt="o", color=color,
                        ecolor=color, capsize=3, markersize=5, linewidth=1.5)
        ax.axvline(0, color="#555555", linestyle="--", linewidth=1)
        ax.set_yticks(range(len(selected)), [labels[row["contrast"]] for row in selected])
        ax.invert_yaxis()
        ax.set_xlabel(xlabel)
        ax.grid(axis="x", alpha=0.25)
        ax.set_title("95% object-bootstrap intervals")
        for y, row in enumerate(selected):
            p = row.get("p_holm")
            p_label = f"Holm p={float(p):.3g}" if p not in (None, "") else "primary p unadjusted"
            ax.text(1.02, y, p_label, transform=ax.get_yaxis_transform(), va="center",
                    fontsize=8, clip_on=False)
    fig.suptitle("Fresh C revision-era paired strategy contrasts\n"
                 "A−B; lower FG-LPIPS favors A; no overall winner is ranked", fontsize=12)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def selection_candidates(rows: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """Rank representative objects by separate endpoints, never a composite."""
    if not rows:
        return []
    n = len(rows)
    psnr_high = sorted(rows, key=lambda r: (-float(r["delta_fg_psnr"]), r["object_uid"]))
    psnr_low = list(reversed(psnr_high))
    lpips_low = sorted(rows, key=lambda r: (float(r["delta_fg_lpips"]), r["object_uid"]))
    lpips_high = list(reversed(lpips_low))
    median_psnr = sorted(float(r["delta_fg_psnr"]) for r in rows)[(n - 1) // 2]
    psnr_median = sorted(rows, key=lambda r: (abs(float(r["delta_fg_psnr"]) - median_psnr), r["object_uid"]))
    strata = (
        (psnr_high, "highest_focal_FG_PSNR"),
        (psnr_low, "lowest_focal_FG_PSNR"),
        (psnr_median, "near_median_focal_FG_PSNR"),
        (lpips_low, "lowest_focal_FG_LPIPS"),
        (lpips_high, "highest_focal_FG_LPIPS"),
    )
    selected: list[tuple[str, str]] = []
    used: set[str] = set()
    for ordered, label in strata:
        for row in ordered:
            uid = row["object_uid"]
            if uid not in used:
                selected.append((uid, label))
                used.add(uid)
                break
    for row in psnr_high:
        uid = row["object_uid"]
        if uid not in used:
            selected.append((uid, "remaining_by_focal_FG_PSNR"))
            used.add(uid)
    return selected


def final_selected_uids(contrast_rows: dict[str, list[dict[str, Any]]], n: int) -> list[dict[str, str]]:
    """Balance the 20 examples across the four frozen named comparisons."""
    focus_order = ("C3-GFL", "LLH-C3", "LLH-linear", "C3-linear")
    target = min(20, n)
    if n < 20:
        return [{"object_uid": uid, "focal_contrast": "C3-GFL", "selection_stratum": label}
                for uid, label in selection_candidates(contrast_rows["C3-GFL"])[:target]]

    queues = {contrast: selection_candidates(contrast_rows[contrast]) for contrast in focus_order}
    cursors = {contrast: 0 for contrast in focus_order}
    selected: list[dict[str, str]] = []
    used: set[str] = set()
    quotas = {contrast: 5 for contrast in focus_order}
    while len(selected) < target:
        made_progress = False
        for contrast in focus_order:
            if sum(row["focal_contrast"] == contrast for row in selected) >= quotas[contrast]:
                continue
            while cursors[contrast] < len(queues[contrast]):
                uid, label = queues[contrast][cursors[contrast]]
                cursors[contrast] += 1
                if uid not in used:
                    selected.append({"object_uid": uid, "focal_contrast": contrast,
                                     "selection_stratum": label})
                    used.add(uid)
                    made_progress = True
                    break
        if not made_progress:
            # Candidate overlap is expected; fill remaining slots in a fixed
            # round-robin order while retaining the focal comparison label.
            for contrast in focus_order:
                while cursors[contrast] < len(queues[contrast]):
                    uid, label = queues[contrast][cursors[contrast]]
                    cursors[contrast] += 1
                    if uid not in used:
                        selected.append({"object_uid": uid, "focal_contrast": contrast,
                                         "selection_stratum": label})
                        used.add(uid)
                        made_progress = True
                        break
                if made_progress:
                    break
        if not made_progress:
            break
    return selected[:target]


def plot_strategy_ranking_pages(
    contrast_rows: dict[str, list[dict[str, Any]]],
    summary_rows: list[dict[str, Any]],
    output: Path,
) -> None:
    """Create separate endpoint pages for each named strategy versus GFL."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    page_dir = output / "strategy_ranking_pages"
    page_dir.mkdir(parents=True, exist_ok=True)
    pages = (("C3", "C3-GFL"), ("LLH", "LLH-GFL"), ("Generic linear", "linear-GFL"))
    summary_by_key = {(row["contrast"], row["metric"]): row for row in summary_rows}
    for label, contrast in pages:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
        for ax, metric, title, favorable in (
            (axes[0], "delta_fg_psnr", "FG-PSNR (higher favors strategy)", "higher"),
            (axes[1], "delta_fg_lpips", "FG-LPIPS (lower favors strategy)", "lower"),
        ):
            ordered = sorted(contrast_rows[contrast], key=lambda row: float(row[metric]))
            values = [float(row[metric]) for row in ordered]
            colors = ["#009E73" if (value > 0 if favorable == "higher" else value < 0)
                      else "#D55E00" if value != 0 else "#777777" for value in values]
            ax.scatter(values, range(len(values)), c=colors, s=9, linewidths=0)
            ax.axvline(0, color="#444444", linestyle="--", linewidth=1)
            ax.set_xlabel(f"A−GFL {metric.removeprefix('delta_')}")
            ax.set_title(title)
            ax.set_ylabel("Objects sorted independently by endpoint")
            ax.grid(axis="x", alpha=0.22)
            metric_key = "fg_psnr" if metric.endswith("psnr") else "fg_lpips"
            stats = summary_by_key.get((contrast, metric_key))
            if stats:
                p = stats.get("p_holm")
                p_label = "Holm p"
                if p in (None, ""):
                    p, p_label = stats.get("p_raw"), "primary raw p"
                detail = (f"mean={float(stats['mean_delta']):+.4g}; "
                          f"median={float(stats['median_delta']):+.4g}; "
                          f"favorable={float(stats['favorable_object_fraction_for_a']):.1%}")
                if p not in (None, ""):
                    detail += f"; {p_label}={float(p):.3g}"
            else:
                delta = np.asarray(values, dtype=float)
                fraction = float(np.mean(delta > 0 if favorable == "higher" else delta < 0))
                detail = (f"median={float(np.median(delta)):+.4g}; favorable={fraction:.1%}; "
                          "unregistered descriptive comparison; no inferential p")
            ax.text(0.02, 0.02, detail, transform=ax.transAxes, va="bottom", fontsize=8,
                    bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"})
        fig.suptitle(f"{label} versus GFL — endpoints ranked independently; no composite winner")
        fig.savefig(page_dir / f"{contrast.replace('-', '_')}.png", dpi=180, bbox_inches="tight")
        plt.close(fig)


def build_final() -> dict[str, Any]:
    uids, tables = load_fresh_rows()
    if len(uids) < 1:
        raise RuntimeError("empty Fresh C cohort")
    output = FIGURES / "fresh_c_final"
    (output / "panels").mkdir(parents=True, exist_ok=True)
    (output / "rankings").mkdir(parents=True, exist_ok=True)
    pairs = (
        ("C3-GFL", "native_gc3", "native_gfl", True),
        ("LLH-C3", "layer_llh", "native_gc3", True),
        ("LLH-linear", "layer_llh", "gen_linear", True),
        ("C3-linear", "native_gc3", "gen_linear", True),
        ("LLH-GFL", "layer_llh", "native_gfl", False),
        ("linear-GFL", "gen_linear", "native_gfl", False),
    )
    all_rank_rows = []
    contrast_rows: dict[str, list[dict[str, Any]]] = {}
    for name, a, b, locked_contrast in pairs:
        rows = []
        for uid in uids:
            a_row, b_row = tables[a][uid], tables[b][uid]
            d_psnr = float(a_row["fg_psnr"]) - float(b_row["fg_psnr"])
            d_lpips = float(a_row["fg_lpips"]) - float(b_row["fg_lpips"])
            row = {"contrast": name, "condition_a": a, "condition_b": b,
                   "object_uid": uid, "delta_fg_psnr": d_psnr,
                   "delta_fg_lpips": d_lpips,
                   "endpoint_pattern": endpoint_class(d_psnr, d_lpips),
                   "locked_named_contrast": locked_contrast,
                   "single_object_significance": "not_estimated"}
            rows.append(row)
        psnr_order = sorted(rows, key=lambda r: (-r["delta_fg_psnr"], r["object_uid"]))
        lpips_order = sorted(rows, key=lambda r: (r["delta_fg_lpips"], r["object_uid"]))
        p_rank = {r["object_uid"]: index + 1 for index, r in enumerate(psnr_order)}
        l_rank = {r["object_uid"]: index + 1 for index, r in enumerate(lpips_order)}
        for row in rows:
            row["rank_a_by_fg_psnr"] = p_rank[row["object_uid"]]
            row["rank_a_by_fg_lpips"] = l_rank[row["object_uid"]]
        write_csv(output / "rankings" / f"{name.replace('-', '_')}_all_objects.csv", rows)
        write_csv(output / "rankings" / f"{name.replace('-', '_')}_by_fg_psnr.csv", psnr_order)
        write_csv(output / "rankings" / f"{name.replace('-', '_')}_by_fg_lpips.csv", lpips_order)
        all_rank_rows.extend(rows)
        contrast_rows[name] = rows
    write_csv(output / "all_contrast_object_deltas.csv", all_rank_rows)

    selected = final_selected_uids(contrast_rows, len(uids))
    render_root = DATA / "renders"
    selection_rows = []
    figure_assets = []
    panels_for_sheet = []
    for index, selection in enumerate(selected, start=1):
        uid = selection["object_uid"]
        focal_contrast = selection["focal_contrast"]
        stratum = selection["selection_stratum"]
        panels = {"__reference__": reference_grid(render_root, uid)}
        for view in VIEWS:
            source = render_root / uid / "image" / f"{view:03d}.png"
            figure_assets.append({"panel_order": index, "object_uid": uid, "condition": "Reference",
                                  "view": view, "role": "input_reference", "path": str(source.relative_to(ROOT)),
                                  "bytes": source.stat().st_size, "sha256": sha256(source)})
        for condition in ("native_gfl", "native_gfh", "no_adapter", "native_gc3", "layer_llh", "gen_linear"):
            campaign_run = (DATA / "runs/revision_era_addendum" if condition in {"layer_llh", "gen_linear"}
                            else DATA / "runs/c3_confirmation")
            panel_path = campaign_run / "predictions" / condition / f"{uid}.png"
            panels[condition] = load_panel(panel_path)
            figure_assets.append({"panel_order": index, "object_uid": uid, "condition": condition,
                                  "view": "six-view-grid", "role": "method_prediction",
                                  "path": str(panel_path.relative_to(ROOT)), "bytes": panel_path.stat().st_size,
                                  "sha256": sha256(panel_path)})
        focus_row = next(row for row in contrast_rows[focal_contrast] if row["object_uid"] == uid)
        title = (f"{focal_contrast} | {stratum} | FG-PSNR {focus_row['delta_fg_psnr']:+.3f} dB; "
                 f"FG-LPIPS {focus_row['delta_fg_lpips']:+.5f} (lower favors A)")
        image = compose(uid, panels, title)
        panel_path = output / "panels" / f"panel_{index:02d}_{uid}.png"
        image.save(panel_path, optimize=False)
        selection_rows.append({"panel_order": index, "object_uid": uid,
                               "focal_contrast": focal_contrast, "selection_stratum": stratum,
                               "delta_fg_psnr_focal_a_minus_b": focus_row["delta_fg_psnr"],
                               "delta_fg_lpips_focal_a_minus_b": focus_row["delta_fg_lpips"],
                               "endpoint_pattern_focal_contrast": focus_row["endpoint_pattern"],
                               "per_object_significance": "not estimated"})
        # Small contact-sheet tiles are for navigation; full-resolution panels
        # remain the visual evidence for close inspection.
        thumb = image.resize((896, 208), Image.Resampling.LANCZOS)
        draw_thumb = ImageDraw.Draw(thumb)
        draw_thumb.rectangle((0, 0, thumb.width - 1, 28), fill=(255, 255, 255))
        text_fit(draw_thumb, (6, 5), f"{index:02d} {uid} | {focal_contrast} | {stratum}",
                 thumb.width - 12, font(13))
        panels_for_sheet.append(thumb)
    write_csv(output / "gallery_asset_sha256.csv", figure_assets)

    if panels_for_sheet:
        columns = 2
        rows_count = math.ceil(len(panels_for_sheet) / columns)
        contact = Image.new("RGB", (columns * 896, rows_count * 208), "white")
        for i, panel in enumerate(panels_for_sheet):
            contact.paste(panel, ((i % columns) * 896, (i // columns) * 208))
        contact.save(output / "20_groups_contact_sheet.png", optimize=False)

    # Cohort-level estimates come only from the locked primary and addendum
    # analyses. The two extra strategy-vs-GFL pages remain descriptive.
    primary = json.loads((DATA / "fresh_c_c3_minus_gfl_analysis.json").read_text())
    addendum = json.loads((DATA / "FRESH_C_ADDENDUM_ANALYSIS.json").read_text())
    summary = []
    for metric, result in primary["tests"].items():
        ci_low, ci_high = result["bootstrap_ci95"]
        higher = result["favorable_direction"] == "higher"
        summary.append({"cohort": primary["cohort"], "contrast": "C3-GFL",
                        "metric": metric, "mean_delta": result["mean"],
                        "median_delta": result["median"], "sd_delta": result["sd"],
                        "ci95_low": ci_low, "ci95_high": ci_high,
                        "favorable_object_fraction_for_a": result["favorable_object_fraction"],
                        "mean_favors_a": result["mean"] > 0 if higher else result["mean"] < 0,
                        "ci95_directional_support_for_a": ci_low > 0 if higher else ci_high < 0,
                        "p_raw": result.get("paired_t_p_raw"),
                        "p_holm": result.get("holm_adjusted_p"),
                        "multiplicity_family": result.get("multiplicity_family", "single registered primary; no adjustment"),
                        "registered_named_contrast": True})
    for result in addendum["tests"]:
        ci_low, ci_high = result["bootstrap_ci95"]
        higher = result["favorable_direction_for_a"] == "higher"
        summary.append({"cohort": addendum["cohort"], "contrast": result["contrast"],
                        "metric": result["metric"], "mean_delta": result["mean"],
                        "median_delta": result["median"], "sd_delta": result["sd"],
                        "ci95_low": ci_low, "ci95_high": ci_high,
                        "favorable_object_fraction_for_a": result["favorable_object_fraction_for_a"],
                        "mean_favors_a": result["mean"] > 0 if higher else result["mean"] < 0,
                        "ci95_directional_support_for_a": ci_low > 0 if higher else ci_high < 0,
                        "p_raw": result["paired_t_p_raw"],
                        "p_holm": result["holm_adjusted_p"],
                        "multiplicity_family": result["multiplicity_family"],
                        "registered_named_contrast": True})
    write_csv(output / "selected_20_uid_index.csv", selection_rows)
    write_csv(output / "cohort_contrast_summary.csv", summary)
    ranked_summary = []
    for family in sorted({row["multiplicity_family"] for row in summary}):
        for metric in sorted({row["metric"] for row in summary if row["multiplicity_family"] == family}):
            family_rows = [row for row in summary if row["multiplicity_family"] == family and row["metric"] == metric]
            family_rows.sort(key=lambda row: (float(row["p_holm"] if row["p_holm"] is not None else row["p_raw"]),
                                              row["contrast"]))
            for rank, row in enumerate(family_rows, start=1):
                ranked_summary.append({**row, "rank_within_registered_family_endpoint": rank,
                                       "ranking_key": "Holm p when defined; otherwise registered single-primary raw p"})
    write_csv(output / "cohort_contrast_summary_ranked_within_family.csv", ranked_summary)
    plot_contrast_forest(summary, output / "cohort_contrast_forest.png")
    plot_strategy_ranking_pages(contrast_rows, summary, output)
    file_hashes = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "gallery_manifest.json":
            file_hashes.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
                                "sha256": sha256(path)})
    manifest = {
        "status": "FINAL_GALLERY_BUILT_AFTER_BOTH_INTEGRITY_GATES",
        "cohort_n": len(uids), "uid_list_sha256": sha256(DATA / "fresh_c_objects.txt"),
        "primary_gate_sha256": sha256(DATA / "FRESH_C_INTEGRITY_GATE.json"),
        "addendum_gate_sha256": sha256(DATA / "FRESH_C_ADDENDUM_INTEGRITY_GATE.json"),
        "primary_analysis_sha256": sha256(DATA / "fresh_c_c3_minus_gfl_analysis.json"),
        "addendum_analysis_sha256": sha256(DATA / "FRESH_C_ADDENDUM_ANALYSIS.json"),
        "views": list(VIEWS), "conditions": [condition for _, condition in CONDITIONS],
        "rankings": "separate endpoint rankings; no cross-metric composite score or global winner",
        "image_selection": "Up to 20 unique objects: five balanced examples for each locked comparison (C3-GFL, LLH-C3, LLH-linear, C3-linear); if N<20 show all objects. Within each comparison, sample FG-PSNR high/low/near-median and FG-LPIPS low/high separately, with no composite score.",
        "gallery_order": "Locked comparison order; cohort-level contrast rankings are separate and sorted within endpoint/multiplicity family by Holm-adjusted p when defined, with effect sizes, confidence intervals, and favorable-object fractions.",
        "human_study_selection": "these outcome-ranked examples are not used to select human-study objects",
        "individual_panel_significance": "never estimated",
        "asset_license_handling": "Fresh C queue was filtered to CC0/CC BY/CC BY-SA; per-image source paths and hashes are recorded. Public redistribution still requires attribution/license review, especially for CC BY-SA outputs.",
        "figure_asset_manifest": str((output / "gallery_asset_sha256.csv").relative_to(ROOT)),
        "output_directory": str(output.relative_to(ROOT)),
        "selected_groups": selection_rows,
        "generated_file_hashes": file_hashes,
    }
    (output / "gallery_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prototype", "final"))
    args = parser.parse_args()
    result = build_prototype() if args.mode == "prototype" else build_final()
    print(json.dumps({"status": result["status"], "uid": result.get("uid"),
                      "n": result.get("cohort_n"), "output": result.get("output", result.get("output_directory"))},
                     indent=2))


if __name__ == "__main__":
    main()
