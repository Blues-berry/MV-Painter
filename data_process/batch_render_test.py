"""
Batch render test objects using Blender.
Reads from test_render_queue.json and renders each object.
"""
import json
import os
import subprocess
from tqdm import tqdm
from multiprocessing import Pool

BLENDER_PATH = '/4T/CXY/MV-Painter/blender-4.2.4-linux-x64/blender'
SCRIPT_PATH = '/4T/CXY/MV-Painter/data_process/blender_script.py'
OUTPUT_DIR = '/4T/CXY/MV-Painter/data/train_data/rendered_full'
HDRI_PATH = '/home/ubuntu/ssd_work/projects/spar3d/demo_files/hdri/studio_small_08_1k.hdr'

def render_object(args):
    """Render a single object using Blender."""
    obj_id, glb_path = args
    obj_output = os.path.join(OUTPUT_DIR, obj_id)

    # Skip if already rendered with all files
    if os.path.exists(os.path.join(obj_output, 'image', '016.png')) and \
       os.path.exists(os.path.join(obj_output, 'camera', '016.npy')):
        return obj_id, 'skip'

    # Remove incomplete render
    if os.path.exists(obj_output):
        import shutil
        shutil.rmtree(obj_output)

    try:
        cmd = [
            BLENDER_PATH, '-noaudio', '--background', '-Y',
            '--python', SCRIPT_PATH, '--',
            '--object_path', glb_path,
            '--object_uid', obj_id,
            '--output_dir', OUTPUT_DIR,
            '--hdri_path', HDRI_PATH
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            return obj_id, 'success'
        else:
            return obj_id, f'error: {result.stderr[-200:]}'
    except subprocess.TimeoutExpired:
        return obj_id, 'timeout'
    except Exception as e:
        return obj_id, f'exception: {str(e)[:200]}'

def main():
    # Load render queue
    queue_file = '/4T/CXY/MV-Painter/data/train_data/test_render_queue.json'
    with open(queue_file) as f:
        render_queue = json.load(f)

    # Convert to list of tuples
    items = list(render_queue.items())
    print(f'Total test objects to render: {len(items)}')

    # Process with multiprocessing (limit to 6 concurrent Blender instances)
    results = {'success': 0, 'skip': 0, 'error': 0, 'timeout': 0}

    with Pool(processes=6) as pool:
        for obj_id, status in tqdm(pool.imap_unordered(render_object, items), total=len(items)):
            if status == 'success':
                results['success'] += 1
            elif status == 'skip':
                results['skip'] += 1
            elif status == 'timeout':
                results['timeout'] += 1
            else:
                results['error'] += 1
                print(f'Error {obj_id}: {status}')

    print(f'\nResults:')
    for k, v in results.items():
        print(f'  {k}: {v}')

if __name__ == '__main__':
    main()
