"""Validated texture diagnostics and GT-relative/reference fidelity metrics.

Images are RGB sRGB arrays in ``[0, 1]``. Variation diagnostics are measured
inside an optionally eroded foreground mask; this prevents background noise
and immediate silhouette pixels from dominating texture statistics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from skimage.color import deltaE_ciede2000, rgb2lab

try:
    from .round2_stats import symmetric_log_error
except ImportError:  # direct ``python geotex/round2_texture.py`` execution
    from round2_stats import symmetric_log_error


def _validate_rgb(image: np.ndarray, name: str) -> np.ndarray:
    image = np.asarray(image, dtype=np.float32)
    if image.ndim != 3 or image.shape[-1] != 3:
        raise ValueError(f"{name} must have shape HxWx3")
    if not np.all(np.isfinite(image)):
        raise ValueError(f"{name} contains NaN or Inf")
    if np.any(image < 0) or np.any(image > 1):
        raise ValueError(f"{name} must be in [0, 1] sRGB")
    return image


def _validated_mask(mask: np.ndarray, shape: tuple[int, int], erosion_radius: int = 1) -> np.ndarray:
    mask = np.asarray(mask)
    if mask.shape != shape:
        raise ValueError(f"mask shape {mask.shape} does not match image {shape}")
    if not np.all(np.isfinite(mask)):
        raise ValueError("mask contains NaN or Inf")
    mask = mask > 0.5
    if erosion_radius < 0:
        raise ValueError("erosion_radius must be non-negative")
    if erosion_radius:
        size = 2 * erosion_radius + 1
        mask = cv2.erode(mask.astype(np.uint8), np.ones((size, size), np.uint8)) > 0
    return mask


def _require_nonempty(mask: np.ndarray) -> None:
    if not np.any(mask):
        raise ValueError("foreground mask is empty after validation/erosion")


def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    """Convert validated sRGB values to linear RGB."""
    rgb = _validate_rgb(rgb, "rgb")
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(rgb: np.ndarray) -> np.ndarray:
    """Convert linear RGB values in [0, 1] to sRGB."""
    rgb = np.asarray(rgb, dtype=np.float32)
    if np.any(~np.isfinite(rgb)) or np.any(rgb < 0) or np.any(rgb > 1):
        raise ValueError("linear RGB must be finite and in [0, 1]")
    return np.where(rgb <= 0.0031308, 12.92 * rgb, 1.055 * rgb ** (1 / 2.4) - 0.055)


def variation_diagnostics(
    image: np.ndarray, mask: np.ndarray | None = None, *, erosion_radius: int = 1
) -> dict[str, float]:
    """Compute Laplacian variance, RGB std, and gradient magnitude."""
    image = _validate_rgb(image, "image")
    valid = (
        _validated_mask(mask, image.shape[:2], erosion_radius)
        if mask is not None
        else np.ones(image.shape[:2], dtype=bool)
    )
    if not np.any(valid):
        return {"laplacian_variance": float("nan"), "rgb_std": float("nan"), "gradient_magnitude": float("nan")}
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_32F, ksize=3)
    gradient_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gradient_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    gradient = np.hypot(gradient_x, gradient_y)
    return {
        "laplacian_variance": float(np.var(laplacian[valid])),
        "rgb_std": float(np.std(image[valid], axis=0).mean()),
        "gradient_magnitude": float(np.mean(gradient[valid])),
    }


def _validated_pair(pred: np.ndarray, gt: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    pred = _validate_rgb(pred, "pred")
    gt = _validate_rgb(gt, "gt")
    if pred.shape != gt.shape:
        raise ValueError(f"pred and gt shapes differ: {pred.shape} vs {gt.shape}")
    return pred, gt


def masked_psnr(
    pred: np.ndarray, gt: np.ndarray, mask: np.ndarray, *, erosion_radius: int = 1
) -> float:
    pred, gt = _validated_pair(pred, gt)
    valid = _validated_mask(mask, pred.shape[:2], erosion_radius)
    if not np.any(valid):
        return float("nan")
    mse = float(np.mean((pred[valid] - gt[valid]) ** 2))
    return 100.0 if mse <= 1e-12 else float(10 * np.log10(1.0 / mse))


def masked_ciede2000(
    pred: np.ndarray, gt: np.ndarray, mask: np.ndarray, *, erosion_radius: int = 1
) -> float:
    """Mean CIEDE2000 after sRGB-to-Lab conversion over the eroded mask."""
    pred, gt = _validated_pair(pred, gt)
    valid = _validated_mask(mask, pred.shape[:2], erosion_radius)
    if not np.any(valid):
        return float("nan")
    return float(deltaE_ciede2000(rgb2lab(pred), rgb2lab(gt))[valid].mean())


def _torch_masked_inputs(pred, gt, mask, erosion_radius):
    import torch

    valid = _validated_mask(mask, pred.shape[:2], erosion_radius)
    if not np.any(valid):
        return None
    p = torch.from_numpy(pred).permute(2, 0, 1).unsqueeze(0).float() * 2 - 1
    t = torch.from_numpy(gt).permute(2, 0, 1).unsqueeze(0).float() * 2 - 1
    m = torch.from_numpy(valid.astype(np.float32)).unsqueeze(0).unsqueeze(0)
    return p * m, t * m


def masked_lpips(pred, gt, mask, *, model=None, erosion_radius=1) -> float:
    """Compute masked LPIPS using a supplied model or optional Alex model."""
    pred, gt = _validated_pair(pred, gt)
    if model is None:
        try:
            import lpips
        except ImportError:
            return float("nan")
        model = lpips.LPIPS(net="alex").eval()
    p, t = _torch_masked_inputs(pred, gt, mask, erosion_radius)
    if p is None:
        return float("nan")
    import torch

    with torch.no_grad():
        value = model(p, t)
    return float(value.detach().cpu().mean())


def masked_dists(pred, gt, mask, *, model=None, erosion_radius=1) -> float:
    """Compute masked DISTS when the optional DISTS package is available."""
    pred, gt = _validated_pair(pred, gt)
    if model is None:
        try:
            from DISTS_pytorch import DISTS
        except ImportError:
            return float("nan")
        model = DISTS().eval()
    p, t = _torch_masked_inputs(pred, gt, mask, erosion_radius)
    if p is None:
        return float("nan")
    import torch

    with torch.no_grad():
        value = model(p, t)
    return float(value.detach().cpu().mean())


def reference_fidelity_metrics(
    pred, gt, mask, *, lpips_model=None, dists_model=None, erosion_radius=1
) -> dict[str, float]:
    """Return the four reference-based metrics with one shared valid mask."""
    return {
        "masked_lpips": masked_lpips(
            pred, gt, mask, model=lpips_model, erosion_radius=erosion_radius
        ),
        "masked_dists": masked_dists(
            pred, gt, mask, model=dists_model, erosion_radius=erosion_radius
        ),
        "ciede2000": masked_ciede2000(pred, gt, mask, erosion_radius=erosion_radius),
        "masked_psnr": masked_psnr(pred, gt, mask, erosion_radius=erosion_radius),
    }


def texture_stat_errors(pred_stats, gt_stats, epsilon=1e-6):
    """Return variation values plus GT-relative symmetric log errors."""
    names = ("laplacian_variance", "rgb_std", "gradient_magnitude")
    missing = [name for name in names if name not in pred_stats or name not in gt_stats]
    if missing:
        raise KeyError(f"missing texture statistics: {missing}")
    pred = {name: float(pred_stats[name]) for name in names}
    gt = {name: float(gt_stats[name]) for name in names}
    for label, values in (("pred", pred), ("gt", gt)):
        if any(not np.isfinite(value) or value < 0 for value in values.values()):
            raise ValueError(f"{label} texture statistics must be finite and non-negative")
    return {
        "variation": pred,
        "symmetric_log_error": {
            name: float(symmetric_log_error(pred[name], gt[name], epsilon)) for name in names
        },
        "epsilon": float(epsilon),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pred", type=Path, required=True, help="JSON object of texture statistics")
    parser.add_argument("--gt", type=Path, required=True, help="JSON object of GT statistics")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--epsilon", type=float, default=1e-6)
    args = parser.parse_args()
    result = texture_stat_errors(
        json.loads(args.pred.read_text()), json.loads(args.gt.read_text()), args.epsilon
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
