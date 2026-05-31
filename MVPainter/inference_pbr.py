"""
PBR Inference Script - Compare Baseline vs Ours checkpoints
"""
import os
import argparse
import torch
import numpy as np
from PIL import Image
from tqdm import tqdm
from omegaconf import OmegaConf
from accelerate import Accelerator
from torchvision.utils import make_grid, save_image

from pbr.models.unet_dr2d_condition import UNetDR2DConditionModel
from pbr.pipelines.pipeline_idarbdiffusion import IDArbDiffusionPipeline
from pbr.data.mv_dataset_arbobjaverse import MVDataset
from pbr.utils.config import load_config


def load_pipeline(cfg, checkpoint_path, device='cuda'):
    """Load pipeline from checkpoint."""
    print(f"Loading pipeline from {checkpoint_path}...")

    # Load base components
    from transformers import CLIPTextModel, CLIPTokenizer, CLIPImageProcessor
    from diffusers import AutoencoderKL, DDIMScheduler

    text_encoder = CLIPTextModel.from_pretrained(cfg.pretrained_model_name_or_path, subfolder="text_encoder")
    tokenizer = CLIPTokenizer.from_pretrained(cfg.pretrained_model_name_or_path, subfolder="tokenizer")
    feature_extractor = CLIPImageProcessor.from_pretrained(cfg.pretrained_model_name_or_path, subfolder="feature_extractor")
    vae = AutoencoderKL.from_pretrained(cfg.pretrained_model_name_or_path, subfolder="vae")

    # Load UNet from checkpoint
    unet = UNetDR2DConditionModel.from_pretrained(checkpoint_path)

    # Load scheduler
    scheduler = DDIMScheduler.from_pretrained(cfg.pretrained_model_name_or_path, subfolder="scheduler")

    # Create pipeline
    pipeline = IDArbDiffusionPipeline(
        text_encoder=text_encoder,
        tokenizer=tokenizer,
        feature_extractor=feature_extractor,
        vae=vae,
        unet=unet,
        safety_checker=None,
        scheduler=scheduler,
        **cfg.pipe_kwargs
    )

    pipeline.to(device)
    pipeline.set_progress_bar_config(disable=False)

    return pipeline


def run_inference(pipeline, dataloader, cfg, output_dir, device='cuda'):
    """Run inference on a dataloader."""
    os.makedirs(output_dir, exist_ok=True)

    generator = torch.Generator(device=device).manual_seed(cfg.seed) if cfg.seed else None

    for i, batch in tqdm(enumerate(dataloader), desc="Inference"):
        imgs_in = batch['imgs_in'].to(device).float()
        imgs_out = batch['imgs_out'].to(device).float()
        task_ids = batch['task_ids'].to(device)
        cam_pose = batch['pose'].to(device).float()

        B, Nv, Nd = imgs_out.shape[:3]

        # Flatten for pipeline
        imgs_in_flat = imgs_in.flatten(0, 1)
        task_ids_flat = task_ids.flatten(0, 2)

        with torch.autocast("cuda"):
            out = pipeline(
                imgs_in_flat,
                task_ids_flat,
                num_views=Nv,
                cam_pose=cam_pose,
                generator=generator,
                guidance_scale=1.0,
                output_type='pt',
                num_images_per_prompt=1,
                **cfg.pipe_validation_kwargs,
            ).images

        # Save results
        for b in range(B):
            obj_dir = os.path.join(output_dir, f"object_{i*B+b}")
            os.makedirs(obj_dir, exist_ok=True)

            # Save input images
            for v in range(Nv):
                img = imgs_in[b, v].cpu()
                save_image(img, os.path.join(obj_dir, f"input_view_{v}.png"))

            # Save predicted PBR maps
            # out shape: (B*Nv*Nd, 3, H, W) where Nd=3 (albedo, normal, material)
            for v in range(Nv):
                for d, dname in enumerate(['albedo', 'normal', 'material']):
                    idx = b * Nv * Nd + v * Nd + d
                    if idx < out.shape[0]:
                        save_image(out[idx].cpu(), os.path.join(obj_dir, f"pred_view{v}_{dname}.png"))

            # Save ground truth
            for v in range(Nv):
                for d, dname in enumerate(['albedo', 'normal', 'material']):
                    gt = imgs_out[b, v, d].cpu()
                    save_image(gt, os.path.join(obj_dir, f"gt_view{v}_{dname}.png"))

    print(f"Results saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True, help='Config file path')
    parser.add_argument('--checkpoint', type=str, required=True, help='Checkpoint path')
    parser.add_argument('--output_dir', type=str, default='PBR/results/', help='Output directory')
    parser.add_argument('--split', type=str, default='test', help='Dataset split')
    parser.add_argument('--num_samples', type=int, default=5, help='Number of samples to visualize')
    args = parser.parse_args()

    cfg = load_config(args.config)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load pipeline
    pipeline = load_pipeline(cfg, args.checkpoint, device)

    # Create dataset
    dataset = MVDataset(
        img_wh=cfg.validation_dataset.get('img_wh', [512, 512]),
        object_list=cfg.validation_dataset['object_list'],
        data_root=cfg.dataset_root,
        split=args.split,
        num_views=cfg.validation_dataset.get('num_views', 4),
        num_samples=args.num_samples
    )
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False)

    # Run inference
    run_inference(pipeline, dataloader, cfg, args.output_dir, device)


if __name__ == '__main__':
    main()
