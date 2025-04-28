import argparse
import logging
import math
import json
import os
import shutil
import time
from omegaconf import OmegaConf
from packaging import version
from collections import defaultdict

import numpy as np
import torch
import torch.utils.checkpoint
import torch.nn.functional as F
from torchvision.utils import make_grid, save_image
from einops import rearrange
from tqdm.auto import tqdm

import accelerate
from accelerate import Accelerator
from accelerate.logging import get_logger
from accelerate.utils import ProjectConfiguration, set_seed

import diffusers
from diffusers import AutoencoderKL, DDPMScheduler, DDIMScheduler
from diffusers.optimization import get_scheduler
from diffusers.training_utils import EMAModel
from diffusers.utils.import_utils import is_xformers_available

import transformers
from transformers import CLIPTextModel, CLIPTokenizer, CLIPImageProcessor

from pbr.models.unet_dr2d_condition import UNetDR2DConditionModel
from pbr.pipelines.pipeline_idarbdiffusion import IDArbDiffusionPipeline
from pbr.data.mv_dataset_arbobjaverse import MVDataset

from pbr.utils.config import TrainingConfig, load_config
from pbr.utils.metrics import MetricCalculator

import random

logger = get_logger(__name__, log_level="INFO")


def load_scheduler(scheduler_type, cfg):
    if scheduler_type == 'ddpm':
        noise_scheduler = DDPMScheduler()
    elif scheduler_type == 'ddim':
        noise_scheduler = DDIMScheduler()
    return_unused_kwargs=False
    config, kwargs, commit_hash = noise_scheduler.load_config(
        pretrained_model_name_or_path=cfg.pretrained_model_name_or_path,
        subfolder="scheduler",
        return_unused_kwargs=True,
        return_commit_hash=True,
    )

    if cfg.zero_snr:
        config['prediction_type'] = "v_prediction"
        config['rescale_betas_zero_snr'] = True
    if cfg.linear_noise_schedule:
        config['beta_schedule'] = 'linear'

    noise_scheduler = noise_scheduler.from_config(config, return_unused_kwargs=return_unused_kwargs)
    return noise_scheduler


def split_data(data_in):
    albedo = data_in[::3]
    normal = data_in[1::3]
    mr = data_in[2::3]
    mtl = mr[:, :1, ...].repeat(1, 3, 1, 1)
    rgh = mr[:, 1:2, ...].repeat(1, 3, 1, 1)
    data_out = torch.stack([albedo, normal, mtl, rgh], dim=1).flatten(0, 1)
    return data_out


def log_validation(dataloader, vae, text_encoder, tokenizer, feature_extractor, unet, cfg: TrainingConfig, accelerator: Accelerator, weight_dtype, global_step, name, save_dir):
    logger.info(f"Running {name} ... ")

    scheduler = load_scheduler('ddim', cfg)
    pipeline = IDArbDiffusionPipeline(
        text_encoder=text_encoder,
        tokenizer=tokenizer,
        feature_extractor=feature_extractor,
        vae=vae,
        unet=accelerator.unwrap_model(unet),
        safety_checker=None,
        scheduler=scheduler,
        **cfg.pipe_kwargs
    )

    pipeline.to(accelerator.device)
    pipeline.set_progress_bar_config(disable=True)

    if cfg.enable_xformers_memory_efficient_attention:
        pipeline.enable_xformers_memory_efficient_attention()

    if cfg.seed is None:
        generator = None
    else:
        generator = torch.Generator(device=accelerator.device).manual_seed(cfg.seed)
    
    nrow = cfg.validation_grid_nrow
    metrics_sum = {}
    for mode in ['multi', 'single']:
        metrics_sum[mode] = defaultdict(list)
    metrics_calc = MetricCalculator(cfg.metrics, accelerator.device)


    # 随机选取5个batch的索引
    for i, batch in tqdm(enumerate(dataloader)):


        # (B, Nv, 3, H, W), (B, Nv, ND, 3, H, W), (B, Nv, 3, H, W), (B, Nv, Nce)
        imgs_in, imgs_out, imgs_mask, task_ids = batch['imgs_in'], batch['imgs_out'], batch['imgs_mask'], batch['task_ids']
        cam_pose = batch['pose']

        imgs_in, imgs_out = imgs_in.to(weight_dtype), imgs_out.to(weight_dtype)
        cam_pose = cam_pose.to(weight_dtype)
        
        B, Nv, Nd = imgs_out.shape[:3] # batch_size, num_views, num_domains

        # (B ND) 3 H W
        imgs_out, imgs_in, imgs_mask, task_ids = imgs_out.flatten(0,2), imgs_in.flatten(0,1), imgs_mask.flatten(0,1), task_ids.flatten(0,2)

        imgs_pred = {}
        with torch.autocast("cuda"):

            for mode in ['multi', 'single']:
                if mode == 'single':
                    Nv_ = 1
                    cam_pose_ = rearrange(cam_pose, 'b t c -> (b t) 1 c')
                else:
                    Nv_ = Nv
                    cam_pose_ = cam_pose
                if cfg.wo_camera:
                    cam_pose_ = None
                out = pipeline(
                    imgs_in,
                    task_ids,
                    num_views=Nv_,
                    cam_pose=cam_pose_,
                    generator=generator,
                    guidance_scale=1.0,
                    output_type='pt',
                    num_images_per_prompt=1,
                    **cfg.pipe_validation_kwargs,
                ).images
                imgs_pred[mode] = out

                # calculate and collect metrics
                metrics = metrics_calc(out, imgs_out, imgs_mask)
                for k in metrics:
                    v = torch.tensor(metrics[k], device=accelerator.device)
                    all_v = accelerator.gather_for_metrics(v)
                    # if k not in metrics_sum:
                    #     metrics_sum[k] = []
                    # metrics_sum[k].append(all_v.detach().cpu().numpy())
                    metrics_sum[mode][k].append(all_v.detach().cpu().numpy())

        # save first iter data for visualization
        if accelerator.is_main_process and i == 0:
            img_cond_grid = make_grid(imgs_in, nrow=(nrow//Nd), padding=0, value_range=(0, 1))
            save_image(img_cond_grid, os.path.join(save_dir, f'{global_step}-{name}-cond.png'))
            imgs_out = split_data(imgs_out)
            img_gt_grid = make_grid(imgs_out, nrow=nrow, padding=0, value_range=(0, 1))
            save_image(img_gt_grid, os.path.join(save_dir, f'{global_step}-{name}-gt.png'))
            for mode in ['multi', 'single']:
                out = imgs_pred[mode]
                out = split_data(out)
                img_pred_grid = make_grid(out, nrow=nrow, padding=0, value_range=(0, 1))
                save_image(img_pred_grid, os.path.join(save_dir, f'{global_step}-{name}-pred-{mode}.png'))

    metrics_log = {}
    for mode in ['multi', 'single']:
        for k in metrics_sum[mode]:
            m_value = np.concatenate(metrics_sum[mode][k])
            m_value = m_value[np.isfinite(m_value)]
            metrics_sum[mode][k] = m_value.mean().item()
            metrics_log[f'{name}/{mode}/{k}'] = metrics_sum[mode][k]
        if accelerator.is_main_process:
            print(f'{name}/{mode}')
            print(metrics_sum[mode])
    accelerator.log(metrics_log, step=global_step)

    torch.cuda.empty_cache()


def main(
    cfg: TrainingConfig
):
    # override local_rank with envvar
    env_local_rank = int(os.environ.get("LOCAL_RANK", -1))
    if env_local_rank != -1 and env_local_rank != cfg.local_rank:
        cfg.local_rank = env_local_rank

    vis_dir = os.path.join(cfg.output_dir, cfg.vis_dir)
    logging_dir = os.path.join(cfg.output_dir, cfg.logging_dir)
    accelerator_project_config = ProjectConfiguration(project_dir=cfg.output_dir, logging_dir=logging_dir)

    accelerator = Accelerator(
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        mixed_precision=cfg.mixed_precision,
        log_with=cfg.report_to,
        project_config=accelerator_project_config,
    )

    # Make one log on every process with the configuration for debugging.
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO,
    )
    logger.info(accelerator.state, main_process_only=False)
    if accelerator.is_local_main_process:
        transformers.utils.logging.set_verbosity_warning()
        diffusers.utils.logging.set_verbosity_info()
    else:
        transformers.utils.logging.set_verbosity_error()
        diffusers.utils.logging.set_verbosity_error()

    # If passed along, set the training seed now.
    if cfg.seed is not None:
        set_seed(cfg.seed)

    generator = torch.Generator(device=accelerator.device).manual_seed(cfg.seed)

    # Handle the repository creation
    if accelerator.is_main_process:
        os.makedirs(cfg.output_dir, exist_ok=True)
        os.makedirs(vis_dir, exist_ok=True)
        OmegaConf.save(cfg, os.path.join(cfg.output_dir, 'config.yaml'))

    # Load scheduler, tokenizer and models.
    noise_scheduler = load_scheduler('ddpm', cfg)
    text_encoder = CLIPTextModel.from_pretrained(cfg.pretrained_model_name_or_path, subfolder="text_encoder")
    tokenizer = CLIPTokenizer.from_pretrained(cfg.pretrained_model_name_or_path, subfolder="tokenizer")
    feature_extractor = CLIPImageProcessor.from_pretrained(cfg.pretrained_model_name_or_path, subfolder="feature_extractor", revision=cfg.revision)
    vae = AutoencoderKL.from_pretrained(cfg.pretrained_model_name_or_path, subfolder="vae", revision=cfg.revision)
    if cfg.pretrained_unet_path is None:
        unet = UNetDR2DConditionModel.from_pretrained_2d(cfg.pretrained_model_name_or_path, subfolder="unet", revision=cfg.revision, **cfg.unet_from_pretrained_kwargs)
    else:
        print("load pre-trained unet from ", cfg.pretrained_unet_path)
        unet = UNetDR2DConditionModel.from_pretrained(cfg.pretrained_unet_path, subfolder="unet", revision=cfg.revision, **cfg.unet_from_pretrained_kwargs)
    if cfg.use_ema:
        ema_unet = EMAModel(unet.parameters(), model_cls=UNetDR2DConditionModel, model_config=unet.config)

    def compute_snr(timesteps):
        """
        Computes SNR as per https://github.com/TiankaiHang/Min-SNR-Diffusion-Training/blob/521b624bd70c67cee4bdf49225915f5945a872e3/guided_diffusion/gaussian_diffusion.py#L847-L849
        """
        alphas_cumprod = noise_scheduler.alphas_cumprod
        sqrt_alphas_cumprod = alphas_cumprod**0.5
        sqrt_one_minus_alphas_cumprod = (1.0 - alphas_cumprod) ** 0.5

        # Expand the tensors.
        # Adapted from https://github.com/TiankaiHang/Min-SNR-Diffusion-Training/blob/521b624bd70c67cee4bdf49225915f5945a872e3/guided_diffusion/gaussian_diffusion.py#L1026
        sqrt_alphas_cumprod = sqrt_alphas_cumprod.to(device=timesteps.device)[timesteps].float()
        while len(sqrt_alphas_cumprod.shape) < len(timesteps.shape):
            sqrt_alphas_cumprod = sqrt_alphas_cumprod[..., None]
        alpha = sqrt_alphas_cumprod.expand(timesteps.shape)

        sqrt_one_minus_alphas_cumprod = sqrt_one_minus_alphas_cumprod.to(device=timesteps.device)[timesteps].float()
        while len(sqrt_one_minus_alphas_cumprod.shape) < len(timesteps.shape):
            sqrt_one_minus_alphas_cumprod = sqrt_one_minus_alphas_cumprod[..., None]
        sigma = sqrt_one_minus_alphas_cumprod.expand(timesteps.shape)

        # Compute SNR.
        snr = (alpha / sigma) ** 2
        return snr
    
    # Freeze vae and text_encoder
    vae.requires_grad_(False)
    text_encoder.requires_grad_(False)
    
    if cfg.trainable_modules is None:
        unet.requires_grad_(True)
    else:
        unet.requires_grad_(False)
        for name, module in unet.named_modules():
            if name.endswith(tuple(cfg.trainable_modules)):
                for params in module.parameters():
                    # print("trainable: ", params)
                    params.requires_grad = True                

    if cfg.enable_xformers_memory_efficient_attention:
        if is_xformers_available():
            import xformers

            xformers_version = version.parse(xformers.__version__)
            if xformers_version == version.parse("0.0.16"):
                logger.warn(
                    "xFormers 0.0.16 cannot be used for training in some GPUs. If you observe problems during training, please update xFormers to at least 0.0.17. See https://huggingface.co/docs/diffusers/main/en/optimization/xformers for more details."
                )
            unet.enable_xformers_memory_efficient_attention()
            print("use xformers to speed up")
        else:
            raise ValueError("xformers is not available. Make sure it is installed correctly")
        
    # `accelerate` 0.16.0 will have better support for customized saving
    if version.parse(accelerate.__version__) >= version.parse("0.16.0"):
        # create custom saving & loading hooks so that `accelerator.save_state(...)` serializes in a nice format
        def save_model_hook(models, weights, output_dir):
            if cfg.use_ema:
                ema_unet.save_pretrained(os.path.join(output_dir, "unet_ema"))

            for i, model in enumerate(models):
                model.save_pretrained(os.path.join(output_dir, "unet"))

                # make sure to pop weight so that corresponding model is not saved again
                weights.pop()

        def load_model_hook(models, input_dir):
            if cfg.use_ema:
                load_model = EMAModel.from_pretrained(os.path.join(input_dir, "unet_ema"), UNetDR2DConditionModel)
                ema_unet.load_state_dict(load_model.state_dict())
                ema_unet.to(accelerator.device)
                del load_model

            for i in range(len(models)):
                # pop models so that they are not loaded again
                model = models.pop()

                # load diffusers style into model
                load_model = UNetDR2DConditionModel.from_pretrained(input_dir, subfolder="unet")
                model.register_to_config(**load_model.config)

                model.load_state_dict(load_model.state_dict())
                del load_model

        accelerator.register_save_state_pre_hook(save_model_hook)
        accelerator.register_load_state_pre_hook(load_model_hook)

    if cfg.gradient_checkpointing:
        unet.enable_gradient_checkpointing()

    # Enable TF32 for faster training on Ampere GPUs,
    # cf https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices
    if cfg.allow_tf32:
        torch.backends.cuda.matmul.allow_tf32 = True        

    if cfg.scale_lr:
        cfg.learning_rate = (
            cfg.learning_rate * cfg.gradient_accumulation_steps * cfg.train_batch_size * accelerator.num_processes
        )

    # Initialize the optimizer
    if cfg.use_8bit_adam:
        try:
            import bitsandbytes as bnb
        except ImportError:
            raise ImportError(
                "Please install bitsandbytes to use 8-bit Adam. You can do so by running `pip install bitsandbytes`"
            )

        optimizer_cls = bnb.optim.AdamW8bit
    else:
        optimizer_cls = torch.optim.AdamW
    optimizer = optimizer_cls(
        unet.parameters(),
        lr=cfg.learning_rate,
        betas=(cfg.adam_beta1, cfg.adam_beta2),
        weight_decay=cfg.adam_weight_decay,
        eps=cfg.adam_epsilon,
    )

    lr_scheduler = get_scheduler(
        cfg.lr_scheduler,
        optimizer=optimizer,
        num_warmup_steps=cfg.lr_warmup_steps * accelerator.num_processes,
        num_training_steps=cfg.max_train_steps * accelerator.num_processes,
    )

    # Get the training dataset
    train_dataset = MVDataset(**cfg.train_dataset)
    validation_dataset = MVDataset(**cfg.validation_dataset)
    validation_train_dataset = MVDataset(**cfg.validation_train_dataset)

    # DataLoaders creation:
    train_dataloader = torch.utils.data.DataLoader(
        train_dataset, batch_size=cfg.train_batch_size, shuffle=True, num_workers=cfg.dataloader_num_workers,
    )
    validation_dataloader = torch.utils.data.DataLoader(
        validation_dataset, batch_size=cfg.validation_batch_size, shuffle=False, num_workers=cfg.dataloader_num_workers
    )
    validation_train_dataloader = torch.utils.data.DataLoader(
        validation_train_dataset, batch_size=cfg.validation_train_batch_size, shuffle=False, num_workers=cfg.dataloader_num_workers
    )

    # Prepare everything with our `accelerator`.
    unet, optimizer, train_dataloader, validation_dataloader, validation_train_dataloader, lr_scheduler = accelerator.prepare(
        unet, optimizer, train_dataloader, validation_dataloader, validation_train_dataloader, lr_scheduler
    )

    if cfg.use_ema:
        ema_unet.to(accelerator.device)

    # For mixed precision training we cast all non-trainable weigths (vae, non-lora text_encoder and non-lora unet) to half-precision
    # as these weights are only used for inference, keeping weights in full precision is not required.
    weight_dtype = torch.float32
    if accelerator.mixed_precision == "fp16":
        weight_dtype = torch.float16
        cfg.mixed_precision = accelerator.mixed_precision
    elif accelerator.mixed_precision == "bf16":
        weight_dtype = torch.bfloat16
        cfg.mixed_precision = accelerator.mixed_precision

    # Move text_encode and vae to gpu and cast to weight_dtype
    text_encoder.to(accelerator.device, dtype=weight_dtype)
    vae.to(accelerator.device, dtype=weight_dtype)

    # prepare task embeddings dictionary
    task_prompts = ['albedo', 'normal', 'metallic and roughness', 'metallic', 'roughness']
    with torch.no_grad():
        input_ids = tokenizer(task_prompts, max_length=tokenizer.model_max_length, padding="max_length", truncation=True, return_tensors="pt").input_ids
        input_ids = input_ids.to(accelerator.device)
        text_embeddings_dict = text_encoder(input_ids, return_dict=False)[0]

    # We need to recalculate our total training steps as the size of the training dataloader may have changed.
    num_update_steps_per_epoch = math.ceil(len(train_dataloader) / cfg.gradient_accumulation_steps)
    num_train_epochs = math.ceil(cfg.max_train_steps / num_update_steps_per_epoch)

    # We need to initialize the trackers we use, and also store our configuration.
    # The trackers initializes automatically on the main process.
    if accelerator.is_main_process:
        # tracker_config = dict(vars(cfg))
        tracker_config = {}
        accelerator.init_trackers(cfg.tracker_project_name, tracker_config)    

    # Train!
    total_batch_size = cfg.train_batch_size * accelerator.num_processes * cfg.gradient_accumulation_steps

    logger.info("***** Running training *****")
    logger.info(f"  Num examples = {len(train_dataset)}")
    logger.info(f"  Num Epochs = {num_train_epochs}")
    logger.info(f"  Instantaneous batch size per device = {cfg.train_batch_size}")
    logger.info(f"  Total train batch size (w. parallel, distributed & accumulation) = {total_batch_size}")
    logger.info(f"  Gradient Accumulation steps = {cfg.gradient_accumulation_steps}")
    logger.info(f"  Total optimization steps = {cfg.max_train_steps}")
    global_step = 0
    first_epoch = 0

    # Potentially load in the weights and states from a previous save
    if cfg.resume_from_checkpoint:
        if cfg.resume_from_checkpoint != "latest":
            path = os.path.basename(cfg.resume_from_checkpoint)
        else:
            # Get the most recent checkpoint
            if os.path.exists(os.path.join(cfg.output_dir, "checkpoint")):
                path = "checkpoint"
            else:
                dirs = os.listdir(cfg.output_dir)
                dirs = [d for d in dirs if d.startswith("checkpoint")]
                dirs = sorted(dirs, key=lambda x: int(x.split("-")[1]))
                path = dirs[-1] if len(dirs) > 0 else None

        if path is None:
            accelerator.print(
                f"Checkpoint '{cfg.resume_from_checkpoint}' does not exist. Starting a new training run."
            )
            cfg.resume_from_checkpoint = None
        else:
            accelerator.print(f"Resuming from checkpoint {path}")
            accelerator.load_state(os.path.join(cfg.output_dir, path))
            global_step = int(path.split("-")[1])

            resume_global_step = global_step * cfg.gradient_accumulation_steps
            first_epoch = global_step // num_update_steps_per_epoch
            resume_step = resume_global_step % (num_update_steps_per_epoch * cfg.gradient_accumulation_steps)        

    # Only show the progress bar once on each machine.
    progress_bar = tqdm(range(cfg.max_train_steps), disable=not accelerator.is_main_process)
    progress_bar.set_description("Steps")
    if global_step > 0:
        progress_bar.update(global_step)

    for epoch in range(first_epoch, num_train_epochs):
        unet.train()
        train_loss = 0.0

        # Skip steps until we reach the resumed step
        if cfg.resume_from_checkpoint and epoch == first_epoch and resume_step is not None:
            activate_dataloader = accelerator.skip_first_batches(train_dataloader, resume_step)
        else:
            activate_dataloader = train_dataloader
        
        for step, batch in enumerate(activate_dataloader):
            print("current step:",step)

            p = np.random.rand()
            mode = 'single' if p < cfg.single_view_prob else 'multi'
            with accelerator.accumulate(unet):
                # (B, Nv, 3, H, W), (B, Nv, ND, 3, H, W), (B, Nv, Nce) (B, Nv)
                imgs_in, imgs_out, task_ids, cam_pose = batch['imgs_in'], batch['imgs_out'], batch['task_ids'], batch['pose']

                B, Nv, Nd = imgs_out.shape[:3] # batch_size, num_views, num_domains
                if mode == 'single':
                    B = B * Nv
                    Nv = 1
                    cam_pose = rearrange(cam_pose, 'b t c -> (b t) 1 c')

                # (B Nv Nd) 3 H W
                imgs_out, imgs_in, task_ids = imgs_out.flatten(0,2), imgs_in.flatten(0,1), task_ids.flatten(0,2)
                text_embeddings = text_embeddings_dict[task_ids]

                imgs_in, imgs_out = imgs_in.to(weight_dtype), imgs_out.to(weight_dtype)
                cam_pose = cam_pose.to(weight_dtype)
                if cfg.wo_camera:
                    cam_pose = None

                cond_vae_embeddings = vae.encode(imgs_in * 2.0 - 1.0).latent_dist.mode() # (B, 4, Hl, Wl)
                if cfg.scale_input_latents:
                    cond_vae_embeddings = cond_vae_embeddings * vae.config.scaling_factor

                latents = vae.encode(imgs_out * 2.0 - 1.0).latent_dist.sample() * vae.config.scaling_factor

                noise = torch.randn_like(latents)

                # same noise for different domains of the same object
                timesteps = torch.randint(0, noise_scheduler.config.num_train_timesteps, (B,), device=latents.device).repeat_interleave(Nd*Nv)
                timesteps = timesteps.long()

                noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

                # Conditioning dropout to support classifier-free guidance during inference. For more details
                # check out the section 3.2.1 of the original paper https://arxiv.org/abs/2211.09800.
                if cfg.use_classifier_free_guidance and cfg.condition_drop_rate > 0.:
                    # drop_as_a_whole: drop a group of normals and colors as a whole
                    random_p = torch.rand(B, device=latents.device, generator=generator)
                    
                    # Sample masks for the conditioning images.
                    image_mask_dtype = cond_vae_embeddings.dtype
                    image_mask = 1 - (
                        (random_p >= cfg.condition_drop_rate).to(image_mask_dtype)
                        * (random_p < 3 * cfg.condition_drop_rate).to(image_mask_dtype)
                    )
                    image_mask = image_mask.reshape(B, 1, 1, 1).repeat_interleave(Nv, dim=0)
                    # Final image conditioning.
                    cond_vae_embeddings = image_mask * cond_vae_embeddings

                cond_vae_embeddings = cond_vae_embeddings.repeat_interleave(Nd, dim=0) # (B ND, 4, Hl, Wl)
                latent_model_input = torch.cat([noisy_latents, cond_vae_embeddings], dim=1) # (B ND, 8, Hl, Wl)

                model_pred = unet(
                    latent_model_input,
                    timesteps,
                    pose=cam_pose,
                    num_views=Nv,
                    encoder_hidden_states=text_embeddings,
                ).sample

                # Get the target for loss depending on the prediction type
                if noise_scheduler.config.prediction_type == "epsilon":
                    target = noise
                elif noise_scheduler.config.prediction_type == "v_prediction":
                    target = noise_scheduler.get_velocity(latents, noise, timesteps)
                else:
                    raise ValueError(f"Unknown prediction type {noise_scheduler.config.prediction_type}") 

                if cfg.snr_gamma is None:
                    loss = F.mse_loss(model_pred.float(), target.float(), reduction="mean")
                else:
                    # Compute loss-weights as per Section 3.4 of https://arxiv.org/abs/2303.09556.
                    # Since we predict the noise instead of x_0, the original formulation is slightly changed.
                    # This is discussed in Section 4.2 of the same paper.
                    snr = compute_snr(timesteps)
                    mse_loss_weights = (
                        torch.stack([snr, cfg.snr_gamma * torch.ones_like(timesteps)], dim=1).min(dim=1)[0] / snr
                    )
                    # We first calculate the original loss. Then we mean over the non-batch dimensions and
                    # rebalance the sample-wise losses with their respective loss weights.
                    # Finally, we take the mean of the rebalanced loss.
                    loss = F.mse_loss(model_pred.float(), target.float(), reduction="none")
                    loss = loss.mean(dim=list(range(1, len(loss.shape)))) * mse_loss_weights
                    loss = loss.mean()

                    if torch.isnan(model_pred).any():
                        print("model_pred is NaN. Taking action.")
                    if torch.isnan(target).any():
                        print("target is NaN. Taking action.")


                    

                # Gather the losses across all processes for logging (if we use distributed training).
                avg_loss = accelerator.gather(loss.repeat(cfg.train_batch_size)).mean()

                train_loss += avg_loss.item() / cfg.gradient_accumulation_steps
                if not torch.isnan(avg_loss):
                    # Backpropagate
                    accelerator.backward(loss)
                    if accelerator.sync_gradients and cfg.max_grad_norm is not None:
                        accelerator.clip_grad_norm_(unet.parameters(), cfg.max_grad_norm)
                    optimizer.step()
                    lr_scheduler.step()
                    optimizer.zero_grad()
                else:
                    # NaN detected: clear gradients
                    optimizer.zero_grad()
                    # Optionally, reset lr_scheduler if desired
                    # lr_scheduler = <Create a new scheduler or reset>
                    print("NaN detected in the loss. Cleared optimizer states.")
                    

            # Checks if the accelerator has performed an optimization step behind the scenes
            if accelerator.sync_gradients:
                if cfg.use_ema:
                    ema_unet.step(unet.parameters())
                progress_bar.update(1)
                global_step += 1
                accelerator.log({"train_loss": train_loss}, step=global_step)
                train_loss = 0.0

                if global_step % cfg.checkpointing_steps == 0:
                    if accelerator.is_main_process:
                        save_path = os.path.join(cfg.output_dir, f"checkpoint-{global_step}")
                        accelerator.save_state(save_path)
                        ckpt_dirs = [d for d in os.listdir(cfg.output_dir) if d.startswith("checkpoint")]
                        ckpt_dirs = sorted(ckpt_dirs, key=lambda x: int(x.split("-")[1]))
                        if len(ckpt_dirs) > cfg.checkpoints_total_limit:
                            for i in range(len(ckpt_dirs) - cfg.checkpoints_total_limit):
                                shutil.rmtree(os.path.join(cfg.output_dir, ckpt_dirs[i]))
                        logger.info(f"Saved state to {save_path}")

                if global_step % cfg.validation_steps == 0 or (cfg.validation_sanity_check and global_step == 1):
                    # if accelerator.is_main_process:
                    if cfg.use_ema:
                        # Store the UNet parameters temporarily and load the EMA parameters to perform inference.
                        ema_unet.store(unet.parameters())
                        ema_unet.copy_to(unet.parameters())
                    log_validation(
                        validation_dataloader,
                        vae,
                        text_encoder,
                        tokenizer,
                        feature_extractor,
                        unet,
                        cfg,
                        accelerator,
                        weight_dtype,
                        global_step,
                        'validation',
                        vis_dir
                    )
         
                    if cfg.use_ema:
                        # Switch back to the original UNet parameters.
                        ema_unet.restore(unet.parameters())

            logs = {"step_loss": loss.detach().item(), "lr": lr_scheduler.get_last_lr()[0]}
            progress_bar.set_postfix(**logs)

            if global_step >= cfg.max_train_steps:
                break

    # Create the pipeline using the trained modules and save it.
    accelerator.wait_for_everyone()
    if accelerator.is_main_process:
        unet = accelerator.unwrap_model(unet)
        if cfg.use_ema:
            ema_unet.copy_to(unet.parameters())
        scheduler = load_scheduler('ddim', cfg)
        pipeline = IDArbDiffusionPipeline(
            text_encoder=text_encoder,
            tokenizer=tokenizer,
            feature_extractor=feature_extractor,
            vae=vae,
            unet=unet,
            safety_checker=None,
            scheduler=scheduler,
            **cfg.pipe_kwargs,
        )            
        os.makedirs(os.path.join(cfg.output_dir, "pipeckpts"), exist_ok=True)
        pipeline.save_pretrained(os.path.join(cfg.output_dir, "pipeckpts"))

    accelerator.end_training()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    cfg = load_config(args.config)
    main(cfg)
