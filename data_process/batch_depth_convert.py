"""
Batch convert depth EXR to PNG for all objects in rendered_full.
"""
import OpenEXR
import Imath
from PIL import Image
import numpy as np
import os
import sys
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

def depth_exr_to_png(exr_file, png_file, depth_channel='V', depth_scale=1.0):
    """Convert a single depth EXR file to PNG."""
    try:
        exr_image = OpenEXR.InputFile(exr_file)
        header = exr_image.header()
        size = (header['displayWindow'].max.x + 1, header['displayWindow'].max.y + 1)
        depth_channel_data = exr_image.channel(depth_channel, Imath.PixelType(Imath.PixelType.FLOAT))
        depth_array = np.frombuffer(depth_channel_data, dtype=np.float32).copy()
        depth_array = depth_array.reshape((size[1], size[0]))
        invalid_mask = depth_array == 1.0
        depth_array /= depth_scale
        depth_array_uint16 = (depth_array * 65535).astype(np.uint16)
        depth_array_uint16[invalid_mask] = 65535
        depth_image = Image.fromarray(depth_array_uint16)
        depth_image.save(png_file)
        return True
    except Exception as e:
        print(f'Error processing {exr_file}: {e}', file=sys.stderr)
        return False

def process_object(args):
    """Process a single object: convert all depth EXR files to PNG."""
    obj_id, rendered_dir = args
    obj_path = os.path.join(rendered_dir, obj_id)
    depth_exr_dir = os.path.join(obj_path, 'depth')
    depth_png_dir = os.path.join(obj_path, 'depth_png')

    # Skip if already has depth_png
    if os.path.exists(depth_png_dir) and len(os.listdir(depth_png_dir)) > 0:
        return obj_id, 'skip'

    # Skip if no depth EXR
    if not os.path.exists(depth_exr_dir) or len(os.listdir(depth_exr_dir)) == 0:
        return obj_id, 'no_exr'

    os.makedirs(depth_png_dir, exist_ok=True)

    exr_files = [f for f in os.listdir(depth_exr_dir) if f.endswith('.exr')]
    success_count = 0
    for exr_file in exr_files:
        exr_path = os.path.join(depth_exr_dir, exr_file)
        png_path = os.path.join(depth_png_dir, exr_file.replace('.exr', '.png'))
        if depth_exr_to_png(exr_path, png_path):
            success_count += 1

    if success_count == len(exr_files):
        return obj_id, 'success'
    else:
        return obj_id, f'partial_{success_count}/{len(exr_files)}'

def main():
    rendered_dir = '/4T/CXY/MV-Painter/data/train_data/rendered_full'

    # Find objects needing conversion
    objects_to_process = []
    for obj_id in os.listdir(rendered_dir):
        obj_path = os.path.join(rendered_dir, obj_id)
        if not os.path.isdir(obj_path):
            continue
        depth_png = os.path.join(obj_path, 'depth_png')
        depth_exr = os.path.join(obj_path, 'depth')
        if os.path.exists(depth_exr) and len(os.listdir(depth_exr)) > 0:
            if not os.path.exists(depth_png) or len(os.listdir(depth_png)) == 0:
                objects_to_process.append((obj_id, rendered_dir))

    print(f'Objects needing depth conversion: {len(objects_to_process)}')

    # Process with multiprocessing
    results = {'success': 0, 'skip': 0, 'no_exr': 0, 'partial': 0, 'error': 0}

    with Pool(processes=min(cpu_count(), 16)) as pool:
        for obj_id, status in tqdm(pool.imap_unordered(process_object, objects_to_process), total=len(objects_to_process)):
            if status == 'success':
                results['success'] += 1
            elif status == 'skip':
                results['skip'] += 1
            elif status == 'no_exr':
                results['no_exr'] += 1
            elif status.startswith('partial'):
                results['partial'] += 1
            else:
                results['error'] += 1

    print(f'\nResults:')
    for k, v in results.items():
        print(f'  {k}: {v}')

if __name__ == '__main__':
    main()
