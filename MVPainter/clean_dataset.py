"""Filter training samples with missing depth/normal/image files."""
import os
import json

root = '/4T/CXY/MV-Painter/data/train_data/rendered_full'
required_views = ['000.png', '014.png']
required_dirs = ['image', 'normal', 'depth_png']

all_objects = sorted(os.listdir(root))
print(f'Total objects: {len(all_objects)}')

valid = []
invalid = []
for obj in all_objects:
    obj_path = os.path.join(root, obj)
    if not os.path.isdir(obj_path):
        continue

    missing = []
    for d in required_dirs:
        dir_path = os.path.join(obj_path, d)
        if not os.path.isdir(dir_path):
            missing.append(f'{d}/')
            continue
        for v in required_views:
            fpath = os.path.join(dir_path, v)
            if not os.path.isfile(fpath) or os.path.getsize(fpath) == 0:
                missing.append(f'{d}/{v}')

    if missing:
        invalid.append((obj, missing))
    else:
        valid.append(obj)

print(f'Valid: {len(valid)}')
print(f'Invalid: {len(invalid)}')

# Save clean list
out_path = os.path.join(root, 'clean_objects.txt')
with open(out_path, 'w') as f:
    for obj in valid:
        f.write(obj + '\n')
print(f'Saved clean list to {out_path}')

# Save invalid list with reasons
inv_path = os.path.join(root, 'invalid_objects.txt')
with open(inv_path, 'w') as f:
    for obj, missing in invalid:
        f.write(f'{obj}: {", ".join(missing)}\n')
print(f'Saved invalid list to {inv_path}')

# Show some examples
if invalid:
    print(f'\nFirst 10 invalid samples:')
    for obj, missing in invalid[:10]:
        print(f'  {obj}: {", ".join(missing)}')
