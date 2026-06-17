#!/usr/bin/env python3
"""
Generate panels_v4: New comparison figures showing raw baseline and adapter improvement.
No inference. Reads existing PNGs only.

Figures:
1. baseline_reality.png — Shows raw baseline vs normalized baseline vs adapter
2. scale_tradeoff_v2.png — Scale comparison with raw baseline context
3. texture_detail.png — Crop-level texture comparison
"""
import os, json, hashlib
import numpy as np
from PIL import Image

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = "/4T/CXY/MV-Painter"
AUDIT_DIR = f"{BASE}/mvpoutput/geotex_refattn_v1/visual_artifacts_s250_audit"
VIS_BASE = f"{AUDIT_DIR}/vis_selected"
OUT_DIR = f"{AUDIT_DIR}/panels_v4"


def sha256_file(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def load_img(path):
    if not os.path.exists(path):
        return None
    return np.array(Image.open(path).convert('RGB')).astype(np.float32) / 255.0


def get_fg_mask(gt_img, threshold=0.92):
    """Foreground mask: pixels that are not near-white."""
    return ~np.all(gt_img > threshold, axis=2)


def normalize_bg_soft(image, mask, bg_value=1.0, threshold=0.3):
    """Softer background normalization with lower threshold."""
    bg = (mask < threshold).expand_as(image)
    result = image.clone()
    result[bg] = bg_value
    return result


def get_fg_bbox(gt_img, pad=0.1):
    """Get foreground bounding box from GT image."""
    mask = get_fg_mask(gt_img)
    if mask.sum() == 0:
        return None
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    h, w = gt_img.shape[:2]
    ph = int((rmax - rmin) * pad)
    pw = int((cmax - cmin) * pad)
    rmin = max(0, rmin - ph)
    rmax = min(h - 1, rmax + ph)
    cmin = max(0, cmin - pw)
    cmax = min(w - 1, cmax + pw)
    return (rmin, rmax, cmin, cmax)


def crop_to_bbox(img, bbox, target_size=256):
    """Crop image to bbox and resize to target_size."""
    if bbox is None:
        return img
    rmin, rmax, cmin, cmax = bbox
    cropped = img[rmin:rmax+1, cmin:cmax+1]
    pil = Image.fromarray((cropped * 255).astype(np.uint8)).resize((target_size, target_size), Image.LANCZOS)
    return np.array(pil).astype(np.float32) / 255.0


def find_input_view(obj_idx):
    """Find condition input view for this object."""
    manifest_path = f"{AUDIT_DIR}/visual_manifest.json"
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
        for obj in manifest.get("objects", []):
            if obj.get("object_idx") == obj_idx:
                img_dir = obj.get("source_data", {}).get("image_dir", "")
                inp = os.path.join(img_dir, "000.png")
                if os.path.exists(inp):
                    return inp
    return None


def make_figure(obj_list, columns, col_labels, title, out_name, crop_mode=False, extra_data=None):
    """Generate a comparison figure."""
    n_rows = len(obj_list)
    n_cols = len(columns)

    fig_w = n_cols * 2.5
    fig_h = n_rows * 2.5
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_w, fig_h))
    if n_rows == 1:
        axes = axes.reshape(1, -1)

    panel_meta = {
        "title": title,
        "columns": col_labels,
        "objects": [],
        "source_hashes": {},
        "crop_mode": crop_mode,
        "crop_policy": "foreground bbox + 10% padding, resize to 256x256" if crop_mode else "none",
        "resize_policy": "original 256x256 cells" if not crop_mode else "crop + resize to 256x256",
    }

    for row, obj_idx in enumerate(obj_list):
        obj_key = f"obj_{obj_idx:03d}"
        obj_meta = {"object_idx": obj_idx}
        panel_meta["objects"].append(obj_meta)
        panel_meta["source_hashes"][obj_key] = {}

        # Get GT for bbox computation
        gt_path = f"{VIS_BASE}/s1p25/visualizations/{obj_key}_gt.png"
        gt_img = load_img(gt_path)
        bbox = get_fg_bbox(gt_img) if crop_mode and gt_img is not None else None

        # Get mask for normalization
        mask = None
        if gt_img is not None:
            mask = get_fg_mask(gt_img).astype(np.float32)

        for col, (col_key, col_label) in enumerate(zip(columns, col_labels)):
            ax = axes[row, col]
            img = None
            src_path = None

            if col_key == "input":
                src_path = find_input_view(obj_idx)
            elif col_key == "gt":
                src_path = f"{VIS_BASE}/s1p25/visualizations/{obj_key}_gt.png"
            elif col_key == "raw_baseline":
                # Raw baseline without normalization
                src_path = f"{VIS_BASE}/s1p25/visualizations/{obj_key}_orig.png"
                if src_path and os.path.exists(src_path):
                    raw = load_img(src_path)
                    if raw is not None:
                        img = raw
                        panel_meta["source_hashes"][obj_key]["raw_baseline"] = sha256_file(src_path)
            elif col_key == "norm_baseline":
                # Baseline with soft normalization (threshold=0.3)
                src_path = f"{VIS_BASE}/s1p25/visualizations/{obj_key}_orig.png"
                if src_path and os.path.exists(src_path):
                    raw = load_img(src_path)
                    if raw is not None and mask is not None:
                        # Apply soft normalization
                        raw_t = torch.from_numpy(raw).permute(2, 0, 1).unsqueeze(0).float()
                        mask_t = torch.from_numpy(mask).unsqueeze(0).unsqueeze(0).float()
                        normed = normalize_bg_soft(raw_t, mask_t, threshold=0.3)
                        img = normed[0].permute(1, 2, 0).numpy()
                        panel_meta["source_hashes"][obj_key]["norm_baseline"] = sha256_file(src_path)
            elif col_key == "s1.25":
                src_path = f"{VIS_BASE}/s1p25/visualizations/{obj_key}_adapter.png"
            elif col_key == "s2.25":
                src_path = f"{VIS_BASE}/s2p25/visualizations/{obj_key}_adapter.png"
            elif col_key == "s2.50":
                src_path = f"{VIS_BASE}/s2p5/visualizations/{obj_key}_adapter.png"

            if img is None and src_path and os.path.exists(src_path):
                img = load_img(src_path)
                if col_key not in panel_meta["source_hashes"][obj_key]:
                    panel_meta["source_hashes"][obj_key][col_key] = sha256_file(src_path)

            if img is not None:
                if crop_mode and bbox is not None and col_key not in ("input",):
                    img = crop_to_bbox(img, bbox, 256)
                ax.imshow(img)
            else:
                ax.text(0.5, 0.5, "N/A", ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color='red')

            if row == 0:
                ax.set_title(col_label, fontsize=7, fontweight='bold')
            ax.axis('off')

        # Row label
        ax0 = axes[row, 0]
        ax0.set_ylabel(f"obj_{obj_idx:03d}", fontsize=7, rotation=0, labelpad=40)

    fig.suptitle(title, fontsize=12, fontweight='bold')
    plt.tight_layout()

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, out_name)
    fig.savefig(out_path, dpi=150, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)

    panel_meta["output_sha256"] = sha256_file(out_path)
    panel_meta["output_path"] = out_path
    meta_path = out_path.replace('.png', '.json')
    with open(meta_path, 'w') as f:
        json.dump(panel_meta, f, indent=2, default=str)

    print(f"  Saved: {out_path}")
    return panel_meta


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Figure 1: Baseline Reality — Shows raw baseline has content
    print("Figure 1: Baseline Reality")
    baseline_objects = [74, 181, 119, 110]  # Mix of best and severe
    baseline_columns = ["input", "gt", "raw_baseline", "norm_baseline", "s1.25", "s2.50"]
    baseline_labels = ["Input\n/Condition", "GT\n/Target", "Raw\nBaseline", "Normalized\nBaseline",
                       "Adapter\ns=1.25", "Adapter\ns=2.50"]
    make_figure(baseline_objects, baseline_columns, baseline_labels,
                "Baseline Reality: Raw vs Normalized", "baseline_reality.png")

    # Figure 2: Scale Trade-off v2 — With raw baseline context
    print("\nFigure 2: Scale Trade-off v2")
    tradeoff_objects = [74, 179, 298, 181]
    tradeoff_columns = ["input", "gt", "raw_baseline", "s1.25", "s2.25", "s2.50"]
    tradeoff_labels = ["Input\n/Condition", "GT\n/Target", "Raw\nBaseline",
                       "Adapter\ns=1.25", "Adapter\ns=2.25", "Adapter\ns=2.50"]
    make_figure(tradeoff_objects, tradeoff_columns, tradeoff_labels,
                "Scale Trade-off with Raw Baseline", "scale_tradeoff_v2.png")

    # Figure 3: Texture Detail — Crop-level comparison
    print("\nFigure 3: Texture Detail")
    texture_objects = [179, 83, 74, 118]
    texture_columns = ["gt", "raw_baseline", "s1.25", "s2.25", "s2.50"]
    texture_labels = ["GT\ncrop", "Raw Baseline\ncrop", "s=1.25\ncrop", "s=2.25\ncrop", "s=2.50\ncrop"]
    make_figure(texture_objects, texture_columns, texture_labels,
                "Texture Detail: Crop Comparison", "texture_detail.png", crop_mode=True)

    print(f"\nAll panels saved to {OUT_DIR}/")


if __name__ == "__main__":
    import torch
    main()
