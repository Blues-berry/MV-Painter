"""CLIP-IQA evaluation for texture quality assessment.

Uses HuggingFace transformers CLIPModel (openai/clip-vit-base-patch32) features
to compute no-reference image quality scores.
Based on CLIP-IQA (Wang et al., AAAI 2023) methodology:
  - Extract CLIP visual features from generated images
  - Project onto quality-relevant directions (good/bad texture prompts)
  - Higher score = better perceptual quality

Evaluates s=1.25, s=2.50, C3 conditions on 300-object validation set.
Uses pre-generated images (no model inference needed if images exist).

Usage:
    # From pre-generated images:
    python geotex/eval_clipiqa.py \
        --mode from_images \
        --image_dirs mvpoutput/revision_s125:mvpoutput/revision_s250:mvpoutput/revision_c3 \
        --labels "s=1.25:s=2.50:C3 (TCAS)" \
        --output_dir mvpoutput/revision_clipiqa

    # Generate + evaluate (full pipeline):
    python geotex/eval_clipiqa.py \
        --mode generate \
        --config MVPainter/configs/mvpainter-geotex-v2-train.yaml \
        --checkpoint mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt \
        --output_dir mvpoutput/revision_clipiqa \
        --num_objects 300
"""
import os
import sys
import json
import csv
import argparse
import math
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
from torchvision import transforms

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'MVPainter'))
sys.path.insert(0, os.path.dirname(__file__))


# ============================================================
# CLIP-IQA Implementation using open_clip
# ============================================================

class CLIPIQAScorer:
    """No-reference image quality scorer based on CLIP features.

    Uses the difference in CLIP cosine similarity between
    positive (high quality) and negative (low quality) text prompts
    as a perceptual quality indicator.

    This is a simplified version of CLIP-IQA that doesn't require
    fine-tuning — it leverages CLIP's zero-shot capabilities with
    carefully designed prompt pairs.

    Uses HuggingFace transformers CLIPModel (locally cached) to avoid
    network dependencies.
    """

    # Quality prompts designed for texture evaluation
    POSITIVE_PROMPTS = [
        "a photo with rich texture details",
        "a high quality image with fine surface details",
        "sharp and detailed texture",
        "image with clear material and color variations",
        "high resolution photo with visible surface patterns",
    ]

    NEGATIVE_PROMPTS = [
        "a blurry flat image without texture",
        "low quality image with smooth featureless surface",
        "oversmoothed image lacking detail",
        "image with washed out colors and no texture",
        "flat uniform surface without variation",
    ]

    def __init__(self, device='cuda', model_name='openai/clip-vit-base-patch32'):
        from transformers import CLIPModel, CLIPProcessor
        self.device = device
        self.model = CLIPModel.from_pretrained(model_name, local_files_only=True)
        self.processor = CLIPProcessor.from_pretrained(model_name, local_files_only=True)
        self.model = self.model.to(device).eval()

        # Pre-compute text embeddings
        with torch.no_grad():
            pos_inputs = self.processor(text=self.POSITIVE_PROMPTS, return_tensors='pt',
                                        padding=True, truncation=True)
            neg_inputs = self.processor(text=self.NEGATIVE_PROMPTS, return_tensors='pt',
                                        padding=True, truncation=True)
            pos_inputs = {k: v.to(device) for k, v in pos_inputs.items() if k != 'pixel_values'}
            neg_inputs = {k: v.to(device) for k, v in neg_inputs.items() if k != 'pixel_values'}
            self.pos_embeds = self.model.get_text_features(**pos_inputs)
            self.neg_embeds = self.model.get_text_features(**neg_inputs)
            self.pos_embeds = F.normalize(self.pos_embeds, dim=-1)
            self.neg_embeds = F.normalize(self.neg_embeds, dim=-1)
            # Average positive/negative directions
            self.pos_dir = F.normalize(self.pos_embeds.mean(dim=0, keepdim=True), dim=-1)
            self.neg_dir = F.normalize(self.neg_embeds.mean(dim=0, keepdim=True), dim=-1)

        # Pre-compute CLIP normalization tensors (avoid per-call allocation)
        self.clip_mean = torch.tensor(
            [0.48145466, 0.4578275, 0.40821073], device=device
        ).view(1, 3, 1, 1)
        self.clip_std = torch.tensor(
            [0.26862954, 0.26130258, 0.27577711], device=device
        ).view(1, 3, 1, 1)

    @torch.no_grad()
    def score_tensor(self, image_tensor):
        """Score a single image tensor (B, C, H, W) in [0,1] range.

        Returns a quality score per image in the batch.
        Higher = better perceptual texture quality.
        """
        # Resize to CLIP input size
        images = F.interpolate(image_tensor, size=(224, 224), mode='bicubic', align_corners=False)
        # Normalize with CLIP stats
        images = (images - self.clip_mean) / self.clip_std

        # Encode using HF transformers CLIP
        features = self.model.get_image_features(pixel_values=images.to(self.device))
        features = F.normalize(features, dim=-1)

        # Compute quality score: cos(feat, positive) - cos(feat, negative)
        pos_sim = (features @ self.pos_dir.T).squeeze(-1)
        neg_sim = (features @ self.neg_dir.T).squeeze(-1)
        score = (pos_sim - neg_sim + 1.0) / 2.0  # Normalize to [0, 1]
        return score.cpu().numpy()

    @torch.no_grad()
    def score_pil(self, pil_image):
        """Score a PIL image."""
        tensor = transforms.ToTensor()(pil_image).unsqueeze(0).to(self.device)
        return self.score_tensor(tensor)[0]

    @torch.no_grad()
    def score_foreground(self, image_tensor, mask):
        """Score only the foreground region by cropping to FG bounding box.

        This is more relevant for 3D texture evaluation where background
        is uniform white.
        """
        # Crop to foreground bbox with padding
        m = mask[:, :1] if mask.shape[1] > 1 else mask
        fg = m[0, 0] > 0.5
        if fg.sum() < 100:
            return self.score_tensor(image_tensor)

        rows = torch.any(fg, dim=1)
        cols = torch.any(fg, dim=0)
        if not rows.any() or not cols.any():
            return self.score_tensor(image_tensor)

        rmin, rmax = torch.where(rows)[0][[0, -1]]
        cmin, cmax = torch.where(cols)[0][[0, -1]]

        # Add 10% padding
        H, W = fg.shape
        ph = max(int((rmax - rmin).item() * 0.1), 5)
        pw = max(int((cmax - cmin).item() * 0.1), 5)
        rmin = max(0, rmin.item() - ph)
        rmax = min(H - 1, rmax.item() + ph)
        cmin = max(0, cmin.item() - pw)
        cmax = min(W - 1, cmax.item() + pw)

        cropped = image_tensor[:, :, rmin:rmax+1, cmin:cmax+1]
        return self.score_tensor(cropped)


# ============================================================
# Schedule functions (from shared tcas_schedule module)
# ============================================================

from mvpainter.model_unet_geotex import GeoTexResnetWrapper
from tcas_schedule import schedule_c3, schedule_fixed

EVAL_SCHEDULES = {
    's_1.25': lambda p: schedule_fixed(p, 1.25),
    's_2.50': lambda p: schedule_fixed(p, 2.50),
    'C3_TCAS': lambda p: schedule_c3(p, 1.25, 2.50),
}


# ============================================================
# Generation (reuses existing infrastructure)
# ============================================================

def load_model_for_generation(config_path, checkpoint_path, device):
    from omegaconf import OmegaConf
    from src.utils.train_util import instantiate_from_config
    from torchvision.transforms import v2

    config = OmegaConf.load(config_path)
    model = instantiate_from_config(config.model)

    if checkpoint_path and os.path.exists(checkpoint_path):
        state = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
        if 'adapters' in state:
            model.adapters.load_state_dict(state['adapters'])
            model.geo_encoder.load_state_dict(state['geo_encoder'])
        else:
            model.load_geotex_weights(checkpoint_path)

    model.unet.to(device).to(dtype=torch.float16)
    model.pipeline.vae.to(device).to(dtype=torch.float16)
    for name, module in model.unet.named_modules():
        if hasattr(module, 'adapter'):
            module.adapter.to(device).to(dtype=torch.float32)
    model.adapters.to(device).to(dtype=torch.float32)
    model.geo_encoder.to(device).to(dtype=torch.float32)
    model.pipeline.vision_encoder.to('cpu')
    model.pipeline.vision_encoder_2.to('cpu')
    model.pipeline.vae.eval()
    model._device = device

    def encode_condition_image(images):
        dtype = next(model.pipeline.vae.parameters()).dtype
        image_pil = [v2.functional.to_pil_image(images[i]) for i in range(images.shape[0])]
        image_pt = model.pipeline.feature_extractor_vae(images=image_pil, return_tensors='pt').pixel_values
        image_pt = image_pt.to(device=device, dtype=dtype)
        return model.pipeline.vae.encode(image_pt).latent_dist.sample()
    model.encode_condition_image = encode_condition_image
    return model, config


@torch.no_grad()
def generate_with_schedule(model, batch, device, weight_dtype, geo_feats,
                           schedule_fn, num_steps, init_latents):
    """Generate images with an arbitrary temporal schedule."""
    from torchvision.transforms import v2
    from diffusers import EulerDiscreteScheduler
    from metrics import unscale_latents, unscale_image

    cond_imgs = batch['cond_imgs'].to(device)
    cond_imgs = v2.functional.resize(cond_imgs, model.img_size, interpolation=3, antialias=True).clamp(0, 1)
    B = cond_imgs.shape[0]
    global_embeds = batch['global_embeds'].to(device, dtype=weight_dtype).view(B, 1, -1)
    ramp = global_embeds.new_tensor(model.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
    uc_text_emb = model.pipeline.uc_text_emb.to(device, dtype=weight_dtype)
    prompt_embeds = uc_text_emb + global_embeds * ramp
    cond_latents = model.encode_condition_image(cond_imgs).to(weight_dtype)
    added_cond_kwargs = model.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
    added_cond_kwargs = {k: v.to(device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v
                         for k, v in added_cond_kwargs.items()}

    scheduler = EulerDiscreteScheduler.from_config(model.pipeline.scheduler.config)
    scheduler.set_timesteps(num_steps, device=device)
    latents = init_latents * scheduler.init_noise_sigma

    if geo_feats is not None:
        model._set_geo_feats_on_wrappers(geo_feats)

    try:
        for step_idx, t in enumerate(scheduler.timesteps):
            progress = step_idx / max(num_steps - 1, 1)
            scale = schedule_fn(progress)
            for module in model.unet.modules():
                if isinstance(module, GeoTexResnetWrapper):
                    module._adapter_scale = scale

            latent_input = scheduler.scale_model_input(latents, t)
            noise_pred = model.pipeline.unet(
                latent_input, t, encoder_hidden_states=prompt_embeds,
                cross_attention_kwargs=dict(cond_lat=cond_latents),
                added_cond_kwargs=added_cond_kwargs, return_dict=False, is_training=False,
            )[0]
            latents = scheduler.step(noise_pred, t, latents, return_dict=False)[0]
    finally:
        model._clear_geo_feats_on_wrappers()
        for module in model.unet.modules():
            if isinstance(module, GeoTexResnetWrapper):
                if hasattr(module, '_adapter_scale'):
                    delattr(module, '_adapter_scale')

    latents_dec = unscale_latents(latents)
    decoded = model.pipeline.vae.decode(
        latents_dec / model.pipeline.vae.config.scaling_factor, return_dict=False
    )[0]
    image = unscale_image(decoded)
    return (image * 0.5 + 0.5).clamp(0, 1)


# ============================================================
# Main: Generate + Score mode
# ============================================================

def run_generate_and_score(args):
    """Generate images with all schedules and compute CLIP-IQA scores."""
    from data_utils import prepare_batch, collate_batch
    from torchvision.utils import save_image
    import gc

    device = torch.device(args.device)
    weight_dtype = torch.float16
    os.makedirs(args.output_dir, exist_ok=True)

    # Load model
    print("Loading generation model...")
    model, config = load_model_for_generation(args.config, args.checkpoint, device)
    print("Model loaded.")

    # Load CLIP-IQA scorer
    print("Loading CLIP-IQA scorer...")
    scorer = CLIPIQAScorer(device=device)
    print("CLIP-IQA scorer loaded.")

    # Load dataset
    from omegaconf import OmegaConf
    from src.utils.train_util import instantiate_from_config
    dataset = instantiate_from_config(config.data.params.validation)
    num_objects = min(args.num_objects, len(dataset))
    print(f"Dataset: {len(dataset)} objects, evaluating {num_objects}")

    # Results
    all_results = {name: [] for name in EVAL_SCHEDULES}

    print(f"\nRunning CLIP-IQA evaluation on {num_objects} objects")
    print(f"Conditions: {list(EVAL_SCHEDULES.keys())}")
    print("=" * 80)

    for obj_idx in range(num_objects):
        batch = collate_batch(dataset, obj_idx, device)

        cond_imgs, target_imgs, normal_imgs, real_depth_imgs, geo_input, mask = \
            prepare_batch(batch, model.img_size, device)
        geo_input_clean = geo_input.float().clamp(0, 1)
        geo_input_clean = torch.nan_to_num(geo_input_clean, nan=0.0, posinf=1.0, neginf=0.0)
        geo_feats = model.geo_encoder(geo_input_clean)

        torch.manual_seed(42)
        latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
        init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=weight_dtype)

        for sched_name, sched_fn in EVAL_SCHEDULES.items():
            pred = generate_with_schedule(
                model, batch, device, weight_dtype, geo_feats,
                sched_fn, args.num_steps, init_latents.clone()
            )

            # CLIP-IQA score (foreground-focused)
            clip_score = scorer.score_foreground(pred, mask)
            # Also score full image
            clip_score_full = scorer.score_tensor(pred)

            result = {
                'object': f'obj_{obj_idx:04d}',
                'clipiqa_fg': float(clip_score[0]),
                'clipiqa_full': float(clip_score_full[0]),
            }
            all_results[sched_name].append(result)

            # Save images for human study
            if obj_idx < 30:
                img_dir = os.path.join(args.output_dir, 'images', sched_name)
                os.makedirs(img_dir, exist_ok=True)
                save_image(pred, os.path.join(img_dir, f'obj_{obj_idx:04d}.png'))
                if sched_name == list(EVAL_SCHEDULES.keys())[0]:
                    gt_dir = os.path.join(args.output_dir, 'images', 'GT')
                    os.makedirs(gt_dir, exist_ok=True)
                    save_image(target_imgs, os.path.join(gt_dir, f'obj_{obj_idx:04d}.png'))

        # Progress
        if (obj_idx + 1) % 10 == 0:
            c3_scores = [r['clipiqa_fg'] for r in all_results['C3_TCAS']]
            s25_scores = [r['clipiqa_fg'] for r in all_results['s_2.50']]
            print(f"[{obj_idx+1}/{num_objects}] "
                  f"C3 CLIP-IQA={np.mean(c3_scores):.4f} | "
                  f"s=2.50 CLIP-IQA={np.mean(s25_scores):.4f}")

        if (obj_idx + 1) % 50 == 0:
            torch.cuda.empty_cache()
            gc.collect()

    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "=" * 80)
    print("CLIP-IQA EVALUATION SUMMARY")
    print("=" * 80)

    summary = {}
    for sched_name in EVAL_SCHEDULES:
        fg_scores = [r['clipiqa_fg'] for r in all_results[sched_name]]
        full_scores = [r['clipiqa_full'] for r in all_results[sched_name]]
        summary[sched_name] = {
            'mean_fg': np.mean(fg_scores),
            'std_fg': np.std(fg_scores),
            'mean_full': np.mean(full_scores),
            'std_full': np.std(full_scores),
        }
        print(f"  {sched_name:<12}: FG={summary[sched_name]['mean_fg']:.4f} ± "
              f"{summary[sched_name]['std_fg']:.4f}  |  "
              f"Full={summary[sched_name]['mean_full']:.4f} ± "
              f"{summary[sched_name]['std_full']:.4f}")

    # Object-level win rates: C3 vs s=2.50
    c3_scores = [r['clipiqa_fg'] for r in all_results['C3_TCAS']]
    s25_scores = [r['clipiqa_fg'] for r in all_results['s_2.50']]
    wins = sum(1 for c, s in zip(c3_scores, s25_scores) if c > s)
    print(f"\n  C3 vs s=2.50 win rate (CLIP-IQA FG): {wins}/{num_objects} "
          f"({100*wins/num_objects:.1f}%)")

    # Statistical test
    from scipy import stats
    t_stat, p_value = stats.ttest_rel(c3_scores, s25_scores)
    print(f"  Paired t-test: t={t_stat:.3f}, p={p_value:.4f}")

    # ============================================================
    # Save results
    # ============================================================
    output = {
        'num_objects': num_objects,
        'num_steps': args.num_steps,
        'checkpoint': args.checkpoint,
        'summary': summary,
        'c3_vs_s250_win_rate': wins / num_objects,
        'paired_ttest_p': float(p_value),
        'per_object': {name: results for name, results in all_results.items()},
    }
    result_path = os.path.join(args.output_dir, 'clipiqa_results.json')
    with open(result_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {result_path}")

    # CSV for easy import
    csv_path = os.path.join(args.output_dir, 'clipiqa_per_object.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['object', 's_1.25_fg', 's_2.50_fg', 'C3_fg',
                         's_1.25_full', 's_2.50_full', 'C3_full'])
        for i in range(num_objects):
            writer.writerow([
                f'obj_{i:04d}',
                f"{all_results['s_1.25'][i]['clipiqa_fg']:.6f}",
                f"{all_results['s_2.50'][i]['clipiqa_fg']:.6f}",
                f"{all_results['C3_TCAS'][i]['clipiqa_fg']:.6f}",
                f"{all_results['s_1.25'][i]['clipiqa_full']:.6f}",
                f"{all_results['s_2.50'][i]['clipiqa_full']:.6f}",
                f"{all_results['C3_TCAS'][i]['clipiqa_full']:.6f}",
            ])
    print(f"Saved: {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="CLIP-IQA Texture Quality Evaluation")
    parser.add_argument('--mode', choices=['generate', 'from_images'], default='generate')
    parser.add_argument('--config', type=str, default='MVPainter/configs/mvpainter-geotex-v2-train.yaml')
    parser.add_argument('--checkpoint', type=str, default='mvpoutput/geotex_v2/checkpoints/geotex_v2_ema_final.pt')
    parser.add_argument('--output_dir', type=str, default='mvpoutput/revision_clipiqa')
    parser.add_argument('--num_objects', type=int, default=300)
    parser.add_argument('--num_steps', type=int, default=50)
    parser.add_argument('--device', type=str, default='cuda:0')
    # For from_images mode
    parser.add_argument('--image_dirs', type=str, help='Colon-separated image directories')
    parser.add_argument('--labels', type=str, help='Colon-separated labels for each directory')
    args = parser.parse_args()

    if args.mode == 'generate':
        run_generate_and_score(args)
    else:
        raise NotImplementedError("from_images mode not yet implemented")


if __name__ == '__main__':
    main()
