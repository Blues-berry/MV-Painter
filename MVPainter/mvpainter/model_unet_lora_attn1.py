"""
LoRA training model with attn1-only support.
Applies LoRA ONLY to attn1 (self-attention) for ablation study.
attn2 (cross-attention) keeps original processors.

This is the REVERSE of attn2-only: used to prove that attn1 LoRA is what breaks reference attention.
"""
import os
import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
from torchvision.transforms import v2
from torchvision.utils import make_grid, save_image
from einops import rearrange

from diffusers import EulerAncestralDiscreteScheduler, DDPMScheduler, UNet2DConditionModel

from .mvpainter_pipeline import RefOnlyNoisedUNet, MVPainter_Pipeline
from .lora_utils_attn1 import (
    create_lora_processors_attn1_only,
    save_lora_weights_attn1_only,
)


def scale_latents(latents):
    return (latents - 0.22) * 0.75


def unscale_latents(latents):
    return latents / 0.75 + 0.22


def scale_image(image):
    return image * 0.5 / 0.8


def unscale_image(image):
    return image / 0.5 * 0.8


class LoRACheckpointCallbackAttn1(pl.Callback):
    """Saves attn1-only LoRA weights."""

    def __init__(self, save_dir='', every_n_steps=1000, rank=8, alpha=8):
        super().__init__()
        self.save_dir = save_dir
        self.every_n_steps = every_n_steps
        self.rank = rank
        self.alpha = alpha

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        if (trainer.global_step + 1) % self.every_n_steps == 0 and trainer.global_rank == 0:
            save_dir = self.save_dir or os.path.join(trainer.logdir, 'lora_checkpoints')
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, f'lora_step_{trainer.global_step + 1:07d}.safetensors')
            processors = pl_module.unet.attn_processors
            save_lora_weights_attn1_only(processors, save_path, self.rank, self.alpha)


class MVDiffusionLoRAAttn1(pl.LightningModule):
    """LoRA training with attn1-only for ablation study."""

    def __init__(
        self,
        stable_diffusion_config,
        drop_cond_prob=0.1,
        lora_rank=4,
        lora_alpha=4,
    ):
        super().__init__()

        self.drop_cond_prob = drop_cond_prob
        self.lora_rank = lora_rank
        self.lora_alpha = lora_alpha
        self.img_size = 256
        self._lr = None

        self.register_schedule()

        self.pipeline = MVPainter_Pipeline.from_pretrained(
            stable_diffusion_config['pretrained_model_name_or_path'],
            torch_dtype=torch.float32,
        )
        self.pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
            self.pipeline.scheduler.config, timestep_spacing='trailing',
        )

        self.unet = RefOnlyNoisedUNet(self.pipeline.unet, self.noise_scheduler)

        # Apply attn1-only LoRA
        processors = create_lora_processors_attn1_only(
            self.unet.unet, rank=lora_rank, network_alpha=lora_alpha,
        )
        self.unet.unet.set_attn_processor(processors)

        self.vae = self.pipeline.vae
        self.text_encoder = self.pipeline.text_encoder
        self.image_encoder = self.pipeline.image_encoder

        self.freeze_pretrained()

    def register_schedule(self):
        self.noise_scheduler = DDPMScheduler(
            beta_start=0.00085, beta_end=0.012,
            beta_schedule='scaled_linear',
            num_train_timesteps=1000,
            prediction_type='epsilon',
        )

    def freeze_pretrained(self):
        self.vae.requires_grad_(False)
        self.text_encoder.requires_grad_(False)
        self.image_encoder.requires_grad_(False)
        self.unet.unet.requires_grad_(False)

        # Unfreeze only attn1 LoRA parameters
        for name, param in self.unet.named_parameters():
            if 'attn1' in name and 'lora' in name:
                param.requires_grad = True

    @property
    def lr(self):
        return self._lr

    @lr.setter
    def lr(self, val):
        self._lr = val

    def configure_optimizers(self):
        params = [p for p in self.unet.parameters() if p.requires_grad]
        optimizer = torch.optim.AdamW(params, lr=self._lr, weight_decay=0.01)
        return optimizer

    def training_step(self, batch, batch_idx):
        # Same training logic as model_unet_lora_attn2.py
        images = batch['image']
        cond_images = batch['cond_image']
        depths = batch.get('depth', None)

        with torch.no_grad():
            latents = self.vae.encode(images).latent_dist.sample() * 0.18215
            cond_latents = self.vae.encode(cond_images).latent_dist.sample() * 0.18215

        noise = torch.randn_like(latents)
        timesteps = torch.randint(0, 1000, (latents.shape[0],), device=latents.device)
        noisy_latents = self.noise_scheduler.add_noise(latents, noise, timesteps)

        # Get text/image embeddings
        with torch.no_grad():
            encoder_hidden_states = self.text_encoder(
                batch.get('text_input_ids', torch.zeros(latents.shape[0], 77, dtype=torch.long, device=latents.device))
            )[0]

        # Predict noise
        noise_pred = self.unet(
            noisy_latents,
            timesteps,
            encoder_hidden_states=encoder_hidden_states,
            cross_attention_kwargs={'cond_lat': cond_latents},
            is_training=True,
        ).sample

        loss = F.mse_loss(noise_pred, noise)
        self.log('train_loss', loss, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        pass
