# Tested runtime snapshot

- Python: `3.13.5`.
- Platform: `Linux-6.14.0-37-generic-x86_64-with-glibc2.31`.
- CUDA build: `12.8`.
- GPUs: `NVIDIA GeForce RTX 5090`, `NVIDIA GeForce RTX 5090`.

| Package | Version |
|---|---|
| `diffusers` | `0.37.0` |
| `einops` | `0.7.0` |
| `kornia` | `0.8.2` |
| `lpips` | `0.1.4` |
| `numpy` | `2.2.6` |
| `omegaconf` | `2.3.0` |
| `opencv-python` | `4.13.0.92` |
| `pandas` | `2.2.3` |
| `pytorch-lightning` | `2.6.5` |
| `scikit-image` | `0.26.0` |
| `scipy` | `1.15.0` |
| `torch` | `2.7.1+cu128` |
| `torchvision` | `0.22.1+cu128` |
| `transformers` | `4.57.6` |

The original runtime JSON remains in the local source worktree. The GPU generation runner requires separately supplied source renders, model weights, and a compatible CUDA environment; the bundled CSV analysis can run without those assets.
