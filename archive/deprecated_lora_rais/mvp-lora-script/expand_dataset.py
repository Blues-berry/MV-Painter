"""
Expand MV-Painter dataset with 3D objects from SF3D/NG projects.
Renders multi-view images using Blender.
"""
import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from tqdm import tqdm


def find_3d_objects(base_dirs):
    """Find all 3D model files (.glb, .obj) in the given directories."""
    objects = []
    for base_dir in base_dirs:
        for ext in ['*.glb', '*.obj', '*.gltf']:
            for path in Path(base_dir).rglob(ext):
                objects.append(str(path))
    return objects


def filter_objects(objects, existing_ids, min_size_kb=10, max_size_mb=100):
    """Filter objects by size and exclude existing ones."""
    filtered = []
    for obj_path in objects:
        # Get object ID from filename
        obj_id = Path(obj_path).stem

        # Skip if already in dataset
        if obj_id in existing_ids:
            continue

        # Check file size
        size_kb = os.path.getsize(obj_path) / 1024
        if size_kb < min_size_kb or size_kb > max_size_mb * 1024:
            continue

        filtered.append((obj_id, obj_path))

    return filtered


def render_object(obj_path, output_dir, blender_path, render_script, num_views=17):
    """Render multi-view images for a single object.

    Uses the data_process/blender_script.py which renders 17 views.
    """
    # Get object UID from filename
    obj_uid = os.path.basename(obj_path).split('.')[0]

    # The render script expects:
    # --object_path: path to GLB file
    # --object_uid: object identifier
    # --output_dir: parent directory for rendered output
    # --hdri_path: path to HDRI lighting file

    parent_dir = os.path.dirname(output_dir)
    hdri_path = '/4T/CXY/MV-Painter/data_process/abandoned_bakery_1k.hdr'

    # Check if HDRI exists, use fallback if not
    if not os.path.exists(hdri_path):
        hdri_path = '/4T/CXY/MV-Painter/MVPainter/scripts/overcast_soil_puresky_4k.exr'

    cmd = [
        blender_path,
        '-noaudio',
        '--background',
        '-Y',
        '--python', render_script,
        '--',
        '--object_path', obj_path,
        '--object_uid', obj_uid,
        '--output_dir', parent_dir,
        '--hdri_path', hdri_path,
        '--num_images', str(num_views),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception) as e:
        print(f"  Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Expand MV-Painter dataset')
    parser.add_argument('--sf3d_dir', type=str,
                        default='/4T/CXY/stable-fast-3d-output/output',
                        help='SF3D output directory')
    parser.add_argument('--ng_dir', type=str,
                        default='/4T/CXY/Neural_Gaffer_original',
                        help='Neural Gaffer directory')
    parser.add_argument('--output_dir', type=str,
                        default='/4T/CXY/MV-Painter/data/train_data/rendered_full',
                        help='Output directory for rendered images')
    parser.add_argument('--blender_path', type=str,
                        default='/4T/CXY/MV-Painter/blender-4.2.4-linux-x64/blender',
                        help='Path to Blender executable')
    parser.add_argument('--render_script', type=str,
                        default='/4T/CXY/MV-Painter/data_process/blender_script.py',
                        help='Path to Blender render script')
    parser.add_argument('--max_objects', type=int, default=200,
                        help='Maximum number of objects to add')
    parser.add_argument('--dry_run', action='store_true',
                        help='Only list objects without rendering')

    args = parser.parse_args()

    # Get existing object IDs
    existing_ids = set()
    if os.path.exists(args.output_dir):
        existing_ids = set(os.listdir(args.output_dir))
    print(f"Existing objects in dataset: {len(existing_ids)}")

    # Find 3D objects
    print("Searching for 3D objects...")
    base_dirs = [args.sf3d_dir, args.ng_dir]
    all_objects = find_3d_objects(base_dirs)
    print(f"Found {len(all_objects)} total 3D files")

    # Filter objects
    filtered = filter_objects(all_objects, existing_ids)
    print(f"After filtering: {len(filtered)} new objects available")

    # Limit to max_objects
    objects_to_render = filtered[:args.max_objects]
    print(f"Will render: {len(objects_to_render)} objects")

    if args.dry_run:
        print("\n[DRY RUN] Objects to render:")
        for obj_id, obj_path in objects_to_render[:20]:
            print(f"  {obj_id}: {obj_path}")
        if len(objects_to_render) > 20:
            print(f"  ... and {len(objects_to_render) - 20} more")
        return

    # Render objects
    success_count = 0
    fail_count = 0

    for obj_id, obj_path in tqdm(objects_to_render, desc="Rendering"):
        output_subdir = os.path.join(args.output_dir, obj_id)

        # Skip if already rendered
        if os.path.exists(output_subdir) and len(os.listdir(os.path.join(output_subdir, 'image'))) >= 17:
            print(f"  Skipping {obj_id}: already rendered")
            success_count += 1
            continue

        print(f"\nRendering {obj_id}...")
        os.makedirs(output_subdir, exist_ok=True)

        if render_object(obj_path, output_subdir, args.blender_path, args.render_script):
            # Verify output
            image_dir = os.path.join(output_subdir, 'image')
            if os.path.exists(image_dir) and len(os.listdir(image_dir)) >= 17:
                success_count += 1
                print(f"  Success: {obj_id}")
            else:
                fail_count += 1
                print(f"  Failed: insufficient images rendered")
        else:
            fail_count += 1
            print(f"  Failed: render error")

    # Summary
    print(f"\n{'='*60}")
    print("RENDERING COMPLETE")
    print(f"{'='*60}")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total objects in dataset: {len(existing_ids) + success_count}")

    # Generate manifest
    manifest_path = os.path.join(os.path.dirname(args.output_dir), 'dataset_manifest.json')
    manifest = {
        'total_objects': len(existing_ids) + success_count,
        'new_objects': success_count,
        'sources': {
            'sf3d': args.sf3d_dir,
            'neural_gaffer': args.ng_dir,
        },
        'render_config': {
            'num_views': 17,
            'resolution': [512, 512],
            'engine': 'CYCLES',
        }
    }

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest saved to {manifest_path}")


if __name__ == '__main__':
    main()
