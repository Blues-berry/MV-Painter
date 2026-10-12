"""Compose submission displays from hash-verified, unchanged research outputs."""
from pathlib import Path
import base64
import csv
import hashlib
import json
import shutil

import cairosvg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
SOURCES = FIG / "submission_sources"
CONSERVATIVE = Path("/4T/CXY/MV-Painter/CG_revision_20261011_conservative_submission_r2/manuscript/figures")
SERVER = Path("/4T/CXY/MV-Painter")
EXP = Path("/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
RECORDS = []
DISPLAYS = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path, digest, study, uid, method, view):
    """Cache original bytes; rebuilding after packaging needs no server path."""
    dest = SOURCES / study / uid / f"{method}_view{view:03d}.png"
    if not dest.exists():
        assert path.is_file() and sha(path) == digest, str(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
    assert sha(dest) == digest, str(dest)
    RECORDS.append({"study": study, "uid": uid, "condition": method, "view": view,
                    "original_path": str(path), "sha256": digest,
                    "packaged_path": str(dest.relative_to(ROOT))})
    with Image.open(dest) as im:
        rgba = im.convert("RGBA")
        bg = Image.new("RGBA", rgba.size, "white")
        bg.alpha_composite(rgba)
        return bg.convert("RGB")


def bbox(im):
    a = np.asarray(im, dtype=float)
    border = np.concatenate([a[:4].reshape(-1, 3), a[-4:].reshape(-1, 3),
                             a[:, :4].reshape(-1, 3), a[:, -4:].reshape(-1, 3)])
    y, x = np.where(np.max(abs(a - np.median(border, axis=0)), axis=2) > 25)
    return (int(x.min()), int(y.min()), int(x.max())+1, int(y.max())+1) if len(x) else (0, 0, im.width, im.height)


def frame(images, roi=None):
    bounds = [bbox(im) for im in images] + ([roi] if roi else [])
    w, h = images[0].size
    pad = 12 if w >= 512 else 6
    return (max(0, min(b[0] for b in bounds)-pad), max(0, min(b[1] for b in bounds)-pad),
            min(w, max(b[2] for b in bounds)+pad), min(h, max(b[3] for b in bounds)+pad))


def strip(images, labels, panel, bounds, roi=None, cell=400):
    height = min(360, max(180, round((cell-24)*(bounds[3]-bounds[1])/(bounds[2]-bounds[0]))))
    extra = 240 if roi else 0
    canvas = Image.new("RGB", (cell*len(images), height+extra+60), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(FONT, 29)
    draw.text((8, 10), panel, font=font, fill="#253547")
    for j, (im, label) in enumerate(zip(images, labels)):
        box = draw.textbbox((0, 0), label, font=font)
        draw.text((j*cell+(cell-box[2]+box[0])/2, 10), label, font=font, fill="#253547")
        context = im.crop(bounds)
        if roi:
            ImageDraw.Draw(context).rectangle((roi[0]-bounds[0], roi[1]-bounds[1],
                                               roi[2]-bounds[0], roi[3]-bounds[1]), outline="#c0373f", width=2)
        for image, y, max_h in [(context, 50, height)] + ([(im.crop(roi), 60+height, extra-10)] if roi else []):
            scale = min((cell-24)/image.width, max_h/image.height)
            resized = image.resize((round(image.width*scale), round(image.height*scale)), Image.Resampling.LANCZOS)
            canvas.paste(resized, (j*cell+(cell-resized.width)//2, y+(max_h-resized.height)//2))
    return canvas


def save(panels, name):
    canvas = Image.new("RGB", (max(p.width for p in panels), sum(p.height for p in panels)+28*(len(panels)-1)), "white")
    y = 0
    for p in panels:
        canvas.paste(p, (0, y)); y += p.height+28
    png = FIG / (name+".png")
    canvas.save(png)
    data = base64.b64encode(png.read_bytes()).decode()
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas.width}" height="{canvas.height}"><image width="{canvas.width}" height="{canvas.height}" href="data:image/png;base64,{data}"/></svg>'
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=str(FIG/(name+".pdf")))
    DISPLAYS.append({"asset": str((FIG/(name+".pdf")).relative_to(ROOT)),
                     "sha256": sha(FIG/(name+".pdf")), "image_sha256": sha(png)})


def main():
    # Original lineage is kept separately from the final layout metadata.
    original = FIG / "SUBMISSION_ORIGINAL_FRESH_C_MANIFEST.csv"
    if not original.exists():
        shutil.copy2(ROOT/"history/round_013/figures/FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv"
                     if (ROOT/"history/round_013/figures/FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv").exists()
                     else FIG/"FRESH_C_FIGURE_SOURCE_ROI_MANIFEST.csv", original)
    rows = list(csv.DictReader(original.open()))
    names = {"Reference": "Target", "GFL": "Fixed Low", "GFH": "Fixed High", "C3": "C3", "LLH": "Layer LLH", "Generic Linear": "Generic Linear"}
    panels = []
    for panel_id in sorted({r["panel_id"] for r in rows if r["figure_id"] == "fig5"}):
        group = [r for r in rows if r["panel_id"] == panel_id]
        images = []
        for r in group:
            im = source(SERVER/r["input_path"], r["input_sha256"], "freshc", r["object_uid"], r["method"].replace(" ", "_"), 0)
            if r["method"] != "Reference":
                im = im.crop(tuple(map(int, r["tile_bbox"].split(","))))
            images.append(im.resize((256, 256), Image.Resampling.LANCZOS))
        roi = tuple(map(int, group[0]["crop_bbox"].split(",")))
        bounds = frame(images, roi)
        panels.append(strip(images, [names[r["method"]] for r in group], f"({chr(97+len(panels))})", bounds, roi))
        DISPLAYS.append({"display": "strong_fixed_linear", "uid": group[0]["object_uid"], "view": 0, "shared_frame": bounds, "shared_roi": roi, "selection": "Retained outcome-selected fixed-scale trade-off and linear counterexample; not population-representative."})
    save(panels, "fig5_freshc_context_roi")

    color = [r for r in rows if r["figure_id"] == "fig6_color_diagnostic" and r["method"] != "No Adapter"]
    uid = color[0]["object_uid"]
    images = []
    for r in color:
        im = source(SERVER/r["input_path"], r["input_sha256"], "freshc", uid, r["method"].replace(" ", "_"), 0)
        if r["method"] != "Reference": im = im.crop(tuple(map(int, r["tile_bbox"].split(","))))
        images.append(im.resize((256, 256), Image.Resampling.LANCZOS))
    favorable = FIG/"SUBMISSION_C3_COLOR_SOURCE.json"
    if not favorable.exists():
        provenance = json.loads((CONSERVATIVE/"FIG7_METRIC_FAVORABLE_PROVENANCE.json").read_text())
        item = next(x for p in provenance if p["object_uid"] == uid for x in p["sources"] if x["method"] == "C3")
        favorable.write_text(json.dumps(item, indent=2)+"\n")
    item = json.loads(favorable.read_text())
    c3 = source(Path(item["original_path"]), item["original_sha256"], "freshc", uid, "C3", 0).crop((0, 0, 256, 256))
    images.insert(2, c3)
    roi = (48, 90, 208, 210)
    bounds = frame(images, roi)
    save([strip(images, ["Target", "Fixed Low", "C3", "Layer LLH"], "", bounds, roi)], "fig6_color_diagnostic_freshc_context_roi")
    DISPLAYS.append({"display": "color_failure", "uid": uid, "view": 0, "shared_frame": bounds, "shared_roi": roi,
                     "No_Adapter_visual": "Omitted conspicuously malformed panel only; all numerical results retained.",
                     "selection": "Previously viewed lowest C3-minus-GFL LPIPS stratum, not selected for color."})

    bake_csv = FIG/"SUBMISSION_BAKE_ORIGINAL_PROVENANCE.csv"
    if not bake_csv.exists(): shutil.copy2(CONSERVATIVE/"BAKED_FIGURE_VIDEO_PROVENANCE.csv", bake_csv)
    index = {(r["uid"], r["method"], int(r["raw_view"])): r for r in csv.DictReader(bake_csv.open())}
    uids = ["1dc2c857f7614caeb6c2aa0559ccf973", "21678bd623654182b52c11d013de4e71"]
    panels = []
    bake_uids = list(dict.fromkeys(u for u, method, view in index if view == 4))
    for j, uid in enumerate(bake_uids):
        all_images = {}
        for (u, method, view), r in index.items():
            if u == uid and view == 4:
                all_images[method] = source(Path(r["path"]), r["sha256"], "bake10", uid, method, 4)
        # Bounds include all seven conditions even though four columns are displayed.
        bounds = frame(list(all_images.values()))
        methods = ["source", "gt", "budget_fixed_mean", "budget_late16"]
        if uid in uids:
            panels.append(strip([all_images[m] for m in methods], ["Source", "GT-256 bake", "Fixed Mean", "Late-high"], f"({chr(97+j)})", bounds))
        complete_methods = ["source", "gt", "native_default_1x", "native_gfl", "native_gfh",
                            "budget_fixed_mean", "native_gc3", "budget_late16", "gen_linear"]
        complete_labels = ["Source", "GT-256 bake", "1.0 (capped)", "Fixed Low", "Fixed High",
                           "Fixed Mean", "C3", "Late-high", "Generic Linear"]
        full_panels = [strip([all_images[m] for m in complete_methods[k:k+3]], complete_labels[k:k+3], "", bounds)
                       for k in [0, 3, 6]]
        save(full_panels, f"figS_bake014_{j+1:02d}")
        DISPLAYS.append({"display": "bake10", "uid": uid, "unseen_view": 4, "shared_frame": bounds, "selection": "All seven rights-cleared bake objects; main uses first two input-order objects; not selected by quality."})
    save(panels, "fig8_baked_unseen_context")

    mva_index = FIG/"SUBMISSION_NATIVE50_VISUAL_SOURCES.json"
    if not mva_index.exists():
        freeze = json.loads((EXP/"MVA_MATRIX_FREEZE.json").read_text())
        values = json.loads((EXP/"mvadapter_matrix/rows.json").read_text())
        conditions = ["native_default_1x", "fixed_low_0p75", "fixed_mean_0p83", "budget_early16", "budget_middle16", "budget_late16", "budget_linear_mean_0p83"]
        data = []
        for uid in uids:
            obj = next(o for o in freeze["objects"] if o["object_uid"] == uid)
            data.append({"uid": uid, "condition": "target", **obj["gt_images_official_order"][0]})
            for cond in conditions:
                row = next(r for r in values if r["object_uid"] == uid and r["condition"] == cond)
                data.append({"uid": uid, "condition": cond, "path": str(EXP/"mvadapter_matrix/predictions"/cond/uid/"view_00.png"), "sha256": row["prediction_png_sha256"][0]})
        mva_index.write_text(json.dumps(data, indent=2)+"\n")
    data = json.loads(mva_index.read_text())
    panels = []; complete = []
    labels = {"target": "Target", "native_default_1x": "Native / High", "fixed_low_0p75": "Fixed Low", "fixed_mean_0p83": "Fixed Mean", "budget_early16": "Early-high", "budget_middle16": "Middle-high", "budget_late16": "Late-high", "budget_linear_mean_0p83": "Generic Linear"}
    for j, uid in enumerate(uids):
        all_images = {r["condition"]: source(Path(r["path"]), r["sha256"], "native50", uid, r["condition"], 0) for r in data if r["uid"] == uid}
        bounds = frame(list(all_images.values()))
        methods = ["target", "fixed_mean_0p83", "budget_middle16", "budget_late16"]
        panels.append(strip([all_images[m] for m in methods], [labels[m] for m in methods], f"({chr(97+j)})", bounds))
        for offset in [0, 4]:
            methods = list(labels)[offset:offset+4]
            complete.append(strip([all_images[m] for m in methods], [labels[m] for m in methods], f"({chr(97+j)})" if not offset else "", bounds))
        DISPLAYS.append({"display": "native50", "uid": uid, "view": 0, "shared_frame": bounds, "selection": "First two input-order rights-cleared objects; seven controls shown completely in supplement; no transfer superiority claim."})
    save(panels, "fig9_mvadapter_native014")
    save(complete, "figS_native50_all014")

    controls = list(csv.DictReader((FIG/"ROUND002_CONTROL_PROVENANCE.csv").open()))
    panels = []
    control_labels = {"input": "Conditioning view", "native_unset": "Native residual",
                      "native_default_1x": "1.0 (capped)", "native_gc3": "C3", "budget_late16": "Late-high"}
    for j, uid in enumerate(uids):
        images = []
        for method in control_labels:
            r = next(r for r in controls if r["uid"] == uid and r["method"] == method)
            image = source(Path(r["path"]), r["sha256"], "native_geotex_controls", uid, method, -1)
            if method == "input":
                canvas = Image.new("RGB", (512, 768), "white")
                canvas.paste(image.resize((512, 512), Image.Resampling.LANCZOS), (0, 0))
                image = canvas
            assert image.size == (512, 768)
            images.append(image)
        panels.append(strip(images, list(control_labels.values()), f"({chr(97+j)})", (0, 0, 512, 768)))
    save(panels, "figS_native_controls014")
    DISPLAYS.append({"display": "native_geotex_controls", "selection": "Same two original input-order rights-cleared objects; full six-view grids retained; No Adapter visual column omitted only.", "metric_scope": "Original exploratory contrast family including No Adapter unchanged."})

    # Retain diagnostic grids while omitting disabled-adapter columns. The
    # existing composed source is hash-identified; only complete grid tiles
    # are extracted, without changing their image contents.
    parent = json.loads((ROOT/"PARENT_SOURCE_FREEZE.json").read_text())
    diagnostics = [
        ("figS4_native_base_diagnostic.png", "figS_base_diagnostic014", [0,2,3,4,5],
         ["Conditioning view", "Controlled C3", "Controlled Late-high", "Native base 50", "Native base 75"], 3),
        ("figS7_native_geometry_matrix.png", "figS_geometry_diagnostic014", [0,2,3,4,5,6,7,8],
         ["Conditioning view", "Native residual", "Fixed Low", "Fixed High", "Fixed Mean", "C3", "Late-high", "Generic Linear"], 4),
        ("figS5_guidance_embedding_factorial.png", "figS_guidance_diagnostic014", [0,3,4],
         ["Conditioning view", "Cached / CFG2", "Online / CFG2"], 3),
        ("figS6_target_resolution_bridge.png", "figS_resolution_diagnostic014", [0,2,4],
         ["Conditioning view", "256 / CFG2", "512 / CFG2"], 3),
    ]
    for old_name, new_name, columns, labels, per_row in diagnostics:
        original = FIG/old_name
        assert sha(original) == parent["files_sha256"]["figures/"+old_name]
        RECORDS.append({"study":"archived_protocol_diagnostic", "uid":"two_original_objects", "condition":"archived_composite", "view":-1,
                        "original_path":str(original), "sha256":sha(original), "packaged_path":str(original.relative_to(ROOT))})
        with Image.open(original) as im:
            for j, uid in enumerate(uids):
                tiles=[im.crop((c*256,65+j*440,(c+1)*256,65+j*440+384)).convert("RGB") for c in columns]
                parts=[strip(tiles[k:k+per_row],labels[k:k+per_row],"",(0,0,256,384),cell=360)
                       for k in range(0,len(tiles),per_row)]
                save(parts,f"{new_name}_{j+1:02d}")
                DISPLAYS.append({"display":new_name, "uid":uid, "source_composite_sha256":sha(original),
                                 "retained_columns":columns, "grid_tile_y":65+j*440, "grid_tile_size":[256,384],
                                 "No_Adapter_visual":"Original disabled/no-adapter column1 omitted; all numerical and original failure records retained."})

    # Use the precise, editable vector schematic from the conservative layout.
    svg = FIG/"fig1_tcas_control.svg"
    if not svg.exists() or "data:image" in svg.read_text(): shutil.copy2(CONSERVATIVE/"fig1_tcas_control.svg", svg)
    cairosvg.svg2pdf(bytestring=svg.read_bytes(), write_to=str(FIG/"fig1_tcas_control.pdf"))
    DISPLAYS.append({"asset": "figures/fig1_tcas_control.pdf", "sha256": sha(FIG/"fig1_tcas_control.pdf"), "type": "Reproducible vector diagram; no generated concept-art image or measured result thumbnails."})
    (ROOT/"FINAL_VISUAL_SOURCE_MANIFEST.json").write_text(json.dumps({"sources": RECORDS, "displays": DISPLAYS, "operations": "RGBA-on-white; common whole-object framing; unchanged shared pixel ROI; uniform resampling for display only. No color/detail retouching, image generation, or experimental rescore.", "stats": "All original objects/conditions and negative results retained."}, indent=2)+"\n")
    print(f"Verified {len(RECORDS)} source images/composites; omitted original malformed disabled-adapter visual columns.")


if __name__ == "__main__":
    main()
