#!/usr/bin/env python3
"""Build a PDF contact book from SHA-identified, unmodified RGB evidence."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence_rgb"
OUTPUT = ROOT / "COLOR_FAILURE_CASEBOOK.pdf"
WIDTH, HEIGHT = A4


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def text(c: canvas.Canvas, x: float, y: float, value: str, size: int = 9, bold: bool = False) -> None:
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(x, y, value)


def header(c: canvas.Canvas, title: str, subtitle: str = "") -> None:
    text(c, 34, HEIGHT - 38, title, 17, True)
    if subtitle:
        text(c, 34, HEIGHT - 55, subtitle, 8)
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.line(34, HEIGHT - 64, WIDTH - 34, HEIGHT - 64)


def footer(c: canvas.Canvas, page: int) -> None:
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.line(34, 27, WIDTH - 34, 27)
    text(c, 34, 14, "Original PNG pixels embedded; display scaling only. Full SHA-256 identities: SHA256SUMS.txt", 7)
    c.drawRightString(WIDTH - 34, 14, str(page))


def draw_tile(c: canvas.Canvas, path: Path, x: float, y: float, max_w: float, max_h: float,
              label: str, show_hash: bool = True) -> float:
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(max_w / iw, max_h / ih)
    w, h = iw * scale, ih * scale
    text(c, x, y + h + 5, label, 8, True)
    c.drawImage(ImageReader(str(path)), x, y, width=w, height=h, preserveAspectRatio=True, mask="auto")
    c.setStrokeColorRGB(0.75, 0.75, 0.75)
    c.rect(x, y, w, h, stroke=1, fill=0)
    if show_hash:
        text(c, x, y - 10, sha(path)[:16], 6)
    return h


def metric_lookup(path: Path, sample_id: str) -> dict[str, dict[str, str]]:
    out = {}
    for r in rows(path):
        if r["sample_id"] == sample_id:
            out[r["condition"]] = r
    return out


def add_p1_case(c: canvas.Canvas, page: int, sample: str, title: str, subtitle: str) -> None:
    metrics = metric_lookup(ROOT / "COLOR_FIDELITY_PAIRED_RESULTS.csv", sample)
    header(c, title, subtitle)
    ystats = HEIGHT - 82
    for name, key in [("No Adapter", "No Adapter"), ("GFL", "GFL"), ("LLH", "LLH")]:
        r = metrics[key]
        text(c, 36, ystats, f"{name}: CIEDE2000 {float(r['mean_fg_ciede2000']):.2f}; "
             f"FG-PSNR {float(r['fg_psnr']):.2f} dB; FG-LPIPS {float(r['fg_lpips']):.3f}", 8)
        ystats -= 13
    items = [
        ("GT", EVIDENCE / "p1" / sample / "GT.png"),
        ("No Adapter", EVIDENCE / "p1" / sample / "NoAdapter.png"),
        ("GFL", EVIDENCE / "p1" / sample / "GFL.png"),
        ("LLH", EVIDENCE / "p1" / sample / "LLH.png"),
    ]
    w, h = 196, 294
    positions = [(68, 405), (331, 405), (68, 50), (331, 50)]
    for (label, path), (x, y) in zip(items, positions):
        draw_tile(c, path, x, y, w, h, label)
    footer(c, page)
    c.showPage()


def main() -> None:
    p1 = rows(ROOT / "COLOR_FIDELITY_PAIRED_RESULTS.csv")
    summary = rows(ROOT / "P1_PAIRED_SUMMARY.csv")
    stage = rows(ROOT / "P1_STAGE_TRAJECTORY.csv")
    p0 = rows(ROOT / "P0_OUTPUT_DIFFERENCE_TABLE.csv")
    page = 1
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)

    # Executive summary and paired protocol.
    header(c, "R1 Color Fidelity | Final Evidence Casebook",
           "A bounded, pixel-identified audit of pre-bake RGB outputs, runtime reproducibility and VAE isolation.")
    text(c, 36, 754, "Frozen paired protocol", 11, True)
    text(c, 36, 738, "26 objects × No Adapter / GFL / LLH; same checkpoint, per-object seed and inputs; unique six-view targets.", 9)
    text(c, 36, 724, "Checkpoint SHA-256 0618d6b284ab47aa…; base runner SHA-256 e5c28e915ba137d3…; view order is recorded per row.", 8)
    text(c, 36, 710, "CIEDE/texture use identified PNGs; FG-PSNR/LPIPS/Edge-SSIM use the hash-linked Python 3.10 reloaded-RGB ledger.", 8)

    text(c, 36, 680, "Object-level paired effects (20,000 bootstrap resamples; seed 61008)", 11, True)
    selected = [
        ("GFL − No Adapter", "mean_fg_ciede2000", "−19.654", "[−26.370, −13.248]", "24/26 lower"),
        ("GFL − No Adapter", "fg_psnr", "+6.646 dB", "[+5.556, +7.635]", "25/26 higher"),
        ("GFL − No Adapter", "fg_lpips", "−0.0325", "[−0.0536, −0.0107]", "18/26 lower"),
        ("LLH − GFL", "mean_fg_ciede2000", "+3.583", "[+0.462, +6.712]", "9/26 lower"),
        ("LLH − GFL", "fg_lpips", "−0.0129", "[−0.0274, +0.0007]", "13/26 lower"),
        ("LLH − GFL", "texture_fg_grad_mag", "−0.0677", "[−0.0813, −0.0549]", "0/26 higher"),
    ]
    y = 660
    for contrast, metric, effect, ci, note in selected:
        text(c, 38, y, f"{contrast:20s} | {metric:23s} | {effect:>10s} | 95% CI {ci} | {note}", 8)
        y -= 17
    text(c, 36, 532, "Reading the evidence", 11, True)
    paragraphs = [
        "The same two original Fig. 4 objects were visually tagged with a pink/purple cast in No Adapter, GFL and LLH outputs. GFL lowers average GT-referenced color error over 26 objects, but does not remove those two visible cases.",
        "LLH has no reliable structure advantage over GFL and reduces measured texture/detail. Its average CIEDE2000 is worse; the small LPIPS decrease has a paired interval touching zero.",
        "The color error exists in generated RGB before texture baking. A GT VAE round trip averages CIEDE2000 4.09 on the selected object, versus 22.03 for GFL; this rules against a simple VAE-only account, not every decoder interaction.",
        "Runtime reproduction is environment-sensitive: three locked Fresh C examples reproduce the historical PNGs exactly in Python 3.13 and the earlier observer PNGs exactly in Python 3.10. The first captured value drift is FP16 scheduler latent scaling before UNet step 0.",
    ]
    y = 510
    for para in paragraphs:
        words = para.split(); line = ""
        for word in words:
            if len(line) + len(word) + 1 > 102:
                text(c, 38, y, line, 8); y -= 12; line = word
            else:
                line = (line + " " + word).strip()
        if line:
            text(c, 38, y, line, 8); y -= 12
        y -= 8
    text(c, 36, 302, "Image identity", 11, True)
    text(c, 38, 285, "Each following panel is the exact PNG named in evidence_rgb/; no recoloring, GT adjustment, or per-image normalization was applied.", 8)
    text(c, 38, 271, "P1 raw images use the same six unique target views. Early denoising snapshots are shown only as trajectory context; they are not quality outputs.", 8)
    text(c, 38, 245, f"Evidence rows: {len(p1)} paired RGB conditions; {len(summary)} paired effect summaries; {len(stage)} aligned late-stage rows.", 8)
    footer(c, page); c.showPage(); page += 1

    add_p1_case(c, page, "fig4_row1", "Fig. 4 row 1 | persistent pink cast", "Original object idx 4; seed 46; UID eac4b392b7b448a2b6ec77e8936abe1b; same six target IDs [14, 15, 0, 16, 12, 13].")
    page += 1
    add_p1_case(c, page, "fig4_row3", "Fig. 4 row 3 | persistent hue error", "Original object idx 12; seed 54; UID ed600cc9d91448939edeeb3a6d858448; same six target IDs [14, 15, 0, 16, 12, 13].")
    page += 1
    add_p1_case(c, page, "freshc_panel_03", "Fresh C | typical color / detail control", "Fresh C UID ca887928bb664bcba121219f0af41293; no visual pink cast or fine-detail-loss tag in the frozen review.")
    page += 1
    add_p1_case(c, page, "freshc_panel_01", "Fresh C | detail-loss control", "Fresh C UID c76ac44df995482185077da81939b306; fine-detail loss tagged; no visual pink cast. Also used in P0 runtime identity audit.")
    page += 1

    # Runtime identity comparisons, one case per page to keep the three RGBs readable.
    p0_by_key = {(r["comparison"], r["sample_id"]): r for r in p0}
    runtime_samples = [
        ("freshc_panel_01", "c76ac44df995482185077da81939b306"),
        ("freshc_panel_03", "ca887928bb664bcba121219f0af41293"),
        ("freshc_panel_20", "06fa4974f8cd4d4ea792e98fa1521457"),
    ]
    for sample, uid in runtime_samples:
        b = p0_by_key[("archive_vs_py310", sample)]
        header(c, f"P0 | Runtime identity — {sample}",
               f"UID {uid}; same locked GFL checkpoint, object seed, input tensors, config and unique-six target views.")
        text(c, 36, 758, "Archive ↔ Python 3.13.5: byte-identical; the repeat trace is also exact.", 8)
        text(c, 36, 743,
             f"Archive ↔ Python 3.10.20: MAE {float(b['mae_0_255']):.2f}/255; "
             f"changed-pixel fraction {float(b['changed_pixel_fraction']):.4f}.", 8)
        text(c, 36, 728, "First captured cross-runtime value drift is the FP16 latent × scheduler sigma before UNet step 0.", 8)
        xcols = [36, 223, 410]
        labels = ["Historical archive", "Python 3.13.5", "Python 3.10.20"]
        for x, label, key in zip(xcols, labels, ["archive.png", "python313.png", "python310.png"]):
            draw_tile(c, EVIDENCE / "reproducibility" / sample / key, x, 380, 150, 225, label)
        footer(c, page); c.showPage(); page += 1

    # Denoising trajectory.
    header(c, "P1 | Color trajectory in one aligned pink case",
           "Fig. 4 row 1 GFL; Python 3.10 output SHA matches frozen P1 RGB exactly. Intermediate images are decoded latent snapshots.")
    row_by_step = {r["step_after_scheduler_update"]: r for r in stage if r["condition"] == "GFL"}
    labels = [25, 33, 40, 45, 49, "final_saved_png"]
    xs = [34, 224, 414]
    ys = [452, 187]
    for idx, step in enumerate(labels):
        col, row = idx % 3, idx // 3
        ybase = ys[row]
        name = "final.png" if step == "final_saved_png" else f"after_step_{int(step):02d}.png"
        path = EVIDENCE / "stage_fig4_row1_gfl" / name
        draw_tile(c, path, xs[col], ybase, 145, 218, f"After update {step if isinstance(step, int) else '49 / final'}")
        metric = row_by_step["49" if step == "final_saved_png" else str(step)]
        text(c, xs[col], ybase - 22,
             f"CIEDE {float(metric['mean_fg_ciede2000']):.1f}; Δa* {float(metric['mean_delta_a_star']):+.1f}; Δb* {float(metric['mean_delta_b_star']):+.1f}", 7)
    text(c, 35, 95, "The object is not interpretable in early high-noise snapshots. Magenta surfaces are visible by update 40 in this case.", 8)
    text(c, 35, 82, "This sampled trajectory localizes the observed pattern to late denoising, not the exact first latent step.", 8)
    footer(c, page); c.showPage(); page += 1

    # VAE isolation.
    vae = json.loads((ROOT / "VAE_ISOLATION_RESULTS.json").read_text())
    header(c, "P1 | VAE encode–decode isolation",
           "Same Fig. 4 row 1 GT input; Python 3.10.20, torch 2.7.0+cu128, diffusers 0.20.2; normalization recorded in the metrics JSON.")
    mode = vae["mean_fg_ciede2000"]["mode"]
    sample = vae["mean_fg_ciede2000"]["sample_seed42"]
    text(c, 36, 757, f"GT round trip mean CIEDE2000: posterior mode {mode:.3f}; fixed-seed sample {sample:.3f}.", 8)
    text(c, 36, 742, "Compare with the aligned GFL output: CIEDE2000 22.032, Δa* +1.977; the round trip's mean Δa* is about −1.35.", 8)
    tiles = [
        ("GT input", EVIDENCE / "p1/fig4_row1/GT.png"),
        ("GFL final", EVIDENCE / "p1/fig4_row1/GFL.png"),
        ("VAE round trip · posterior mode", EVIDENCE / "vae_fig4_row1/vae_roundtrip_mode.png"),
        ("VAE round trip · sample seed 42", EVIDENCE / "vae_fig4_row1/vae_roundtrip_sample_seed42.png"),
    ]
    for (label, path), (x, y) in zip(tiles, [(68, 405), (331, 405), (68, 50), (331, 50)]):
        draw_tile(c, path, x, y, 196, 294, label)
    footer(c, page); c.showPage()
    c.save()
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
