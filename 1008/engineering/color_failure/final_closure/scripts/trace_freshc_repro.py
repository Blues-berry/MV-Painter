#!/usr/bin/env python3
"""Read-only tensor trace around the frozen validation-v3 runner.

The upstream runner remains untouched. This wrapper records selected tensors
before and after the UNet, scheduler, and VAE calls for a small fixed object
subset. Run under each environment with separate MVP_RUN_DIR values.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch
import torchvision
import diffusers
import transformers
from PIL import Image
from torchvision.utils import save_image

ROOT = Path("/4T/CXY/MV-Painter")
TRACE_ROOT = Path(os.environ["MVP_FORENSIC_TRACE_DIR"])
RUN_SCRIPT = ROOT / "scripts/run_validation_v3_experiment.py"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))

import geotex.eval_exploration as ee  # noqa: E402
import geotex.explore_contradiction as exp  # noqa: E402

spec = importlib.util.spec_from_file_location("frozen_v3_runner", RUN_SCRIPT)
runner = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(runner)

KEY_STEPS = {0, 1, 10, 25, 33, 40, 45, 49}
ACTIVE: dict | None = None
SEQUENCE: list[tuple[int, str, str]] = []
SEQUENCE_INDEX = 0
MODEL_DETAILS: dict = {}
MODEL_INSTANCE = None
ORIGINAL_VAE_DECODE = None
ORIGINAL_STEP = exp.EulerDiscreteScheduler.step
ORIGINAL_GENERATE = exp.generate_with_schedule
ORIGINAL_LOAD_MODEL = ee.load_model


def cpu_copy(value):
    if torch.is_tensor(value):
        return value.detach().to("cpu").contiguous().clone()
    if isinstance(value, dict):
        return {key: cpu_copy(subvalue) for key, subvalue in value.items()}
    if isinstance(value, list):
        return [cpu_copy(subvalue) for subvalue in value]
    if isinstance(value, tuple):
        return tuple(cpu_copy(subvalue) for subvalue in value)
    return value


def tensor_sha(value) -> str:
    """Hash a tensor or nested tensor tree with names, dtypes, and shapes."""
    digest = hashlib.sha256()

    def update(item, path="root"):
        if torch.is_tensor(item):
            array = item.detach().contiguous().cpu().numpy()
            digest.update(f"tensor:{path}:{item.dtype}:{tuple(item.shape)}:".encode())
            digest.update(array.tobytes())
        elif isinstance(item, dict):
            digest.update(f"dict:{path}:".encode())
            for key in sorted(item, key=str):
                update(item[key], f"{path}.{key}")
        elif isinstance(item, (list, tuple)):
            digest.update(f"{type(item).__name__}:{path}:{len(item)}:".encode())
            for idx, subitem in enumerate(item):
                update(subitem, f"{path}[{idx}]")
        else:
            digest.update(f"value:{path}:{type(item).__name__}:{item!r};".encode())

    update(value)
    return digest.hexdigest()


def save_tensor_trace(key: str, tensor: torch.Tensor) -> None:
    if ACTIVE is None or ACTIVE["step"] not in KEY_STEPS:
        return
    ACTIVE["tensors"][f"{key}_step{ACTIVE['step']:02d}"] = cpu_copy(tensor)


def unet_pre_hook(module, args, kwargs):
    if ACTIVE is None:
        return
    step_idx = ACTIVE["unet_calls"]
    ACTIVE["unet_calls"] += 1
    ACTIVE["step"] = step_idx
    if step_idx in KEY_STEPS:
        latent = args[0] if args else kwargs.get("sample")
        timestep = args[1] if len(args) > 1 else kwargs.get("timestep")
        ACTIVE["tensors"][f"unet_input_step{step_idx:02d}"] = cpu_copy(latent)
        ACTIVE["tensors"][f"unet_timestep_step{step_idx:02d}"] = cpu_copy(timestep)
        for name in ("encoder_hidden_states", "added_cond_kwargs", "cross_attention_kwargs"):
            value = kwargs.get(name)
            if torch.is_tensor(value):
                ACTIVE["tensors"][f"unet_{name}_step{step_idx:02d}"] = cpu_copy(value)
            elif isinstance(value, dict):
                for subname, subvalue in value.items():
                    if torch.is_tensor(subvalue):
                        ACTIVE["tensors"][f"unet_{name}_{subname}_step{step_idx:02d}"] = cpu_copy(subvalue)


def unet_post_hook(module, args, kwargs, output):
    if ACTIVE is None or ACTIVE["step"] not in KEY_STEPS:
        return
    value = output[0] if isinstance(output, (tuple, list)) else getattr(output, "sample", output)
    if torch.is_tensor(value):
        save_tensor_trace("noise_prediction", value)


def traced_scheduler_step(self, *args, **kwargs):
    global ACTIVE
    if len(args) >= 3:
        model_output, timestep, sample = args[:3]
        rest = args[3:]
    else:
        model_output = kwargs["model_output"]
        timestep = kwargs["timestep"]
        sample = kwargs["sample"]
        rest = ()
    idx = ACTIVE["scheduler_calls"] if ACTIVE is not None else -1
    if ACTIVE is not None and idx == 0:
        scheduler = {
            "class": f"{type(self).__module__}.{type(self).__name__}",
            "config": dict(self.config),
            "init_noise_sigma": float(self.init_noise_sigma),
            "timesteps": cpu_copy(self.timesteps),
            "sigmas": cpu_copy(self.sigmas),
            "prediction_type": getattr(self.config, "prediction_type", None),
        }
        ACTIVE["metadata"]["scheduler"] = scheduler
    if ACTIVE is not None and idx in KEY_STEPS:
        ACTIVE["tensors"][f"scheduler_input_latent_step{idx:02d}"] = cpu_copy(sample)
        ACTIVE["tensors"][f"scheduler_input_noise_step{idx:02d}"] = cpu_copy(model_output)
        ACTIVE["tensors"][f"scheduler_timestep_step{idx:02d}"] = cpu_copy(timestep)
    if rest:
        result = ORIGINAL_STEP(self, model_output, timestep, sample, *rest, **kwargs)
    else:
        kwargs.pop("model_output", None)
        kwargs.pop("timestep", None)
        kwargs.pop("sample", None)
        result = ORIGINAL_STEP(self, model_output, timestep, sample, **kwargs)
    if ACTIVE is not None and idx in KEY_STEPS:
        value = result[0] if isinstance(result, (tuple, list)) else result.prev_sample
        ACTIVE["tensors"][f"scheduler_output_latent_step{idx:02d}"] = cpu_copy(value)
    if ACTIVE is not None:
        ACTIVE["scheduler_calls"] += 1
    return result


def wrap_model(model, config):
    global ORIGINAL_VAE_DECODE
    MODEL_DETAILS.update({
        "unet_parameter_dtypes": sorted({str(p.dtype) for p in model.pipeline.unet.parameters()}),
        "vae_parameter_dtypes": sorted({str(p.dtype) for p in model.pipeline.vae.parameters()}),
        "adapter_parameter_dtypes": sorted({str(p.dtype) for p in model.adapters.parameters()}),
        "geo_encoder_parameter_dtypes": sorted({str(p.dtype) for p in model.geo_encoder.parameters()}),
        "unet_attention_processors": {
            name: f"{type(value).__module__}.{type(value).__name__}"
            for name, value in model.pipeline.unet.attn_processors.items()
        },
        "unet_attention_implementation": getattr(model.pipeline.unet.config, "_attn_implementation", None),
        "scheduler_config": dict(model.pipeline.scheduler.config),
    })
    model.pipeline.unet.register_forward_pre_hook(unet_pre_hook, with_kwargs=True)
    model.pipeline.unet.register_forward_hook(unet_post_hook, with_kwargs=True)
    original_decode = model.pipeline.vae.decode
    ORIGINAL_VAE_DECODE = original_decode

    def traced_decode(*args, **kwargs):
        if ACTIVE is not None and args:
            ACTIVE["tensors"]["vae_decode_input"] = cpu_copy(args[0])
        decoded = original_decode(*args, **kwargs)
        if ACTIVE is not None:
            value = decoded[0] if isinstance(decoded, (tuple, list)) else decoded.sample
            ACTIVE["tensors"]["vae_decoded_rgb"] = cpu_copy(value)
        return decoded

    model.pipeline.vae.decode = traced_decode
    return model, config


def traced_load_model(*args, **kwargs):
    global MODEL_INSTANCE
    model = ORIGINAL_LOAD_MODEL(*args, **kwargs)
    wrap_model(model, None)
    MODEL_INSTANCE = model
    return model


def traced_generate(*args, **kwargs):
    global ACTIVE, SEQUENCE_INDEX
    if SEQUENCE_INDEX >= len(SEQUENCE):
        raise RuntimeError("trace sequence exhausted; runner condition order changed")
    object_idx, uid, condition = SEQUENCE[SEQUENCE_INDEX]
    SEQUENCE_INDEX += 1
    trace_file = TRACE_ROOT / uid / f"{condition}.pt"
    ACTIVE = {
        "step": -1,
        "unet_calls": 0,
        "scheduler_calls": 0,
        "metadata": {
            "uid": uid,
            "object_idx": object_idx,
            "condition": condition,
            "weight_dtype": str(args[3]),
            "input_hashes": {},
            "tensor_hashes": {},
        },
        "tensors": {},
    }
    model, batch, device, weight_dtype, geo_feats, _, _, init_latents, _ = args
    ACTIVE["metadata"]["weight_dtype"] = str(weight_dtype)
    for key in ("cond_imgs", "target_imgs", "depth_imgs", "real_depth_imgs", "global_embeds"):
        if key in batch and torch.is_tensor(batch[key]):
            ACTIVE["metadata"]["input_hashes"][key] = tensor_sha(batch[key])
            if os.environ.get("MVP_TRACE_LIGHTWEIGHT") != "1":
                ACTIVE["tensors"][f"batch_{key}"] = cpu_copy(batch[key])
    if geo_feats is not None:
        ACTIVE["metadata"]["tensor_hashes"]["geo_feats"] = tensor_sha(geo_feats)
        if os.environ.get("MVP_TRACE_LIGHTWEIGHT") != "1":
            ACTIVE["tensors"]["geo_feats"] = cpu_copy(geo_feats)
    ACTIVE["metadata"]["tensor_hashes"]["initial_latent"] = tensor_sha(init_latents)
    ACTIVE["tensors"]["initial_latent"] = cpu_copy(init_latents)
    ACTIVE["metadata"]["scheduler_config_source"] = dict(model.pipeline.scheduler.config)
    prediction = ORIGINAL_GENERATE(*args, **kwargs)
    ACTIVE["metadata"]["unet_calls"] = ACTIVE["unet_calls"]
    ACTIVE["metadata"]["scheduler_calls"] = ACTIVE["scheduler_calls"]
    ACTIVE["metadata"]["final_rgb_sha256"] = tensor_sha(prediction)
    ACTIVE["tensors"]["final_rgb"] = cpu_copy(prediction)
    if os.environ.get("MVP_TRACE_INTERMEDIATE_DECODE") == "1":
        trace = ACTIVE
        old_active = ACTIVE
        ACTIVE = None
        image_dir = trace_file.parent
        image_dir.mkdir(parents=True, exist_ok=True)
        decoded_hashes = {}
        try:
            requested_steps = {
                int(x) for x in os.environ.get("MVP_TRACE_INTERMEDIATE_STEPS", "0,10,25,49").split(",")
                if x.strip()
            }
            for step_idx in sorted(requested_steps & KEY_STEPS):
                raw = trace["tensors"][f"scheduler_output_latent_step{step_idx:02d}"]
                raw = raw.to(device=device if isinstance(device, torch.device) else next(model.pipeline.vae.parameters()).device,
                             dtype=next(model.pipeline.vae.parameters()).dtype)
                vae_latent = (raw / 0.75 + 0.22) / model.pipeline.vae.config.scaling_factor
                decoded = ORIGINAL_VAE_DECODE(vae_latent, return_dict=False)[0]
                image = (decoded * 0.8 + 0.5).clamp(0, 1)
                out_path = image_dir / f"{condition}_after_step{step_idx:02d}.png"
                save_image(image, out_path)
                decoded_hashes[str(step_idx)] = {
                    "png_sha256": hashlib.sha256(out_path.read_bytes()).hexdigest(),
                    "latent_source": f"scheduler_output_latent_step{step_idx:02d}",
                }
                del raw, vae_latent, decoded, image
        finally:
            ACTIVE = old_active
        ACTIVE["metadata"]["intermediate_decode_pngs"] = decoded_hashes
    for key, value in ACTIVE["tensors"].items():
        if torch.is_tensor(value):
            ACTIVE["metadata"]["tensor_hashes"][key] = tensor_sha(value)
    trace_file.parent.mkdir(parents=True, exist_ok=True)
    torch.save(ACTIVE, trace_file)
    ACTIVE = None
    return prediction


def main():
    global SEQUENCE
    object_list = Path(os.environ["MVP_OBJECT_LIST"])
    with object_list.open() as f:
        uids = [line.strip() for line in f if line.strip()]
    indices = [int(x) for x in os.environ["MVP_OBJECT_INDICES"].split(",") if x.strip()]
    conditions = sorted(x for x in os.environ["MVP_CONDITIONS"].split(",") if x.strip())
    shard = int(os.environ.get("MVP_SHARD", "0"))
    n_shards = int(os.environ.get("MVP_NUM_SHARDS", "1"))
    indices = [i for i in indices if i % n_shards == shard]
    SEQUENCE = [(i, uids[i], condition) for i in indices for condition in conditions]

    TRACE_ROOT.mkdir(parents=True, exist_ok=True)
    exp.EulerDiscreteScheduler.step = traced_scheduler_step
    exp.generate_with_schedule = traced_generate
    runner.ee.load_model = traced_load_model
    gpus = subprocess.run(
        ["nvidia-smi", "--query-gpu=index,name,driver_version", "--format=csv,noheader"],
        capture_output=True, text=True, check=False,
    ).stdout.strip()
    env = {
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "diffusers": diffusers.__version__,
        "transformers": transformers.__version__,
        "cuda_runtime": torch.version.cuda,
        "gpu_driver_and_model": gpus,
        "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "allow_tf32_matmul": torch.backends.cuda.matmul.allow_tf32,
        "allow_tf32_cudnn": torch.backends.cudnn.allow_tf32,
        "float32_matmul_precision": torch.get_float32_matmul_precision(),
        "cudnn_deterministic": torch.backends.cudnn.deterministic,
        "cudnn_benchmark": torch.backends.cudnn.benchmark,
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "allow_fp16_reduced_precision_reduction": torch.backends.cuda.matmul.allow_fp16_reduced_precision_reduction,
        "attention_processors": None,
        "runner_sha256": hashlib.sha256(RUN_SCRIPT.read_bytes()).hexdigest(),
        "trace_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sequence": [{"object_idx": i, "uid": uid, "condition": cond} for i, uid, cond in SEQUENCE],
    }
    TRACE_ROOT.parent.mkdir(parents=True, exist_ok=True)
    (TRACE_ROOT.parent / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    runner.main()
    roundtrip_input = os.environ.get("MVP_TRACE_VAE_ROUNDTRIP_PNG")
    if roundtrip_input:
        run_vae_roundtrip(
            MODEL_INSTANCE,
            Path(roundtrip_input),
            Path(os.environ["MVP_TRACE_VAE_ROUNDTRIP_OUTPUT_DIR"]),
        )
    env["model_details"] = MODEL_DETAILS
    env["attention_processors"] = MODEL_DETAILS.get("unet_attention_processors")
    (TRACE_ROOT.parent / "environment.json").write_text(json.dumps(env, indent=2) + "\n")


def run_vae_roundtrip(model, image_path: Path, output_dir: Path) -> None:
    """Deterministic-mode and fixed-seed VAE input/output isolation controls."""
    if model is None:
        raise RuntimeError("VAE isolation requested before the runner loaded its model")
    output_dir.mkdir(parents=True, exist_ok=True)
    source = np.asarray(Image.open(image_path).convert("RGB"), dtype=np.uint8)
    image = torch.from_numpy(source.copy()).permute(2, 0, 1).unsqueeze(0).float() / 255.0
    vae = model.pipeline.vae
    device = next(vae.parameters()).device
    dtype = next(vae.parameters()).dtype
    normalized = ((image.to(device=device, dtype=dtype) - 0.5) / 0.8)
    with torch.no_grad():
        posterior = vae.encode(normalized).latent_dist
        latents = {
            "mode": posterior.mode(),
            "sample_seed42": posterior.sample(generator=torch.Generator(device=device).manual_seed(42)),
        }
        results = {}
        for name, latent in latents.items():
            decoded = ORIGINAL_VAE_DECODE(latent, return_dict=False)[0]
            output = (decoded * 0.8 + 0.5).clamp(0, 1)
            path = output_dir / f"vae_roundtrip_{name}.png"
            save_image(output, path)
            results[name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            del decoded, output
    torch.save({"input_normalized": normalized.detach().cpu(), **{k: v.detach().cpu() for k, v in latents.items()}},
               output_dir / "vae_roundtrip_tensors.pt")

    try:
        from skimage.color import deltaE_ciede2000, rgb2lab
    except ImportError as exc:
        raise RuntimeError("scikit-image is required for VAE isolation color metrics") from exc
    reference = source.astype(np.float32) / 255.0
    mask_path = Path(os.environ["MVP_TRACE_VAE_ROUNDTRIP_MASK"])
    mask_grid = np.asarray(Image.open(mask_path).convert("L")) > 127
    rows = []
    for name, record in results.items():
        prediction = np.asarray(Image.open(record["path"]).convert("RGB"), dtype=np.uint8).astype(np.float32) / 255.0
        for view in range(6):
            row, col = divmod(view, 2)
            ys, xs = slice(row * 256, (row + 1) * 256), slice(col * 256, (col + 1) * 256)
            fg = mask_grid[ys, xs]
            ref_tile, pred_tile = reference[ys, xs], prediction[ys, xs]
            lab_ref, lab_pred = rgb2lab(ref_tile), rgb2lab(pred_tile)
            dl = lab_pred - lab_ref
            de = deltaE_ciede2000(lab_ref, lab_pred)
            rows.append({
                "variant": name,
                "view": view,
                "fg_ciede2000": float(de[fg].mean()),
                "fg_ciede2000_p95": float(np.quantile(de[fg], 0.95)),
                "fg_delta_a_star": float(dl[..., 1][fg].mean()),
                "fg_delta_b_star": float(dl[..., 2][fg].mean()),
                "fg_rgb_mae_0_1": float(np.abs(pred_tile[fg] - ref_tile[fg]).mean()),
            })
    summary = {
        "input_path": str(image_path),
        "input_sha256": hashlib.sha256(image_path.read_bytes()).hexdigest(),
        "mask_path": str(mask_path),
        "mask_sha256": hashlib.sha256(mask_path.read_bytes()).hexdigest(),
        "checkpoint_sha256": hashlib.sha256(Path(runner.CHECKPOINT).read_bytes()).hexdigest(),
        "config_sha256": hashlib.sha256(Path(runner.CONFIG).read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256(RUN_SCRIPT.read_bytes()).hexdigest(),
        "python": sys.version,
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "diffusers": diffusers.__version__,
        "transformers": transformers.__version__,
        "vae_dtype": str(dtype),
        "normalization": "(RGB_0_1 - 0.5) / 0.8; decode RGB = clamp(0.8 * decoded + 0.5, 0, 1)",
        "posterior_controls": "mode and sample with fixed torch.Generator seed 42",
        "outputs": results,
        "foreground_metrics_by_view": rows,
        "mean_fg_ciede2000": {
            name: float(np.mean([r["fg_ciede2000"] for r in rows if r["variant"] == name]))
            for name in results
        },
    }
    (output_dir / "vae_roundtrip_metrics.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
