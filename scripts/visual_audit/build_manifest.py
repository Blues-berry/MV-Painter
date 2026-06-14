"""Build visual artifact manifest for s=2.50 audit.

Maps each selected object to all available assets: source data, eval outputs, metrics.
All paths resolved from config, no hardcoded paths.

Usage: python scripts/visual_audit/build_manifest.py
"""
import csv, json, hashlib, os, sys
import numpy as np

# === Config ===
ROOT = "mvpoutput/geotex_refattn_v1"
DATA_ROOT = "/4T/CXY/MV-Painter/data/train_data/rendered_full"
OBJECT_LIST = f"{DATA_ROOT}/test_objects_300.txt"
OUTPUT_DIR = f"{ROOT}/visual_artifacts_s250_audit"

EVAL_DIRS = {
    "s1.25_50obj": f"{ROOT}/scale_sweep_v1_50obj/scale_1p25",
    "s1.25_300obj": f"{ROOT}/scale_1p25_300obj",
    "s2.25_50obj": f"{ROOT}/scale_sweep_v1_extended_50obj/scale_2p25",
    "s2.50_50obj": f"{ROOT}/scale_sweep_v1_extended_50obj/scale_2p50",
    "s2.50_300obj": f"{ROOT}/eval_300obj_scale_2p50",
}

METRIC_FILES = {
    "s1.25_300obj": f"{ROOT}/scale_1p25_300obj/per_object_metrics.csv",
    "s2.50_300obj": f"{ROOT}/eval_300obj_scale_2p50/per_object_metrics.csv",
    "extended_sweep": f"{ROOT}/scale_sweep_v1_extended_50obj/extended_per_object_scale_sweep.csv",
    "selection": f"{ROOT}/scale_sweep_v1_extended_50obj/selection_analysis.json",
}


def sha256_file(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()[:16]


def load_object_uids():
    with open(OBJECT_LIST) as f:
        return [line.strip() for line in f if line.strip()]


def load_metrics_300(csv_path):
    """Load per-object metrics from 300-object CSV."""
    if not os.path.exists(csv_path):
        return {}
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
    return {int(r['object_idx']): r for r in rows}


def select_objects():
    """Select objects for visual audit based on metrics."""
    m125 = load_metrics_300(METRIC_FILES["s1.25_300obj"])
    m250 = load_metrics_300(METRIC_FILES["s2.50_300obj"])

    if not m125 or not m250:
        print("WARNING: Missing 300-object metrics, using defaults")
        return list(range(30))

    common = sorted(set(m125.keys()) & set(m250.keys()))
    diffs = []
    for obj in common:
        fg125 = float(m125[obj]['delta_fg_ssim'])
        fg250 = float(m250[obj]['delta_fg_ssim'])
        delta = fg250 - fg125
        diffs.append((obj, fg125, fg250, delta))
    diffs.sort(key=lambda x: x[3])

    selected = []

    # Severe regression: delta < -0.05
    severe = [d for d in diffs if d[3] < -0.05]
    for obj, fg125, fg250, delta in severe[:8]:
        selected.append({
            'object_idx': obj, 'category': 'severe_regression',
            'reason': f'FG SSIM delta={delta:+.4f} (s=2.50 vs s=1.25)',
            'fg_ssim_125': fg125, 'fg_ssim_250': fg250, 'delta': delta
        })

    # Borderline regression: -0.05 < delta < -0.03
    borderline = [d for d in diffs if -0.05 <= d[3] < -0.03]
    for obj, fg125, fg250, delta in borderline[:4]:
        selected.append({
            'object_idx': obj, 'category': 'borderline_regression',
            'reason': f'FG SSIM delta={delta:+.4f}',
            'fg_ssim_125': fg125, 'fg_ssim_250': fg250, 'delta': delta
        })

    # Best improvement: top 8
    best = sorted(diffs, key=lambda x: x[3], reverse=True)
    for obj, fg125, fg250, delta in best[:8]:
        selected.append({
            'object_idx': obj, 'category': 'best_improvement',
            'reason': f'FG SSIM delta={delta:+.4f}',
            'fg_ssim_125': fg125, 'fg_ssim_250': fg250, 'delta': delta
        })

    # Median improvement: around median delta
    median_delta = np.median([d[3] for d in diffs])
    median_objs = sorted(diffs, key=lambda x: abs(x[3] - median_delta))
    for obj, fg125, fg250, delta in median_objs[:6]:
        if obj not in [s['object_idx'] for s in selected]:
            selected.append({
                'object_idx': obj, 'category': 'median',
                'reason': f'Near-median delta={delta:+.4f}',
                'fg_ssim_125': fg125, 'fg_ssim_250': fg250, 'delta': delta
            })

    return selected


def build_manifest():
    uids = load_object_uids()
    selected = select_objects()
    manifest = {"version": "1.0", "date": "2026-06-14", "objects": []}

    for entry in selected:
        obj = entry['object_idx']
        uid = uids[obj] if obj < len(uids) else f"unknown_{obj}"
        data_dir = f"{DATA_ROOT}/{uid}"

        obj_entry = {
            "object_idx": obj,
            "uid": uid,
            "category": entry['category'],
            "selection_reason": entry['reason'],
            "metrics": {
                "fg_ssim_s1.25": entry.get('fg_ssim_125'),
                "fg_ssim_s2.50": entry.get('fg_ssim_250'),
                "delta": entry.get('delta'),
            },
            "source_data": {
                "data_dir": data_dir,
                "image_dir": f"{data_dir}/image",
                "camera_dir": f"{data_dir}/camera",
                "depth_dir": f"{data_dir}/depth_png",
                "normal_dir": f"{data_dir}/normal",
                "meta_npy": f"{data_dir}/meta.npy",
            },
            "eval_outputs": {},
            "available_views": [],
            "missing_assets": [],
            "sha256": {},
        }

        # Check source data
        for key, path in obj_entry["source_data"].items():
            if key.endswith('_dir'):
                if os.path.isdir(path):
                    files = sorted(os.listdir(path))
                    obj_entry["available_views"] = [f for f in files if f.endswith('.png')]
                else:
                    obj_entry["missing_assets"].append(f"source:{key}")
            elif os.path.exists(path):
                obj_entry["sha256"][key] = sha256_file(path)
            else:
                obj_entry["missing_assets"].append(f"source:{key}")

        # Check eval outputs
        for eval_name, eval_dir in EVAL_DIRS.items():
            vis_dir = f"{eval_dir}/visualizations"
            entry_data = {"dir": eval_dir, "vis": {}}
            for suffix in ['gt', 'orig', 'adapter']:
                path = f"{vis_dir}/obj_{obj:03d}_{suffix}.png"
                if os.path.exists(path):
                    entry_data["vis"][suffix] = path
                    obj_entry["sha256"][f"{eval_name}_{suffix}"] = sha256_file(path)
                else:
                    entry_data["vis"][suffix] = None
            obj_entry["eval_outputs"][eval_name] = entry_data

        # Check mesh/texture (for relighting)
        mesh_path = f"{data_dir}/{uid}.obj"
        if os.path.exists(mesh_path):
            obj_entry["source_data"]["mesh"] = mesh_path
            obj_entry["sha256"]["mesh"] = sha256_file(mesh_path)
        else:
            obj_entry["missing_assets"].append("mesh (not in source data, requires bake pipeline)")

        manifest["objects"].append(obj_entry)

    # Save manifest
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = f"{OUTPUT_DIR}/visual_manifest.json"
    with open(out_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest: {len(manifest['objects'])} objects")
    for cat in ['severe_regression', 'borderline_regression', 'best_improvement', 'median']:
        objs = [o for o in manifest['objects'] if o['category'] == cat]
        print(f"  {cat}: {len(objs)} objects")
    print(f"Saved: {out_path}")
    return manifest


if __name__ == '__main__':
    build_manifest()
