"""Runtime checks shared by GPU-backed evaluation entry points."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _device_nodes() -> list[str]:
    try:
        return sorted(str(path) for path in Path("/dev").glob("nvidia*"))
    except OSError:
        return []


def _gpu_device_nodes(nodes: list[str]) -> list[str]:
    return [
        node for node in nodes
        if Path(node).name.startswith("nvidia")
        and Path(node).name[len("nvidia"):].isdigit()
    ]


def cuda_report() -> dict[str, object]:
    """Return the CUDA visibility facts needed to diagnose container failures."""
    import torch

    nodes = _device_nodes()
    return {
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "cuda_available": bool(torch.cuda.is_available()),
        "device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "device_nodes": nodes,
        "gpu_device_nodes": _gpu_device_nodes(nodes),
    }


def require_cuda(requested: str, purpose: str):
    """Validate an explicitly requested CUDA device without silently falling back.

    GPU inference is intentionally fail-fast.  A CPU fallback would produce a
    different execution path and could be mistaken for a valid model result.
    """
    import torch

    device = torch.device(requested)
    if device.type != "cuda":
        raise RuntimeError(
            f"{purpose} requires an explicit CUDA device, got {requested!r}; "
            "CPU mode is not a substitute for this inference run"
        )

    report = cuda_report()
    if not report["cuda_available"]:
        raise RuntimeError(
            f"{purpose} requested {device}, but PyTorch reports CUDA unavailable. "
            f"Runtime probe: {report}. This indicates that the container/sandbox "
            "has no NVIDIA device mapping (for example, missing /dev/nvidia*), "
            "not that the model ran out of memory. Run the job in a GPU-enabled "
            "container/host with the NVIDIA devices mapped; do not use a CPU "
            "fallback for formal inference."
        )

    count = int(report["device_count"])
    if device.index is not None and device.index >= count:
        raise RuntimeError(
            f"{purpose} requested {device}, but only {count} CUDA device(s) are "
            f"visible after CUDA_VISIBLE_DEVICES={report['cuda_visible_devices']!r}"
        )
    return device
