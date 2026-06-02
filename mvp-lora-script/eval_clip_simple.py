"""
Simple CLIP evaluation using existing images.
"""
import numpy as np
from PIL import Image
import torch
from transformers import CLIPModel, CLIPProcessor

# Load CLIP
print('Loading CLIP...')
clip_model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32').to('cuda')
clip_processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')
print('CLIP loaded')

# Test objects
test_objects = [
    'd6a5427888b8413fbfcbcaad14353af8',
    'aa82baf218104070a932dee9a1db61ce',
    'e3f35d4cfbb14410bf96a4ffa28235a1',
]

base_dir = '/4T/CXY/MV-Painter/mvpoutput/three_way_comparison'

def clip_sim(img1, img2):
    inputs1 = clip_processor(images=img1, return_tensors='pt').to('cuda')
    inputs2 = clip_processor(images=img2, return_tensors='pt').to('cuda')
    with torch.no_grad():
        f1 = clip_model.get_image_features(**inputs1)
        f2 = clip_model.get_image_features(**inputs2)
    f1 = f1 / f1.norm(dim=-1, keepdim=True)
    f2 = f2 / f2.norm(dim=-1, keepdim=True)
    return (f1 * f2).sum(dim=-1).item()

results = []
for obj_id in test_objects:
    gt_path = f'/4T/CXY/MV-Painter/data/train_data/rendered_full/{obj_id}/image/000.png'
    orig_path = f'{base_dir}/{obj_id}_original.png'
    broken_path = f'{base_dir}/{obj_id}_broken.png'
    working_path = f'{base_dir}/{obj_id}_attn2only.png'

    gt = Image.open(gt_path).convert('RGB')
    orig = Image.open(orig_path).convert('RGB')
    broken = Image.open(broken_path).convert('RGB')
    working = Image.open(working_path).convert('RGB')

    clip_a = clip_sim(gt, orig)
    clip_b = clip_sim(gt, broken)
    clip_c = clip_sim(gt, working)

    print(f'{obj_id[:16]}: A={clip_a:.4f}, B={clip_b:.4f}, C={clip_c:.4f}')
    results.append({'id': obj_id, 'a': clip_a, 'b': clip_b, 'c': clip_c})

print(f'\nAverage:')
print(f'  Original: {np.mean([r["a"] for r in results]):.4f}')
print(f'  Crashed:  {np.mean([r["b"] for r in results]):.4f}')
print(f'  Working:  {np.mean([r["c"] for r in results]):.4f}')
