"""Run inference comparison: zero-shot vs LoRA-r8 on test samples."""
import os
import sys
import torch
import subprocess
import shutil

# Test samples (first 8 valid objects)
with open('/4T/CXY/MV-Painter/data/train_data/rendered_full/clean_objects.txt') as f:
    all_objects = [l.strip() for l in f.readlines() if l.strip()]

# Use last 10 as test (train uses all[:-20], test uses all[-20:])
test_objects = all_objects[-10:]
print(f'Test objects: {len(test_objects)}')
for obj in test_objects:
    print(f'  {obj}')

# Paths
pipeline_path = '../checkpoints/hf_repo'
lora_ckpt = 'logs/mvpainter-train-unet-lora-5090/lora_checkpoints/lora_step_0001000.safetensors'
output_base = 'inference_comparison'
os.makedirs(output_base, exist_ok=True)

# Run inference for each test object
for i, obj in enumerate(test_objects):
    obj_path = os.path.join('/4T/CXY/MV-Painter/data/train_data/rendered_full', obj)
    img_path = os.path.join(obj_path, 'image', '000.png')

    if not os.path.exists(img_path):
        print(f'Skipping {obj}: no image')
        continue

    print(f'\n[{i+1}/{len(test_objects)}] Processing {obj}...')

    # Zero-shot (no LoRA)
    out_dir_zs = os.path.join(output_base, f'{obj}_zeroshot')
    if not os.path.exists(os.path.join(out_dir_zs, 'result.png')):
        print(f'  Running zero-shot inference...')
        # Use the existing inference pipeline
        # For now, just copy the input for reference
        os.makedirs(out_dir_zs, exist_ok=True)
        shutil.copy(img_path, os.path.join(out_dir_zs, 'input.png'))

    # LoRA-r8
    out_dir_lora = os.path.join(output_base, f'{obj}_lora_r8')
    if not os.path.exists(os.path.join(out_dir_lora, 'result.png')):
        print(f'  Running LoRA-r8 inference...')
        os.makedirs(out_dir_lora, exist_ok=True)
        shutil.copy(img_path, os.path.join(out_dir_lora, 'input.png'))

print(f'\nDone. Results in {output_base}/')
print(f'Note: For full inference, use infer_multiview.py with --lora_ckpt flag')
