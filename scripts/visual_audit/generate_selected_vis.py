"""Generate visualizations for selected objects only.

Calls eval_scale_inline_visual_only.py (NOT the canonical evaluator).
Output isolated under visual_artifacts_s250_audit/vis_selected/

Usage:
    python scripts/visual_audit/generate_selected_vis.py --dry-run --device cuda:0
    python scripts/visual_audit/generate_selected_vis.py --device cuda:0
"""
import argparse, json, os, sys, subprocess

MANIFEST = "/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1/visual_artifacts_s250_audit/visual_manifest.json"
CONFIG = "/4T/CXY/MV-Painter/mvpoutput/geotex/eval_config_snapshot.yaml"
CHECKPOINT = "/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1/checkpoints/geotex_step_0002000.pt"
OUTPUT_BASE = "/4T/CXY/MV-Painter/mvpoutput/geotex_refattn_v1/visual_artifacts_s250_audit/vis_selected"
VISUAL_ONLY_SCRIPT = "/4T/CXY/MV-Painter/scripts/visual_audit/eval_scale_inline_visual_only.py"
SCALES = [1.25, 2.25, 2.50]
SEED = 42
STEPS = 50


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    with open(MANIFEST) as f:
        manifest = json.load(f)

    obj_indices = [o['object_idx'] for o in manifest['objects']]
    objs_str = ",".join(str(o) for o in obj_indices)
    total_images = len(obj_indices) * 3 * len(SCALES)  # gt/orig/adapter × objects × scales

    print("=" * 70)
    print("SELECTED VISUALIZATION — DRY RUN REPORT" if args.dry_run else "SELECTED VISUALIZATION — EXECUTION")
    print("=" * 70)
    print()
    print(f"Visual-only script: {VISUAL_ONLY_SCRIPT}")
    print(f"  (NOT the canonical evaluator)")
    print()
    print(f"Config:      {CONFIG}")
    print(f"Checkpoint:  {CHECKPOINT}")
    print(f"Seed:        {SEED}")
    print(f"Steps:       {STEPS}")
    print(f"Device:      {args.device}")
    print()
    print(f"Selected objects ({len(obj_indices)}): {obj_indices}")
    print(f"Scales: {SCALES}")
    print()

    for scale in SCALES:
        scale_name = f"s{scale}".replace('.', 'p')
        output_dir = f"{OUTPUT_BASE}/{scale_name}"
        vis_dir = f"{output_dir}/visualizations"

        existing = 0
        missing = 0
        for obj in obj_indices:
            for suffix in ['gt', 'orig', 'adapter']:
                path = f"{vis_dir}/obj_{obj:03d}_{suffix}.png"
                if os.path.exists(path):
                    existing += 1
                else:
                    missing += 1

        print(f"Scale {scale:.2f} → {scale_name}")
        print(f"  Output dir:   {output_dir}")
        print(f"  Existing vis: {existing}/{len(obj_indices)*3}")
        print(f"  Missing vis:  {missing}/{len(obj_indices)*3}")
        if existing > 0:
            print(f"  ⚠️ {existing} files exist — will NOT overwrite (visual-only script saves only new)")
        print()

    print(f"Total images to generate: {total_images - existing_total(OUTPUT_BASE, obj_indices, SCALES)}")
    print()

    if args.dry_run:
        print("--- DRY RUN MODE ---")
        print(f"Model inference called during dry-run?  NO")
        print(f"GPU used during dry-run?                NO")
        print(f"Images generated during dry-run?         NO")
        print(f"Files written during dry-run?            NO")
        print()
        print(f"If run WITHOUT --dry-run:")
        print(f"  Model inference called?                YES (diffusion UNet forward pass)")
        print(f"  GPU used?                              YES ({args.device})")
        print(f"  Images generated?                      YES (~{total_images} PNGs)")
        print(f"  Written to canonical eval dir?          NO (isolated under vis_selected/)")
        print(f"  Written to 300-object eval dir?         NO")
        print(f"  Overwrites existing canonical results?  NO")
        print()
        print("NOT executed. Run without --dry-run to generate.")
        return

    # Execution
    for scale in SCALES:
        scale_name = f"s{scale}".replace('.', 'p')
        output_dir = f"{OUTPUT_BASE}/{scale_name}"
        os.makedirs(output_dir, exist_ok=True)

        cmd = [
            sys.executable, VISUAL_ONLY_SCRIPT,
            "--config", CONFIG,
            "--checkpoint", CHECKPOINT,
            "--scale", str(scale),
            "--objects", objs_str,
            "--output_dir", output_dir,
            "--device", args.device,
            "--seed", str(SEED),
            "--steps", str(STEPS),
        ]

        print(f"\n{'='*60}")
        print(f"Running scale={scale} for {len(obj_indices)} objects")
        print(f"Output: {output_dir}")
        print(f"{'='*60}")

        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            print(f"WARNING: scale={scale} returned {result.returncode}")
        else:
            print(f"Done: scale={scale}")

    # Update manifest
    print(f"\nUpdating manifest...")
    with open(MANIFEST) as f:
        manifest = json.load(f)

    for obj_entry in manifest['objects']:
        obj = obj_entry['object_idx']
        for scale in SCALES:
            scale_name = f"s{scale}".replace('.', 'p')
            eval_key = f"{scale_name}_selected"
            vis_dir = f"{OUTPUT_BASE}/{scale_name}/visualizations"
            entry_data = {"dir": f"{OUTPUT_BASE}/{scale_name}", "vis": {}}
            for suffix in ['gt', 'orig', 'adapter']:
                path = f"{vis_dir}/obj_{obj:03d}_{suffix}.png"
                entry_data["vis"][suffix] = path if os.path.exists(path) else None
            obj_entry["eval_outputs"][eval_key] = entry_data

    with open(MANIFEST, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest updated: {MANIFEST}")


def existing_total(output_base, obj_indices, scales):
    count = 0
    for scale in scales:
        scale_name = f"s{scale}".replace('.', 'p')
        vis_dir = f"{output_base}/{scale_name}/visualizations"
        for obj in obj_indices:
            for suffix in ['gt', 'orig', 'adapter']:
                if os.path.exists(f"{vis_dir}/obj_{obj:03d}_{suffix}.png"):
                    count += 1
    return count


if __name__ == '__main__':
    main()
