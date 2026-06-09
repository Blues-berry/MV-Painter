"""
Clean up invalid/incomplete objects from rendered_full dataset.

Removes objects that:
1. Are listed in invalid_objects.txt
2. Have incomplete rendering (< 17 views for image/normal/depth/camera)
3. Are missing depth_png directory
4. Are missing embeddings/global_embeds.npy

Also generates a quality report before deletion.
"""
import os
import sys
import json
import shutil
import argparse
from datetime import datetime


RENDERED_DIR = '/4T/CXY/MV-Painter/data/train_data/rendered_full'
REQUIRED_DIRS = ['image', 'normal', 'depth', 'depth_png', 'camera']
REQUIRED_FILES = ['meta.npy']
EMBED_FILE = 'embeddings/global_embeds.npy'
MIN_VIEWS = 17


def load_invalid_objects():
    """Load invalid_objects.txt."""
    invalid_path = os.path.join(RENDERED_DIR, 'invalid_objects.txt')
    invalid = set()
    if os.path.exists(invalid_path):
        with open(invalid_path) as f:
            for line in f:
                obj_id = line.split(':')[0].strip()
                if obj_id:
                    invalid.add(obj_id)
    return invalid


def load_clean_objects():
    """Load clean_objects.txt."""
    clean_path = os.path.join(RENDERED_DIR, 'clean_objects.txt')
    clean = set()
    if os.path.exists(clean_path):
        with open(clean_path) as f:
            for line in f:
                obj_id = line.strip()
                if obj_id:
                    clean.add(obj_id)
    return clean


def check_object(obj_id):
    """Check if an object has all required components.

    Returns (is_valid, issues_list).
    """
    obj_dir = os.path.join(RENDERED_DIR, obj_id)
    issues = []

    if not os.path.isdir(obj_dir):
        return False, ['directory_missing']

    # Check required directories with minimum views
    for d in REQUIRED_DIRS:
        dpath = os.path.join(obj_dir, d)
        if not os.path.exists(dpath):
            issues.append(f'{d}_missing')
        else:
            # Count only actual view files, not subdirectories
            if d == 'camera':
                count = len([f for f in os.listdir(dpath) if f.endswith('.npy')])
            elif d == 'depth':
                count = len([f for f in os.listdir(dpath) if f.endswith('.exr')])
            else:
                count = len([f for f in os.listdir(dpath) if f.endswith('.png')])
            if count < MIN_VIEWS:
                issues.append(f'{d}_partial({count}/{MIN_VIEWS})')

    # Check required files
    for f in REQUIRED_FILES:
        if not os.path.exists(os.path.join(obj_dir, f)):
            issues.append(f'{f}_missing')

    # Check embeddings
    embed_path = os.path.join(obj_dir, EMBED_FILE)
    if not os.path.exists(embed_path):
        issues.append('embeddings_missing')

    return len(issues) == 0, issues


def audit_dataset():
    """Audit all objects and return categorization."""
    invalid_set = load_invalid_objects()
    clean_set = load_clean_objects()

    results = {
        'clean': [],           # In clean_objects.txt and valid
        'invalid_listed': [],  # In invalid_objects.txt
        'incomplete': [],      # Not in clean, has issues
        'ready_not_clean': [], # Not in clean, but fully valid
        'partial_render': [],  # Has directory but < 17 views (new renders)
    }

    for obj_id in sorted(os.listdir(RENDERED_DIR)):
        obj_dir = os.path.join(RENDERED_DIR, obj_id)
        if not os.path.isdir(obj_dir):
            continue

        is_valid, issues = check_object(obj_id)

        if obj_id in invalid_set:
            results['invalid_listed'].append((obj_id, issues))
        elif obj_id in clean_set:
            if is_valid:
                results['clean'].append((obj_id, []))
            else:
                results['incomplete'].append((obj_id, issues))
        elif is_valid:
            results['ready_not_clean'].append((obj_id, []))
        else:
            # Check if it's a partial render (new from queue)
            obj_dir_path = os.path.join(RENDERED_DIR, obj_id, 'image')
            if os.path.exists(obj_dir_path):
                img_count = len(os.listdir(obj_dir_path))
                if img_count < MIN_VIEWS:
                    results['partial_render'].append((obj_id, issues))
                else:
                    results['incomplete'].append((obj_id, issues))
            else:
                results['incomplete'].append((obj_id, issues))

    return results


def generate_report(results, output_path):
    """Generate audit report."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'clean_valid': len(results['clean']),
            'invalid_listed': len(results['invalid_listed']),
            'incomplete': len(results['incomplete']),
            'ready_not_clean': len(results['ready_not_clean']),
            'partial_render': len(results['partial_render']),
        },
        'details': {
            'invalid_listed': [(oid, iss) for oid, iss in results['invalid_listed']],
            'incomplete': [(oid, iss) for oid, iss in results['incomplete']],
            'partial_render': [(oid, iss) for oid, iss in results['partial_render']],
        }
    }

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    return report


def delete_objects(obj_list, dry_run=True, label=""):
    """Delete objects from disk."""
    if not obj_list:
        print(f"  No {label} objects to delete.")
        return 0

    deleted = 0
    for obj_id, issues in obj_list:
        obj_dir = os.path.join(RENDERED_DIR, obj_id)
        if os.path.isdir(obj_dir):
            if dry_run:
                print(f"  [DRY RUN] Would delete: {obj_id} ({', '.join(issues) if issues else 'no issues'})")
            else:
                try:
                    shutil.rmtree(obj_dir)
                    print(f"  Deleted: {obj_id}")
                    deleted += 1
                except Exception as e:
                    print(f"  Error deleting {obj_id}: {e}")
    return deleted


def update_clean_objects(results):
    """Update clean_objects.txt with valid objects only."""
    clean_ids = sorted([obj_id for obj_id, _ in results['clean']])
    clean_path = os.path.join(RENDERED_DIR, 'clean_objects.txt')

    # Backup old file
    backup_path = clean_path + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    if os.path.exists(clean_path):
        shutil.copy2(clean_path, backup_path)
        print(f"  Backed up to: {backup_path}")

    with open(clean_path, 'w') as f:
        for obj_id in clean_ids:
            f.write(obj_id + '\n')
    print(f"  Updated clean_objects.txt: {len(clean_ids)} objects")


def main():
    parser = argparse.ArgumentParser(description='Clean up invalid objects from dataset')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Only show what would be deleted (default: True)')
    parser.add_argument('--delete', action='store_true',
                        help='Actually delete invalid objects')
    parser.add_argument('--delete-incomplete', action='store_true',
                        help='Also delete incomplete/partial render objects')
    parser.add_argument('--update-clean', action='store_true',
                        help='Update clean_objects.txt with valid objects only')
    parser.add_argument('--report', type=str,
                        default='/4T/CXY/MV-Painter/mvpoutput/dataset_audit.json',
                        help='Path to save audit report')
    args = parser.parse_args()

    dry_run = not args.delete

    print("=" * 60)
    print("Dataset Audit & Cleanup")
    print("=" * 60)

    # Audit
    print("\n[1/4] Auditing dataset...")
    results = audit_dataset()

    print(f"\n  Clean & valid:      {len(results['clean'])}")
    print(f"  Invalid (listed):   {len(results['invalid_listed'])}")
    print(f"  Incomplete:         {len(results['incomplete'])}")
    print(f"  Ready but not clean:{len(results['ready_not_clean'])}")
    print(f"  Partial render:     {len(results['partial_render'])}")

    # Generate report
    print(f"\n[2/4] Generating report...")
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    report = generate_report(results, args.report)
    print(f"  Report saved to: {args.report}")

    # Delete invalid objects
    print(f"\n[3/4] Cleaning up invalid objects...")
    if dry_run:
        print("  Mode: DRY RUN (use --delete to actually delete)")
    else:
        print("  Mode: DELETING")

    deleted = delete_objects(results['invalid_listed'], dry_run, "invalid_listed")

    if args.delete_incomplete:
        deleted += delete_objects(results['incomplete'], dry_run, "incomplete")
        deleted += delete_objects(results['partial_render'], dry_run, "partial_render")

    if dry_run:
        print(f"\n  Would delete {len(results['invalid_listed'])} invalid objects")
        if args.delete_incomplete:
            print(f"  Would delete {len(results['incomplete'])} incomplete objects")
            print(f"  Would delete {len(results['partial_render'])} partial render objects")
    else:
        print(f"\n  Deleted {deleted} objects")

    # Update clean_objects.txt
    if args.update_clean:
        print(f"\n[4/4] Updating clean_objects.txt...")
        update_clean_objects(results)
    else:
        print(f"\n[4/4] Skipping clean_objects.txt update (use --update-clean)")

    # Final summary
    remaining = len(results['clean']) + len(results['ready_not_clean'])
    if not dry_run:
        remaining -= deleted
    print(f"\n{'=' * 60}")
    print(f"Final: {remaining} valid objects remaining in dataset")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
