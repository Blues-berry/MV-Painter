import os
from dataclasses import dataclass
from omegaconf import OmegaConf
from typing import Dict, Optional, Tuple, List


# ============ Register OmegaConf Recolvers ============= #
OmegaConf.register_new_resolver('calc_exp_lr_decay_rate', lambda factor, n: factor**(1./n))
OmegaConf.register_new_resolver('add', lambda a, b: a + b)
OmegaConf.register_new_resolver('sub', lambda a, b: a - b)
OmegaConf.register_new_resolver('mul', lambda a, b: a * b)
OmegaConf.register_new_resolver('div', lambda a, b: a / b)
OmegaConf.register_new_resolver('idiv', lambda a, b: a // b)
OmegaConf.register_new_resolver('basename', lambda p: os.path.basename(p))
# ======================================================= #

@dataclass
class TrainingConfig:
    pretrained_model_name_or_path: str
    pretrained_unet_path: Optional[str]
    revision: Optional[str]
    dataset_root: Dict
    train_dataset: Dict
    validation_dataset: Dict
    validation_train_dataset: Dict
    output_dir: str
    seed: Optional[int]
    train_batch_size: int
    validation_batch_size: int
    validation_train_batch_size: int
    max_train_steps: int
    gradient_accumulation_steps: int
    gradient_checkpointing: bool
    learning_rate: float
    scale_lr: bool
    lr_scheduler: str
    lr_warmup_steps: int
    snr_gamma: Optional[float]
    use_8bit_adam: bool
    allow_tf32: bool
    use_ema: bool
    dataloader_num_workers: int
    adam_beta1: float
    adam_beta2: float
    adam_weight_decay: float
    adam_epsilon: float
    max_grad_norm: Optional[float]
    logging_dir: str
    vis_dir: str
    mixed_precision: Optional[str]
    report_to: Optional[str]
    local_rank: int
    checkpointing_steps: int
    checkpoints_total_limit: Optional[int]
    resume_from_checkpoint: Optional[str]
    enable_xformers_memory_efficient_attention: bool
    validation_steps: int
    validation_sanity_check: bool
    tracker_project_name: str

    trainable_modules: Optional[list]
    use_classifier_free_guidance: bool
    condition_drop_rate: float
    scale_input_latents: bool

    pipe_kwargs: Dict
    pipe_validation_kwargs: Dict
    unet_from_pretrained_kwargs: Dict
    validation_grid_nrow: int

    num_domains: int
    camera_embedding_type: str

    metrics: Dict

    single_view_prob: float
    zero_snr: bool = False
    linear_noise_schedule: bool = False

    wo_camera: bool = False


def load_config(cfg_path):
    cfg = OmegaConf.load(cfg_path)
    
    num_domains = 3
    cfg.validation_grid_nrow = 6

    cfg.num_domains = num_domains
    cfg.unet_from_pretrained_kwargs['num_domains'] = num_domains
    cfg.unet_from_pretrained_kwargs['projection_class_embeddings_input_dim'] = num_domains * 2
    if 'img_wh' in cfg.train_dataset:
        cfg.unet_from_pretrained_kwargs['sample_size'] = cfg.train_dataset['img_wh'][0] // 8
    else:
        cfg.unet_from_pretrained_kwargs['sample_size'] = 512 // 8

    cfg.pipe_kwargs['num_domains'] = num_domains
    if 'dataset_root' in cfg:
        cfg.train_dataset['data_root'] = cfg.dataset_root
        cfg.validation_dataset['data_root'] = cfg.dataset_root
        cfg.validation_train_dataset['data_root'] = cfg.dataset_root

    schema = OmegaConf.structured(TrainingConfig)
    cfg = OmegaConf.merge(schema, cfg)
    return cfg

