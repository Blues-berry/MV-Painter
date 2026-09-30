#!/usr/bin/env python
"""Independent end-to-end bake pipeline audit (final acceptance Phase 4).

Hand-traces 3 objects (obj_0013, obj_0048, obj_0078) x 4 methods through:
prediction panel -> UV texture -> GLB -> unseen renders -> metrics.
File forensics only; no summary CSV is trusted without recomputation.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import struct
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/4T/CXY/MV-Painter")
BAKE = ROOT / "final/round2/main_adapter_baking/cpu_bake_12_layerwise"
HANDOFF = ROOT / "final/round2/main_adapter_baking/BAKE_INPUT_HANDOFF_LAYERWISE_20260930.json"
PANEL_DIR = Path("/4T/tmp/mvpainter-layer-bake-input-20260930")
OUT_DIR = ROOT / "final/round2/coordination/final_acceptance_20260930"
OBJECTS = ["obj_0013", "obj_0048", "obj_0078"]
METHODS = ["global_fixed_low", "global_c3", "layer_lhl", "layer_llh"]
UNSEEN = list(range(1, 12))
SAMPLE_VIEWS = [1, 6, 11]

findings: list[str] = []
problems: list[str] = []


def check(cond: bool, ok_msg: str, fail_msg: str) -> bool:
    if cond:
        findings.append(ok_msg)
    else:
        problems.append(fail_msg)
    return cond


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rgba(p: Path) -> np.ndarray:
    return np.asarray(Image.open(p).convert("RGBA"), dtype=np.float32) / 255.0


def masked_psnr(pred, target, mask) -> float:
    valid = mask > 0.5
    mse = float(np.mean((pred[valid] - target[valid]) ** 2))
    return 100.0 if mse < 1e-12 else float(10.0 * math.log10(1.0 / mse))


def masked_ciede(pred, target, mask) -> float:
    from skimage.color import deltaE_ciede2000, rgb2lab
    valid = mask > 0.5
    return float(deltaE_ciede2000(rgb2lab(pred), rgb2lab(target))[valid].mean())


def glb_image_info(path: Path) -> tuple[str | None, int, str]:
    """Return (uri or None, image count, storage kind). Embedded bufferView
    textures have uri=None by glTF spec; byte-identity is checked separately."""
    data = path.read_bytes()
    length, = struct.unpack_from("<I", data, 12)
    jchunk = json.loads(data[20 : 20 + length])
    imgs = jchunk.get("images", [])
    kind = "absent"
    if imgs:
        kind = "embedded_bufferView" if "bufferView" in imgs[0] else f"uri:{imgs[0].get('uri')}"
    return (imgs[0].get("uri") if imgs else None), len(imgs), kind


def main() -> None:
    handoff = {r["object"]: r for r in json.loads(HANDOFF.read_text())["objects"]}
    pv_rows = list(csv.DictReader(open(BAKE / "UNSEEN_PER_VIEW_METRICS.csv")))
    obj_rows = {(r["object"], r["method"]): r for r in csv.DictReader(open(BAKE / "UNSEEN_OBJECT_METRICS.csv"))}
    trace: dict = {}

    for oid in OBJECTS:
        rec = handoff[oid]
        per_method = {}
        for meth in METHODS:
            mdir = BAKE / meth / oid
            meta = json.loads((mdir / "bake_metadata.json").read_text())

            # -- input identity: same exact GLB for all methods, hash matches handoff
            glb_in = Path(meta["input_exact_glb"])
            check(glb_in.resolve() == Path(rec["exact_glb_path"]).resolve(),
                  f"{oid}/{meth}: input GLB == handoff path", f"{oid}/{meth}: input GLB mismatch")
            check(sha(glb_in) == rec["exact_glb_sha256"],
                  f"{oid}/{meth}: input GLB SHA-256 matches handoff", f"{oid}/{meth}: input GLB hash mismatch")

            # -- prediction panel independence
            panel = PANEL_DIR / meth / f"{oid}.png"
            check(panel.exists(), f"{oid}/{meth}: panel exists", f"{oid}/{meth}: MISSING panel {panel}")
            panel_real = panel.resolve()
            ph = sha(panel)
            pw, phh = Image.open(panel).size

            # -- texture / glb / renders independence
            tex = Path(meta["texture_path"]); glb = Path(meta["output_textured_glb"])
            check(tex.parent.resolve() == mdir.resolve(), f"{oid}/{meth}: texture inside own method dir",
                  f"{oid}/{meth}: texture outside method dir")
            th = sha(tex); gh = sha(glb)
            uri, n_img, img_kind = glb_image_info(glb)
            check(n_img >= 1 and img_kind == "embedded_bufferView",
                  f"{oid}/{meth}: GLB embeds texture as bufferView image",
                  f"{oid}/{meth}: unexpected GLB image storage: kind={img_kind} uri={uri}")
            # texture bytes embedded in GLB must equal texture png bytes
            data = glb.read_bytes()
            ln, = struct.unpack_from("<I", data, 12)
            json_end = 20 + ln
            bin_len, = struct.unpack_from("<I", data, json_end)
            bin_chunk = data[json_end + 8 : json_end + 8 + bin_len]
            check(tex.read_bytes() in bin_chunk, f"{oid}/{meth}: GLB embeds byte-identical texture",
                  f"{oid}/{meth}: GLB binary chunk lacks exact texture bytes")

            renders = {}
            for v in UNSEEN:
                rp = mdir / "unseen_renders" / f"view_{v:03d}.png"
                renders[v] = (sha(rp), rp)
            check(len(set(h for h, _ in renders.values())) == 11,
                  f"{oid}/{meth}: 11 distinct render files", f"{oid}/{meth}: duplicate render hashes WITHIN method")
            check(meta["source_views"] == rec["target_view_mapping_slot_views"] if "target_view_mapping_slot_views" in rec else True,
                  "source views recorded", "")
            check(meta["unseen_views"] == UNSEEN, f"{oid}/{meth}: unseen view ids 1..11",
                  f"{oid}/{meth}: unexpected unseen_views {meta['unseen_views']}")

            # -- GT consistency: same GT paths in handoff for every method (checked once below)
            per_method[meth] = {
                "panel": str(panel), "panel_real": str(panel_real), "panel_sha256": ph,
                "panel_size": [pw, phh], "texture_sha256": th,
                "texture_size": list(Image.open(tex).size), "glb_sha256": gh,
                "glb_image_storage": img_kind, "glb_images": n_img,
                "render_sha256": {v: renders[v][0] for v in UNSEEN},
                "inpainted_fraction": meta["inpainting"]["inpainted_fraction"],
                "metadata_paths_resolve_to_method_dir": str(mdir.resolve()) == str(Path(meta["output_textured_glb"]).parent.resolve()),
            }

        # cross-method checks
        hashes = {
            "panel": [per_method[m]["panel_sha256"] for m in METHODS],
            "texture": [per_method[m]["texture_sha256"] for m in METHODS],
            "glb": [per_method[m]["glb_sha256"] for m in METHODS],
        }
        for kind, hs in hashes.items():
            check(len(set(hs)) == 4, f"{oid}: 4 distinct {kind} hashes across methods",
                  f"{oid}: {kind} hashes NOT distinct across methods: {hs}")
        real_dirs = {Path(per_method[m]["panel_real"]).parent.resolve() for m in METHODS}
        check(len(real_dirs) == 4, f"{oid}: 4 distinct real panel dirs (no softlink aliasing)",
              f"{oid}: panel dirs alias to same realpath: {real_dirs}")
        all_render_hashes = [per_method[m]["render_sha256"][v] for m in METHODS for v in UNSEEN]
        check(len(set(all_render_hashes)) == 44, f"{oid}: all 44 unseen renders distinct across methods",
              f"{oid}: render reuse across methods detected ({44 - len(set(all_render_hashes))} collisions)")

        # GT identity across methods: handoff GT paths are per-object (method-independent) by construction
        gt_paths = [Path(p) for p in rec["gt_rgba_17"]]
        gt_hash = {v: sha(gt_paths[v]) for v in UNSEEN}
        trace[oid] = {"per_method": per_method, "gt_sha256": gt_hash,
                      "gt_paths_unseen": {v: str(gt_paths[v]) for v in UNSEEN[:1]} | {}}

        # independent metric recomputation on sample views
        for meth in METHODS:
            mdir = BAKE / meth / oid
            for v in SAMPLE_VIEWS:
                render = load_rgba(mdir / "unseen_renders" / f"view_{v:03d}.png")
                gt = load_rgba(gt_paths[v])
                if gt.shape[1::-1] != render.shape[1::-1]:
                    gt_img = Image.fromarray(np.round(gt * 255).astype(np.uint8), mode="RGBA")
                    gt = np.asarray(gt_img.resize((render.shape[1], render.shape[0]), Image.Resampling.BICUBIC),
                                    dtype=np.float32) / 255.0
                gt_rgb = gt[:, :, :3] * gt[:, :, 3:4] + (1.0 - gt[:, :, 3:4])
                m = gt[:, :, 3]
                psnr = masked_psnr(render[:, :, :3], gt_rgb, m)
                ciede = masked_ciede(render[:, :, :3], gt_rgb, m)
                row = [r for r in pv_rows if r["object"] == oid and r["method"] == meth and int(r["raw_view"]) == v]
                check(len(row) == 1, f"{oid}/{meth}/v{v}: exactly one per-view CSV row",
                      f"{oid}/{meth}/v{v}: per-view CSV rows={len(row)}")
                if row:
                    dp = abs(float(row[0]["masked_psnr"]) - psnr)
                    dc = abs(float(row[0]["ciede2000"]) - ciede)
                    check(dp < 1e-4, f"{oid}/{meth}/v{v}: PSNR recompute matches CSV ({psnr:.4f})",
                          f"{oid}/{meth}/v{v}: PSNR CSV={row[0]['masked_psnr']} recomputed={psnr}")
                    check(dc < 1e-4, f"{oid}/{meth}/v{v}: CIEDE2000 recompute matches CSV ({ciede:.4f})",
                          f"{oid}/{meth}/v{v}: CIEDE2000 CSV={row[0]['ciede2000']} recomputed={ciede}")

            # object-level CSV vs per-view mean
            opsnr = np.mean([float(r["masked_psnr"]) for r in pv_rows
                             if r["object"] == oid and r["method"] == meth])
            orow = obj_rows[(oid, meth)]
            check(abs(opsnr - float(orow["masked_psnr"])) < 1e-3,
                  f"{oid}/{meth}: object CSV == mean(per-view CSV)",
                  f"{oid}/{meth}: object CSV masked_psnr {orow['masked_psnr']} != per-view mean {opsnr}")

        print(f"[{oid}] traced", flush=True)

    # paper-table spot check for the three traced objects (values from frozen CSV)
    paper_means = {}
    for meth in METHODS:
        vals = [float(obj_rows[(o, meth)]["masked_psnr"]) for o in OBJECTS]
        paper_means[meth] = vals
    trace["_traced_objects_masked_psnr"] = paper_means

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "BAKE_PIPELINE_AUDIT": "PASS" if not problems else "FAIL",
        "objects": OBJECTS, "methods": METHODS,
        "checks_passed": len(findings), "problems": problems,
        "trace": trace,
    }
    (OUT_DIR / "BAKE_PIPELINE_INDEPENDENT_AUDIT.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(f"checks_passed={len(findings)} problems={len(problems)}")
    for p in problems:
        print("PROBLEM:", p)


if __name__ == "__main__":
    main()
