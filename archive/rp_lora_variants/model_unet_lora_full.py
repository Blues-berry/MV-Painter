"""
Full LoRA training model - applies LoRA to both attn1 and attn2.
Uses the same LoRA implementation as attn2-only for compatibility.
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

from .mvpainter_pipeline import RefOnlyNoisedUNet, MVPainter_Pipeline, ReferenceOnlyAttnProc
from .lora_utils import LoRAAttnProcessor2_0, save_lora_weights


def create_lora_processors_full(
    unet,
    rank: int = 8,
    network_alpha=None,
):
    """Create LoRA processors for ALL attention layers (attn1 + attn2)."""
    processors = {}
    for name, _ in unet.attn_processors.items():
        attn_name = name.replace('.processor', '')
        attn_module = dict(unet.named_modules())[attn_name]
        hidden_size = attn_module.to_q.in_features
        cross_attn_dim = attn_module.to_k.in_features if 'attn2' in name else None

        lora_proc = LoRAAttnProcessor2_0(
            hidden_size=hidden_size,
            cross_attention_dim=cross_attn_dim,
            rank=rank,
            network_alpha=network_alpha,
        )
        processors[name] = ReferenceOnlyAttnProc(
            lora_proc,
            enabled=name.endswith("attn1.processor"),
            name=name,
        )
    return processors


def scale_latents(latents):
    return (latents - 0.22) * 0.75


def unscale_latents(latents):
    return latents / 0.75 + 0.22


def scale_image(image):
    return image * 0.5 / 0.8


def unscale_image(image):
    return image / 0.5 * 0.8


class LoRACheckpointCallbackFull(pl.Callback):
    """Saves full LoRA weights (attn1 + attn2)."""

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
            save_lora_weights(processors, save_path, self.rank, self.alpha)


class MVDiffusionLoRAFull(pl.LightningModule):
    """Full LoRA training - applies LoRA to both attn1 and attn2."""

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

        # Load pipeline
        print("stable_diffusion_config:", stable_diffusion_config, self.device)
        pipeline = MVPainter_Pipeline.from_pretrained(
            stable_diffusion_config['pretrained_model_name_or_path'],
            use_safetensors=True,
        ).to(self.device)
        pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
            pipeline.scheduler.config, timestep_spacing='trailing',
        )
        self.pipeline = pipeline

        # Set up full LoRA processors (attn1 + attn2)
        lora_processors = create_lora_processors_full(
            pipeline.unet, rank=lora_rank, network_alpha=lora_alpha,
        )
        pipeline.unet.set_attn_processor(lora_processors)

        # Wrap in RefOnlyNoisedUNet without replacing processors
        train_sched = DDPMScheduler.from_config(pipeline.scheduler.config)
        if isinstance(pipeline.unet, UNet2DConditionModel) or True:
            pipeline.unet = RefOnlyNoisedUNet(
                pipeline.unet, train_sched, pipeline.scheduler, replace_processors=False,
            )

        self.train_scheduler = train_sched
        self.unet = pipeline.unet

        # Count LoRA params
        lora_params = sum(
            p.numel() for n, p in self.unet.named_parameters()
            if any(kw in n for kw in ['to_q_lora', 'to_k_lora', 'to_v_lora', 'to_out_lora'])
        )
        total_params = sum(p.numel() for p in self.unet.parameters())
        print(f"Full LoRA parameters: {lora_params / 1e6:.2f}M / {total_params / 1e6:.2f}M total ({100 * lora_params / total_params:.2f}%)")

        self.validation_step_outputs = []

    def register_schedule(self):
        self.num_timesteps = 1000
        beta_start = 0.00085
        beta_end = 0.0120
        betas = torch.linspace(beta_start, beta_end, 1000, dtype=torch.float32)

        alphas = 1. - betas
        alphas_cumprod = torch.cumprod(alphas, dim=0)
        alphas_cumprod_prev = torch.cat([torch.ones(1, dtype=torch.float64), alphas_cumprod[:-1]], 0)

        self.register_buffer('betas', betas.float())
        self.register_buffer('alphas_cumprod', alphas_cumprod.float())
        self.register_buffer('alphas_cumprod_prev', alphas_cumprod_prev.float())

        self.register_buffer('sqrt_alphas_cumprod', torch.sqrt(alphas_cumprod).float())
        self.register_buffer('sqrt_one_minus_alphas_cumprod', torch.sqrt(1 - alphas_cumprod).float())

        self.register_buffer('sqrt_recip_alphas_cumprod', torch.sqrt(1. / alphas_cumprod).float())
        self.register_buffer('sqrt_recipm1_alphas_cumprod', torch.sqrt(1. / alphas_cumprod - 1).float())

    def on_fit_start(self):
        device = torch.device(f'cuda:{self.global_rank}')
        print(device, self.device)
        self.pipeline.to('cpu')
        self.unet.to(device)
        self.pipeline.vae.to(device)
        self.pipeline.vision_encoder.to('cpu')
        self.pipeline.vision_encoder_2.to('cpu')

        if self.global_rank == 0:
            os.makedirs(os.path.join(self.logdir, 'images'), exist_ok=True)
            os.makedirs(os.path.join(self.logdir, 'images_val'), exist_ok=True)

    def prepare_batch_data(self, batch):
        cond_imgs = batch['cond_imgs']
        cond_imgs = cond_imgs.to(self.device)
        cond_imgs = v2.functional.resize(cond_imgs, self.img_size, interpolation=3, antialias=True).clamp(0, 1)

        target_imgs = batch['target_imgs']
        target_imgs = v2.functional.resize(target_imgs, self.img_size, interpolation=3, antialias=True).clamp(0, 1)
        target_imgs = rearrange(target_imgs, 'b (x y) c h w -> b c (x h) (y w)', x=3, y=2)
        target_imgs = target_imgs.to(self.device)

        depth_imgs = batch['depth_imgs']
        depth_imgs = v2.functional.resize(depth_imgs, self.img_size, interpolation=3, antialias=True).clamp(0, 1)
        depth_imgs = rearrange(depth_imgs, 'b (x y) c h w -> b c (x h) (y w)', x=3, y=2)
        depth_imgs = depth_imgs.to(self.device)

        real_depth_imgs = batch['real_depth_imgs']
        real_depth_imgs = v2.functional.resize(real_depth_imgs, self.img_size, interpolation=3, antialias=True).clamp(0, 1)
        real_depth_imgs = rearrange(real_depth_imgs, 'b (x y) c h w -> b c (x h) (y w)', x=3, y=2)
        real_depth_imgs = real_depth_imgs.to(self.device)

        return cond_imgs, target_imgs, depth_imgs, real_depth_imgs

    @torch.no_grad()
    def encode_condition_image(self, images):
        dtype = next(self.pipeline.vae.parameters()).dtype
        image_pil = [v2.functional.to_pil_image(images[i]) for i in range(images.shape[0])]
        image_pt = self.pipeline.feature_extractor_vae(images=image_pil, return_tensors="pt").pixel_values
        image_pt = image_pt.to(device=self.device, dtype=dtype)
        latents = self.pipeline.vae.encode(image_pt).latent_dist.sample()
        return latents

    @torch.no_grad()
    def encode_target_images(self, images):
        dtype = next(self.pipeline.vae.parameters()).dtype
        images = (images - 0.5) / 0.8
        posterior = self.pipeline.vae.encode(images.to(dtype)).latent_dist
        latents = posterior.sample() * self.pipeline.vae.config.scaling_factor
        latents = scale_latents(latents)
        return latents

    def forward_unet(self, latents, t, prompt_embeds, cond_latents, depth_imgs, added_cond_kwargs, is_training, depth_imgs_2=None):
        dtype = next(self.pipeline.unet.parameters()).dtype
        latents = latents.to(dtype)
        prompt_embeds = prompt_embeds.to(dtype)
        cond_latents = cond_latents.to(dtype)
        cross_attention_kwargs = dict(cond_lat=cond_latents)

        pred_noise = self.pipeline.unet(
            latents,
            t,
            encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=cross_attention_kwargs,
            added_cond_kwargs=added_cond_kwargs,
            return_dict=False,
            is_training=is_training,
        )[0]
        return pred_noise

    def training_step(self, batch, batch_idx):
        cond_imgs, target_imgs, _, _ = self.prepare_batch_data(batch)

        B = cond_imgs.shape[0]
        t = torch.randint(0, self.num_timesteps, size=(B,)).long().to(self.device)

        with torch.no_grad():
            weight_dtype = torch.float16

            if np.random.rand() > self.drop_cond_prob:
                if 'global_embeds' in batch:
                    global_embeds = batch['global_embeds'].to(self.device, dtype=weight_dtype)
                    global_embeds = global_embeds.view(B, 1, -1)
                    ramp = global_embeds.new_tensor(self.pipeline.config.ramping_coefficients).unsqueeze(-1).to(weight_dtype)
                    uc_text_emb = self.pipeline.uc_text_emb.to(self.device, dtype=weight_dtype)
                    prompt_embeds = uc_text_emb + global_embeds * ramp
                else:
                    prompt_embeds = self.pipeline.get_prompt_embeds_train(cond_image=cond_imgs, is_drop=False)
                cond_latents = self.encode_condition_image(cond_imgs).to(weight_dtype)
                added_cond_kwargs = self.pipeline.get_added_cond_kwargs_train(B, is_drop=False)
                added_cond_kwargs = {k: v.to(self.device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v for k, v in added_cond_kwargs.items()}
            else:
                if 'global_embeds' in batch:
                    prompt_embeds = torch.zeros((B, 77, 2048), device=self.device, dtype=weight_dtype)
                else:
                    prompt_embeds = self.pipeline.get_prompt_embeds_train(cond_image=cond_imgs, is_drop=True)
                cond_latents = self.encode_condition_image(torch.zeros_like(cond_imgs)).to(weight_dtype)
                added_cond_kwargs = self.pipeline.get_added_cond_kwargs_train(B, is_drop=True)
                added_cond_kwargs = {k: v.to(self.device, dtype=weight_dtype) if isinstance(v, torch.Tensor) else v for k, v in added_cond_kwargs.items()}

        latents = self.encode_target_images(target_imgs).to(weight_dtype)

        noise = torch.randn_like(latents)
        latents_noisy = self.train_scheduler.add_noise(latents, noise, t)

        noise_pred = self.forward_unet(
            latents_noisy, t, prompt_embeds, cond_latents,
            depth_imgs=None,
            added_cond_kwargs=added_cond_kwargs, is_training=True,
        )

        loss, loss_dict = self.compute_loss(noise_pred, noise)
        self.log_dict(loss_dict, prog_bar=True, logger=True, on_step=True, on_epoch=True)
        self.log("global_step", self.global_step, prog_bar=True, logger=True, on_step=True, on_epoch=False)
        lr = self.optimizers().param_groups[0]['lr']
        self.log('lr_abs', lr, prog_bar=True, logger=True, on_step=True, on_epoch=False)

        return loss

    def on_after_backward(self):
        valid_gradients = True
        for name, param in self.named_parameters():
            if param.grad is not None:
                valid_gradients = not (torch.isnan(param.grad).any() or torch.isinf(param.grad).any())
                if not valid_gradients:
                    break
        if not valid_gradients:
            print('!!!!!! detected inf or nan values in gradients. not updating model parameters !!!!!!!')
            self.zero_grad()
        return super().on_after_backward()

    def compute_loss(self, noise_pred, noise_gt):
        loss = F.mse_loss(noise_pred, noise_gt)
        loss_dict = {'train/loss': loss}
        return loss, loss_dict

    @torch.no_grad()
    def validation_step(self, batch, batch_idx):
        cond_imgs, target_imgs, depth_image, _ = self.prepare_batch_data(batch)
        images_pil = [v2.functional.to_pil_image(cond_imgs[i]) for i in range(cond_imgs.shape[0])]

        outputs = []
        for cond_img in images_pil:
            latent = self.pipeline(cond_img, depth_image=depth_image, num_inference_steps=75, output_type='latent').images
            image = unscale_image(self.pipeline.vae.decode(latent / self.pipeline.vae.config.scaling_factor, return_dict=False)[0])
            image = (image * 0.5 + 0.5).clamp(0, 1)
            outputs.append(image)
        outputs = torch.cat(outputs, dim=0).to(self.device)
        images = torch.cat([target_imgs, outputs], dim=-2)
        self.validation_step_outputs.append(images)

    @torch.no_grad()
    def on_validation_epoch_end(self):
        images = torch.cat(self.validation_step_outputs, dim=0)
        all_images = self.all_gather(images)
        all_images = rearrange(all_images, 'r b c h w -> (r b) c h w')

        if self.global_rank == 0:
            grid = make_grid(all_images, nrow=8, normalize=True, value_range=(0, 1))
            save_image(grid, os.path.join(self.logdir, 'images_val', f'val_{self.global_step:07d}.png'))

        self.validation_step_outputs.clear()

    def configure_optimizers(self):
        lr = getattr(self, 'learning_rate', None) or self._lr or 5e-4

        # Freeze everything
        self.unet.requires_grad_(False)

        # Unfreeze only LoRA parameters
        lora_keywords = ['to_q_lora', 'to_k_lora', 'to_v_lora', 'to_out_lora']
        trainable_params = []
        for name, param in self.unet.named_parameters():
            if any(kw in name for kw in lora_keywords):
                param.requires_grad = True
                trainable_params.append(param)

        print(f"Full LoRA trainable parameters: {sum(p.numel() for p in trainable_params) / 1e6:.2f}M")

        # Prefer DeepSpeed CPUAdam when available (required for ZeRO-3 offload),
        # then bitsandbytes 8-bit Adam, then standard AdamW.
        try:
            from deepspeed.ops.adam import DeepSpeedCPUAdam
            optimizer = DeepSpeedCPUAdam(trainable_params, lr=lr)
            print("Using DeepSpeed CPUAdam optimizer")
        except ImportError:
            try:
                import bitsandbytes as bnb
                optimizer = bnb.optim.AdamW8bit(trainable_params, lr=lr)
                print("Using 8-bit AdamW optimizer")
            except ImportError:
                optimizer = torch.optim.AdamW(trainable_params, lr=lr)
                print("Using standard AdamW optimizer")

        scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, 3000, eta_min=lr / 4)
        return {'optimizer': optimizer, 'lr_scheduler': scheduler}
