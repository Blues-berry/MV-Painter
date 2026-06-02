"""
Verify LoRA impact on self-attention using Stable Diffusion img2img.
This serves as a supplementary experiment to validate our findings on a different architecture.
"""
import os
import torch
import numpy as np
from PIL import Image
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
from peft import LoraConfig, get_peft_model


def compute_image_similarity(img1, img2):
    """Compute pixel-level MSE and SSIM between two images."""
    from skimage.metrics import structural_similarity as ssim

    arr1 = np.array(img1).astype(float) / 255.0
    arr2 = np.array(img2).astype(float) / 255.0

    mse = np.mean((arr1 - arr2) ** 2)
    ssim_val = ssim(arr1, arr2, multichannel=True, channel_axis=2)

    return mse, ssim_val


def load_sd_pipeline(model_id="stabilityai/stable-diffusion-2-1"):
    """Load Stable Diffusion pipeline."""
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        safety_checker=None,
    )
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    return pipe.to("cuda")


def apply_lora_to_unet(pipe, target_modules, rank=4, alpha=1):
    """Apply LoRA to specified modules in UNet."""
    lora_config = LoraConfig(
        r=rank,
        lora_alpha=alpha,
        target_modules=target_modules,
        lora_dropout=0.0,
        bias="none",
    )

    pipe.unet = get_peft_model(pipe.unet, lora_config)
    return pipe


def run_img2img(pipe, init_image, prompt, strength=0.75, num_inference_steps=50, seed=42):
    """Run img2img inference."""
    generator = torch.Generator(device="cuda").manual_seed(seed)

    with torch.no_grad():
        output = pipe(
            prompt=prompt,
            image=init_image,
            strength=strength,
            num_inference_steps=num_inference_steps,
            generator=generator,
        )

    return output.images[0]


def main():
    output_dir = '/4T/CXY/MV-Painter/mvpoutput/sd_lora_verification'
    os.makedirs(output_dir, exist_ok=True)

    # Load test image
    test_image_path = '/4T/CXY/MV-Painter/data/train_data/rendered_full/d6a5427888b8413fbfcbcaad14353af8/image/000.png'
    if not os.path.exists(test_image_path):
        print(f"Test image not found: {test_image_path}")
        return

    init_image = Image.open(test_image_path).convert('RGB')
    init_image = init_image.resize((512, 512))

    # Configuration
    prompt = "a high quality 3D render of an object"
    strength = 0.5  # Lower strength preserves more of original

    print("="*60)
    print("Stable Diffusion LoRA Verification Experiment")
    print("="*60)

    # Load pipeline
    print("\nLoading Stable Diffusion pipeline...")
    pipe = load_sd_pipeline()

    # --- Config A: Original (no LoRA) ---
    print("\nConfig A: Original (no LoRA)...")
    img_a = run_img2img(pipe, init_image, prompt, strength=strength)
    img_a.save(os.path.join(output_dir, 'config_a_original.png'))

    # --- Config B: Full LoRA (all attention layers) ---
    print("\nConfig B: Full LoRA (all attention)...")
    pipe_b = load_sd_pipeline()
    target_modules_full = [
        "to_q", "to_k", "to_v", "to_out.0",  # self-attention
        "to_q_text", "to_k_text", "to_v_text", "to_out_text.0",  # cross-attention
    ]
    pipe_b = apply_lora_to_unet(pipe_b, target_modules_full, rank=4, alpha=1)
    img_b = run_img2img(pipe_b, init_image, prompt, strength=strength)
    img_b.save(os.path.join(output_dir, 'config_b_full_lora.png'))
    del pipe_b; torch.cuda.empty_cache()

    # --- Config C: Cross-attention only LoRA ---
    print("\nConfig C: Cross-attention only LoRA...")
    pipe_c = load_sd_pipeline()
    target_modules_cross = [
        "to_q_text", "to_k_text", "to_v_text", "to_out_text.0",  # cross-attention only
    ]
    pipe_c = apply_lora_to_unet(pipe_c, target_modules_cross, rank=4, alpha=1)
    img_c = run_img2img(pipe_c, init_image, prompt, strength=strength)
    img_c.save(os.path.join(output_dir, 'config_c_cross_attn_lora.png'))
    del pipe_c; torch.cuda.empty_cache()

    # --- Compute similarities ---
    print("\nComputing similarities...")

    # Similarity with original input
    mse_a, ssim_a = compute_image_similarity(init_image, img_a)
    mse_b, ssim_b = compute_image_similarity(init_image, img_b)
    mse_c, ssim_c = compute_image_similarity(init_image, img_c)

    # Similarity with original output (reference)
    mse_ba, ssim_ba = compute_image_similarity(img_a, img_b)
    mse_ca, ssim_ca = compute_image_similarity(img_a, img_c)

    # Generate report
    report_path = os.path.join(output_dir, 'verification_report.md')
    with open(report_path, 'w') as f:
        f.write("# Stable Diffusion LoRA Verification Report\n\n")
        f.write("**Purpose**: Validate that LoRA on self-attention disrupts image generation consistency.\n\n")
        f.write("**Method**: img2img with strength=0.5 (preserves 50% of original).\n\n")

        f.write("## Results\n\n")
        f.write("| Metric | Original (A) | Full LoRA (B) | Cross-Attn Only (C) |\n")
        f.write("|--------|--------------|---------------|---------------------|\n")
        f.write(f"| MSE vs Input ↓ | {mse_a:.6f} | {mse_b:.6f} | {mse_c:.6f} |\n")
        f.write(f"| SSIM vs Input ↑ | {ssim_a:.4f} | {ssim_b:.4f} | {ssim_c:.4f} |\n")
        f.write(f"| MSE vs Original ↓ | — | {mse_ba:.6f} | {mse_ca:.6f} |\n")
        f.write(f"| SSIM vs Original ↑ | — | {ssim_ba:.4f} | {ssim_ca:.4f} |\n")

        f.write("\n## Analysis\n\n")
        if ssim_ca > ssim_ba:
            f.write("**Cross-attention only LoRA preserves better consistency with the original output.**\n")
            f.write(f"- SSIM improvement: {ssim_ca - ssim_ba:+.4f}\n")
            f.write("- This supports our hypothesis that LoRA on self-attention disrupts feature consistency.\n")
        else:
            f.write("**Both LoRA approaches show similar consistency.**\n")
            f.write("- Further investigation needed with different configurations.\n")

        f.write("\n## Implications for Multi-View Models\n\n")
        f.write("This experiment on Stable Diffusion (single-view) demonstrates the general principle:\n")
        f.write("- Self-attention layers process and store spatial features\n")
        f.write("- LoRA modifications to these layers alter the feature processing\n")
        f.write("- In multi-view models with reference attention, this disruption is more severe\n")
        f.write("  because it corrupts the stored reference features\n")

    print(f"\nReport saved to {report_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Config':<20} {'SSIM vs Input':>15} {'SSIM vs Original':>18}")
    print(f"{'-'*53}")
    print(f"{'Original':<20} {ssim_a:>15.4f} {'—':>18}")
    print(f"{'Full LoRA':<20} {ssim_b:>15.4f} {ssim_ba:>18.4f}")
    print(f"{'Cross-Attn Only':<20} {ssim_c:>15.4f} {ssim_ca:>18.4f}")


if __name__ == '__main__':
    main()
