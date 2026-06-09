"""Generate comparison figures from fixed_comparison_results."""
import os
from PIL import Image, ImageDraw, ImageFont

RESULTS_DIR = 'fixed_comparison_results'
OUTPUT_DIR = 'comparison_figures_new'
os.makedirs(OUTPUT_DIR, exist_ok=True)

SCALES = ['0.0', '0.1', '0.25', '0.5', '1.0']


def get_font(size=20):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()


def load_img(path, size=None):
    if not os.path.exists(path):
        return None
    img = Image.open(path).convert('RGB')
    if size:
        img = img.resize(size, Image.LANCZOS)
    return img


def draw_label(draw, x, y, text, font, color=(0, 0, 0)):
    draw.text((x + 5, y), text, fill=color, font=font)


# --- Find samples ---
samples = set()
for d in os.listdir(RESULTS_DIR):
    for suffix in ['_zeroshot', '_lora_r4', '_lora_r8']:
        if d.endswith(suffix):
            samples.add(d.replace(suffix, ''))
samples = sorted(samples)
print(f'Found {len(samples)} samples: {[s[:8] for s in samples]}')


# --- 1. Per-sample: zeroshot vs r4 vs r8 ---
def make_per_sample(sample):
    methods = [
        ('zeroshot', 'Zero-shot', (200, 50, 50)),
        ('lora_r4', 'LoRA r4', (50, 150, 50)),
        ('lora_r8', 'LoRA r8', (50, 50, 200)),
    ]
    imgs = []
    for method, label, color in methods:
        path = os.path.join(RESULTS_DIR, f'{sample}_{method}', 'result_6view.png')
        img = load_img(path, (512, 768))
        if img:
            imgs.append((label, img, color))

    if len(imgs) < 2:
        return

    margin = 10
    label_h = 40
    tw, th = 512, 768
    n = len(imgs)
    canvas_w = n * tw + (n + 1) * margin
    canvas_h = th + label_h + 2 * margin
    canvas = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    font = get_font(22)

    for i, (label, img, color) in enumerate(imgs):
        x = (i + 1) * margin + i * tw
        y = label_h + margin
        canvas.paste(img, (x, y))
        draw_label(draw, x, 5, label, font, color)

    out = os.path.join(OUTPUT_DIR, f'per_sample_{sample[:8]}.png')
    canvas.save(out, quality=95)
    print(f'  per-sample: {out}')


# --- 2. Scale sweep grid: r4 and r8 ---
def make_sweep_grid(sample, rank):
    imgs = []
    for s in SCALES:
        dirname = f'sweep_{sample}_r{rank}_s{s}'
        path = os.path.join(RESULTS_DIR, dirname, 'result_6view.png')
        img = load_img(path, (512, 768))
        if img:
            imgs.append((f's={s}', img))

    if len(imgs) < 2:
        return

    margin = 8
    label_h = 35
    tw, th = 512, 768
    n = len(imgs)
    canvas_w = n * tw + (n + 1) * margin
    canvas_h = th + label_h + 2 * margin
    canvas = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    font = get_font(20)

    for i, (label, img) in enumerate(imgs):
        x = (i + 1) * margin + i * tw
        y = label_h + margin
        canvas.paste(img, (x, y))
        color = (0, 100, 0) if rank == 4 else (0, 0, 150)
        draw_label(draw, x, 5, label, font, color)

    out = os.path.join(OUTPUT_DIR, f'sweep_r{rank}_{sample[:8]}.png')
    canvas.save(out, quality=95)
    print(f'  sweep r{rank}: {out}')


# --- 3. Combined: zeroshot | r4 s=best | r8 s=best ---
def make_combined(sample):
    # Pick best scale visually (s=0.5 is often good)
    methods = [
        ('zeroshot', f'{sample}_zeroshot', 'Zero-shot', (200, 50, 50)),
        ('r4_s0.5', f'sweep_{sample}_r4_s0.5', 'LoRA r4 s=0.5', (50, 150, 50)),
        ('r8_s0.5', f'sweep_{sample}_r8_s0.5', 'LoRA r8 s=0.5', (50, 50, 200)),
    ]
    imgs = []
    for key, dirname, label, color in methods:
        path = os.path.join(RESULTS_DIR, dirname, 'result_6view.png')
        img = load_img(path, (512, 768))
        if img:
            imgs.append((label, img, color))

    if len(imgs) < 2:
        return

    margin = 10
    label_h = 40
    tw, th = 512, 768
    n = len(imgs)
    canvas_w = n * tw + (n + 1) * margin
    canvas_h = th + label_h + 2 * margin
    canvas = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    font = get_font(22)

    for i, (label, img, color) in enumerate(imgs):
        x = (i + 1) * margin + i * tw
        y = label_h + margin
        canvas.paste(img, (x, y))
        draw_label(draw, x, 5, label, font, color)

    out = os.path.join(OUTPUT_DIR, f'combined_{sample[:8]}.png')
    canvas.save(out, quality=95)
    print(f'  combined: {out}')


# --- Generate all ---
for sample in samples:
    sid = sample[:8]
    print(f'\nSample {sid}:')
    make_per_sample(sample)
    make_sweep_grid(sample, 4)
    make_sweep_grid(sample, 8)
    make_combined(sample)

print(f'\nDone! All figures in {OUTPUT_DIR}/')
