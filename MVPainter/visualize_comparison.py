"""
Visualize comparison between baseline and Ours (MV Consistency) PBR generation.
"""
import os
import torch
import numpy as np
from PIL import Image
from tqdm import tqdm
import json

def load_model(pretrained_path, checkpoint_path=None):
    """Load PBR model with optional fine-tuned checkpoint."""
    from diffusers import AutoencoderKL, UNet2DConditionModel
    from transformers import CLIPTextModel, CLIPTokenizer, CLIPImageProcessor
    from pbr.models.unet_dr2d_condition import UNetDR2DConditionModel
    from pbr.pipelines.pipeline_idarbdiffusion import IDArbDiffusionPipeline

    # Load pipeline components
    vae = AutoencoderKL.from_pretrained(pretrained_path, subfolder="vae")
    tokenizer = CLIPTokenizer.from_pretrained(pretrained_path, subfolder="tokenizer")
    text_encoder = CLIPTextModel.from_pretrained(pretrained_path, subfolder="text_encoder")
    feature_extractor = CLIPImageProcessor.from_pretrained(pretrained_path, subfolder="feature_extractor")

    # Load UNet
    unet = UNetDR2DConditionModel.from_pretrained(pretrained_path, subfolder="unet")

    # Load fine-tuned weights if provided
    if checkpoint_path and os.path.exists(checkpoint_path):
        print(f"Loading checkpoint from {checkpoint_path}")
        from safetensors.torch import load_file
        state_dict = load_file(os.path.join(checkpoint_path, "diffusion_pytorch_model.safetensors"))
        unet.load_state_dict(state_dict, strict=False)

    # Create pipeline
    pipeline = IDArbDiffusionPipeline(
        vae=vae,
        text_encoder=text_encoder,
        tokenizer=tokenizer,
        unet=unet,
        scheduler=None,
        safety_checker=None,
        feature_extractor=feature_extractor,
    )

    return pipeline


def generate_pbr(pipeline, input_image, device="cuda"):
    """Generate PBR maps from input image."""
    from torchvision import transforms

    # Prepare input
    transform = transforms.Compose([
        transforms.Resize((512, 512)),
        transforms.ToTensor(),
    ])
    img_tensor = transform(input_image).unsqueeze(0).to(device)

    # Generate PBR
    with torch.no_grad():
        output = pipeline(
            img_tensor,
            num_inference_steps=50,
            guidance_scale=7.5,
        ).images

    return output


def create_comparison_grid(images_list, titles, save_path):
    """Create a comparison grid image."""
    n_rows = len(images_list)
    n_cols = len(images_list[0])

    # Get image size
    w, h = images_list[0][0].size

    # Create canvas
    canvas = Image.new('RGB', (w * n_cols, h * n_rows))

    for i, (images, title) in enumerate(zip(images_list, titles)):
        for j, img in enumerate(images):
            canvas.paste(img, (j * w, i * h))

    canvas.save(save_path)
    print(f"Saved comparison to {save_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretrained", default="lizb6626/IDArb", help="Pretrained model path")
    parser.add_argument("--baseline_ckpt", default=None, help="Baseline checkpoint path")
    parser.add_argument("--ours_ckpt", default="output/pbr-mvpainter-mv-consistency/checkpoint-10000/unet", help="Ours checkpoint path")
    parser.add_argument("--data_root", default="/4T/CXY/MV-Painter/data/train_data/rendered_full", help="Data root directory")
    parser.add_argument("--output_dir", default="output/visualization", help="Output directory")
    parser.add_argument("--num_objects", type=int, default=5, help="Number of objects to visualize")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load models
    print("Loading baseline model...")
    baseline_pipeline = load_model(args.pretrained, args.baseline_ckpt)
    baseline_pipeline = baseline_pipeline.to(device)

    print("Loading Ours model...")
    ours_pipeline = load_model(args.pretrained, args.ours_ckpt)
    ours_pipeline = ours_pipeline.to(device)

    # Load test objects
    with open("datalist/mvpainter_pbr_train.json") as f:
        objects = json.load(f)

    # Select test objects
    test_objects = objects[-args.num_objects:]  # Use last N objects (not in training)

    print(f"Generating PBR for {len(test_objects)} objects...")

    for dtype, uid in tqdm(test_objects):
        obj_dir = os.path.join(args.data_root, uid)

        # Load input image (view 0)
        input_path = os.path.join(obj_dir, "image", "000.png")
        if not os.path.exists(input_path):
            print(f"Skipping {uid}: no input image")
            continue

        input_image = Image.open(input_path).convert("RGB")

        # Generate PBR with baseline
        print(f"  Generating baseline for {uid}...")
        baseline_output = generate_pbr(baseline_pipeline, input_image, device)

        # Generate PBR with Ours
        print(f"  Generating Ours for {uid}...")
        ours_output = generate_pbr(ours_pipeline, input_image, device)

        # Load ground truth views
        gt_views = []
        for view_idx in [0, 1, 2]:
            gt_path = os.path.join(obj_dir, "image", f"{view_idx:03d}.png")
            if os.path.exists(gt_path):
                gt_views.append(Image.open(gt_path).convert("RGB"))
            else:
                gt_views.append(Image.new("RGB", (512, 512)))

        # Create comparison
        comparison = [
            [input_image] + gt_views[:2],  # Input + GT views
            baseline_output[:3] if len(baseline_output) >= 3 else baseline_output + [Image.new("RGB", (512, 512))] * (3 - len(baseline_output)),
            ours_output[:3] if len(ours_output) >= 3 else ours_output + [Image.new("RGB", (512, 512))] * (3 - len(ours_output)),
        ]
        titles = ["Input + GT", "Baseline", "Ours"]

        save_path = os.path.join(args.output_dir, f"{uid}_comparison.png")
        create_comparison_grid(comparison, titles, save_path)

    print(f"\nVisualization complete! Results saved to {args.output_dir}")


if __name__ == "__main__":
    main()
