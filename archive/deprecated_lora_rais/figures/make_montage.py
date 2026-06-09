"""
Create comparison montages: Input | Zero-shot | LoRA-r4 | LoRA-r8
"""
import os
from PIL import Image, ImageDraw, ImageFont

RESULTS_DIR = 'fixed_comparison_results'
TRAIN_DATA = '/4T/CXY/MV-Painter/data/train_data/rendered_full'
MONTAGE_DIR = 'montages'
os.makedirs(MONTAGE_DIR, exist_ok=True)

with open(os.path.join(TRAIN_DATA, 'clean_objects.txt')) as f:
    all_objects = [l.strip() for l in f.readlines() if l.strip()]
test_objects = all_objects[-4:]

COLS = ['Input', 'Zero-shot', 'LoRA-r4', 'LoRA-r8']

for obj in test_objects:
    print(f'Creating montage for {obj}...')

    # Load input image
    input_path = os.path.join(TRAIN_DATA, obj, 'image', '000.png')
    if not os.path.exists(input_path):
        print(f'  Skipping {obj}: input not found')
        continue
    input_img = Image.open(input_path).convert('RGB')

    # Load results
    imgs = [input_img]
    for variant in ['zeroshot', 'lora_r4', 'lora_r8']:
        result_path = os.path.join(RESULTS_DIR, f'{obj}_{variant}', 'result_6view.png')
        if os.path.exists(result_path):
            imgs.append(Image.open(result_path).convert('RGB'))
        else:
            # Create blank placeholder
            imgs.append(Image.new('RGB', (512, 768), (128, 128, 128)))

    # Resize all to same height
    target_h = 600
    resized = []
    for img in imgs:
        aspect = img.width / img.height
        w = int(target_h * aspect)
        resized.append(img.resize((w, target_h), Image.LANCZOS))

    # Create montage
    margin = 20
    label_h = 40
    total_w = sum(r.width for r in resized) + margin * (len(resized) + 1)
    total_h = target_h + label_h + margin * 2

    montage = Image.new('RGB', (total_w, total_h), (255, 255, 255))
    draw = ImageDraw.Draw(montage)

    # Try to get a font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except:
        font = ImageFont.load_default()

    x = margin
    for i, (label, img) in enumerate(zip(COLS, resized)):
        # Draw label
        draw.text((x + 5, margin // 2), label, fill=(0, 0, 0), font=font)
        # Paste image
        montage.paste(img, (x, label_h + margin))
        x += img.width + margin

    out_path = os.path.join(MONTAGE_DIR, f'{obj}_comparison.png')
    montage.save(out_path)
    print(f'  Saved: {out_path} ({montage.width}x{montage.height})')

# Also create a combined montage with all samples
print('\nCreating combined overview...')
all_montages = []
for obj in test_objects:
    path = os.path.join(MONTAGE_DIR, f'{obj}_comparison.png')
    if os.path.exists(path):
        all_montages.append(Image.open(path))

if all_montages:
    # Resize all to same width
    max_w = max(m.width for m in all_montages)
    resized_montages = []
    for m in all_montages:
        if m.width != max_w:
            ratio = max_w / m.width
            m = m.resize((max_w, int(m.height * ratio)), Image.LANCZOS)
        resized_montages.append(m)

    # Stack vertically
    total_h = sum(m.height for m in resized_montages) + 10 * (len(resized_montages) - 1)
    combined = Image.new('RGB', (max_w, total_h), (255, 255, 255))
    y = 0
    for m in resized_montages:
        combined.paste(m, (0, y))
        y += m.height + 10

    combined.save(os.path.join(MONTAGE_DIR, 'all_samples_comparison.png'))
    print(f'Saved combined: {MONTAGE_DIR}/all_samples_comparison.png')

print('\nDone!')
