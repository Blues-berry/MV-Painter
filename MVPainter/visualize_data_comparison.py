"""
Visualize comparison of PBR data from different views.
This script creates comparison images showing cross-view consistency.
"""
import os
import numpy as np
from PIL import Image
import json
import argparse


def create_comparison_grid(images, labels, title, save_path):
    """Create a comparison grid image."""
    n = len(images)
    w, h = images[0].size

    # Add space for labels
    label_height = 30
    title_height = 40
    canvas = Image.new('RGB', (w * n, h + label_height + title_height), (255, 255, 255))

    # Draw title
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font = ImageFont.load_default()
        small_font = font

    draw.text((10, 10), title, fill=(0, 0, 0), font=font)

    # Paste images
    for i, (img, label) in enumerate(zip(images, labels)):
        x = i * w
        y = title_height
        canvas.paste(img, (x, y))
        draw.text((x + 10, y + h + 5), label, fill=(0, 0, 0), font=small_font)

    canvas.save(save_path)
    print(f"Saved: {save_path}")


def compute_cross_view_consistency(img1, img2):
    """Compute cross-view consistency metric (MSE between images)."""
    arr1 = np.array(img1).astype(float) / 255.0
    arr2 = np.array(img2).astype(float) / 255.0
    mse = np.mean((arr1 - arr2) ** 2)
    return mse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", default="/4T/CXY/MV-Painter/data/train_data/rendered_full", help="Data root directory")
    parser.add_argument("--output_dir", default="output/visualization", help="Output directory")
    parser.add_argument("--num_objects", type=int, default=5, help="Number of objects to visualize")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Load test objects
    with open("datalist/mvpainter_pbr_train.json") as f:
        objects = json.load(f)

    # Select test objects (last N, not in training)
    test_objects = objects[-args.num_objects:]

    print(f"Visualizing {len(test_objects)} objects...")

    consistency_metrics = []

    for dtype, uid in test_objects:
        obj_dir = os.path.join(args.data_root, uid)
        image_dir = os.path.join(obj_dir, "image")
        basecolor_dir = os.path.join(obj_dir, "basecolor")
        metallic_dir = os.path.join(obj_dir, "metallic")
        roughness_dir = os.path.join(obj_dir, "roughness")

        if not os.path.exists(image_dir):
            print(f"Skipping {uid}: no image directory")
            continue

        # Load views
        views_to_show = [0, 1, 2, 3, 4, 5]  # First 6 views
        images = []
        labels = []

        for view_idx in views_to_show:
            img_path = os.path.join(image_dir, f"{view_idx:03d}.png")
            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGB").resize((256, 256))
                images.append(img)
                labels.append(f"View {view_idx}")

        if len(images) < 2:
            print(f"Skipping {uid}: not enough views")
            continue

        # Compute cross-view consistency
        for i in range(len(images) - 1):
            mse = compute_cross_view_consistency(images[i], images[i + 1])
            consistency_metrics.append({
                'object': uid,
                'view_pair': f"{i}-{i+1}",
                'mse': mse
            })

        # Create comparison grid
        save_path = os.path.join(args.output_dir, f"{uid}_views.png")
        create_comparison_grid(images, labels, f"Object: {uid[:8]}...", save_path)

        # Load and show PBR maps if available
        if os.path.exists(basecolor_dir):
            pbr_images = []
            pbr_labels = []

            for view_idx in [0, 1, 2]:
                # Original image
                img_path = os.path.join(image_dir, f"{view_idx:03d}.png")
                if os.path.exists(img_path):
                    pbr_images.append(Image.open(img_path).convert("RGB").resize((256, 256)))
                    pbr_labels.append(f"View {view_idx}")

                # Basecolor
                bc_path = os.path.join(basecolor_dir, f"{view_idx:03d}.png")
                if os.path.exists(bc_path):
                    pbr_images.append(Image.open(bc_path).convert("RGB").resize((256, 256)))
                    pbr_labels.append(f"Basecolor {view_idx}")

                # Metallic
                mtl_path = os.path.join(metallic_dir, f"{view_idx:03d}.png")
                if os.path.exists(mtl_path):
                    pbr_images.append(Image.open(mtl_path).convert("RGB").resize((256, 256)))
                    pbr_labels.append(f"Metallic {view_idx}")

            if pbr_images:
                save_path = os.path.join(args.output_dir, f"{uid}_pbr.png")
                create_comparison_grid(pbr_images[:9], pbr_labels[:9], f"PBR Maps: {uid[:8]}...", save_path)

    # Print consistency metrics
    if consistency_metrics:
        print("\n=== Cross-View Consistency Metrics ===")
        mse_values = [m['mse'] for m in consistency_metrics]
        print(f"Mean MSE: {np.mean(mse_values):.4f}")
        print(f"Std MSE: {np.std(mse_values):.4f}")
        print(f"Min MSE: {np.min(mse_values):.4f}")
        print(f"Max MSE: {np.max(mse_values):.4f}")

        # Save metrics
        import csv
        metrics_path = os.path.join(args.output_dir, "consistency_metrics.csv")
        with open(metrics_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['object', 'view_pair', 'mse'])
            writer.writeheader()
            writer.writerows(consistency_metrics)
        print(f"\nMetrics saved to {metrics_path}")

    print(f"\nVisualization complete! Results saved to {args.output_dir}")


if __name__ == "__main__":
    main()
