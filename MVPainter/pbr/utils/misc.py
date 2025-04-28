import os
from packaging import version
import numpy as np


def get_rank():
    # SLURM_PROCID can be set even if SLURM is not managing the multiprocessing,
    # therefore LOCAL_RANK needs to be checked first
    rank_keys = ("RANK", "LOCAL_RANK", "SLURM_PROCID", "JSM_NAMESPACE_RANK")
    for key in rank_keys:
        rank = os.environ.get(key)
        if rank is not None:
            return int(rank)
    return 0

def parse_version(ver):
    return version.parse(ver)

def rgb_to_srgb(f: np.ndarray):
    # f is loaded from .exr
    # output is NOT clipped to [0, 1]
    assert len(f.shape) == 3, f.shape
    assert f.shape[2] == 3, f.shape
    f = np.where(f > 0.0031308, np.power(np.maximum(f, 0.0031308), 1.0 / 2.4) * 1.055 - 0.055, 12.92 * f)
    return f

def srgb_to_rgb(f: np.ndarray) -> np.ndarray:
    assert f.shape[-1] == 3
    f = np.where(f <= 0.04045, f / 12.92, np.power((np.maximum(f, 0.04045) + 0.055) / 1.055, 2.4))
    return f
