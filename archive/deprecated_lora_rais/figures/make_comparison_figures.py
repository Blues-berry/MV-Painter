"""Create comparison figures: Input | Zero-shot | LoRA-r4 | LoRA-r8 with metrics."""
import os
from PIL import Image, ImageDraw, ImageFont

RESULTS_DIR = 'comparison_results'
OUTPUT_DIR = 'comparison_figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Get all test samples
samples = set()
for d in os.listdir(RESULTS_DIR):
    for suffix in ['_zeroshot', '_lora_r4', '_lora_r8']:
        if d.endswith(suffix):
            samples.add(d.replace(suffix, ''))
samples = sorted(samples)

# Metrics text
METRICS = {
    'zeroshot': 'Zero-shot\n(Full Fine-tune\nOOM: 30.7GB)',
    'lora_r4': 'LoRA rank=4\n5.81M params (0.23%)\n15.4GB VRAM\n12MB ckpt\nloss=0.000561',
    'lora_r8': 'LoRA rank=8\n11.61M params (0.45%)\n15.4GB VRAM\n23MB ckpt\nloss=0.000466',
}

def get_font(size=20):
    """Get a font, falling back to default."""
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", size)
        except:
            return ImageFont.load_default()

def create_comparison(sample_name):
    """Create a comparison figure for one sample."""
    # Load images
    images = {}
    input_img = None
    for method, label in [('zeroshot', 'Zero-shot'), ('lora_r4', 'LoRA-r4'), ('lora_r8', 'LoRA-r8')]:
        path = os.path.join(RESULTS_DIR, f'{sample_name}_{method}', 'result_6view.png')
        if os.path.exists(path):
            images[method] = Image.open(path).convert('RGB')
        cond_path = os.path.join(RESULTS_DIR, f'{sample_name}_{method}', 'result_cond.png')
        if os.path.exists(cond_path) and input_img is None:
            input_img = Image.open(cond_path).convert('RGB')

    if len(images) < 2:
        print(f'  Skipping {sample_name}: not enough results')
        return

    # Resize all to same height
    target_h = 768  # half of 1536
    target_w = 512  # half of 1024

    for k in images:
        images[k] = images[k].resize((target_w, target_h), Image.LANCZOS)
    if input_img:
        input_img = input_img.resize((target_w, target_h), Image.LANCZOS)

    # Layout: [Input] [Zero-shot] [LoRA-r4] [LoRA-r8]
    # Each column: target_w x target_h
    # Top margin for labels: 80px
    # Left margin for metrics: 0 (metrics go on top of each image)

    n_cols = 1 + len(images) # input + methods
    margin = 10
    label_h = 60
    canvas_w = n_cols * target_w + (n_cols + 1) * margin
    canvas_h = target_h + label_h + 2 * margin

    canvas = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    font_label = get_font(22)
    font_metrics = get_font(14)

    # Place input image
    x = margin
    y = label_h + margin
    if input_img:
        canvas.paste(input_img, (x, y))
        draw.text((x + 5, 5), 'Input', fill=(0, 0, 0), font=font_label)

    # Place method images with metrics
    methods = [
        ('zeroshot', 'Zero-shot', (200, 50, 50)),    # red
        ('lora_r4', 'LoRA-r4', (50, 150, 50)),        # green
        ('lora_r8', 'LoRA-r8', (50, 50, 200)),         # blue
    ]

    for i, (method, label, color) in enumerate(methods):
        if method not in images:
            continue
        x = (i + 1) * margin + (i + 1) * target_w
        y = label_h + margin
        canvas.paste(images[method], (x, y))

        # Label
        draw.text((x + 5, 5), label, fill=color, font=font_label)

        # Metrics overlay (top-left of each image)
        metrics_text = METRICS[method]
        # Draw semi-transparent background
        metrics_lines = metrics_text.split('\n')
        line_h = 18
        box_w = 220
        box_h = len(metrics_lines) * line_h + 10
        overlay = Image.new('RGBA', (box_w, box_h), (0, 0, 0, 160))
        canvas.paste(overlay.convert('RGB'), (x + 5, y + 5), overlay)
        draw = ImageDraw.Draw(canvas)
        for j, line in enumerate(metrics_lines):
            draw.text((x + 10, y + 10 + j * line_h), line, fill=(255, 255, 255), font=font_metrics)

    # Save
    out_path = os.path.join(OUTPUT_DIR, f'comparison_{sample_name[:8]}.png')
    canvas.save(out_path, quality=95)
    print(f'  Saved: {out_path} ({canvas.size})')

# Generate for all samples
print(f'Generating comparison figures for {len(samples)} samples...')
for sample in samples:
    print(f'  {sample[:16]}...')
    create_comparison(sample)

print(f'\nDone! Figures in {OUTPUT_DIR}/')
