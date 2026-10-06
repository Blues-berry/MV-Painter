#!/usr/bin/env python3
"""Small numeric checks for the E5 dose construction before the GPU pilot."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import torch

script = Path(__file__).with_name("run_e5_residual_dose.py")
spec = importlib.util.spec_from_file_location("e5_dose", script)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

hidden = torch.tensor([[[[3.0, 4.0]]]], dtype=torch.float32)
raw = torch.tensor([[[[0.0, 5.0]]]], dtype=torch.float32)
hidden_norm, raw_norm, requested, delta = module.normalized_delta(hidden, raw, 0.01, torch.float32)
assert hidden_norm == 5.0 and raw_norm == 5.0 and requested == 0.05
assert torch.allclose(delta.norm(), torch.tensor(0.05), atol=1e-7)
assert torch.allclose(delta / hidden_norm, torch.tensor([[[[0.0, 0.01]]]]), atol=1e-7)

hidden16 = hidden.to(torch.float16)
_, _, _, delta16 = module.normalized_delta(hidden16, raw.to(torch.float16), 0.01, torch.float16)
actual = ((hidden16 + delta16).float() - hidden16.float()).norm() / hidden16.float().norm()
assert torch.isfinite(actual) and abs(float(actual) - 0.01) / 0.01 <= 0.05

for bad_hidden, bad_raw, expected in (
    (torch.zeros_like(hidden), raw, "hidden"),
    (hidden, torch.zeros_like(raw), "correction"),
):
    try:
        module.normalized_delta(bad_hidden, bad_raw, 0.01, torch.float32)
    except ValueError as exc:
        assert expected in str(exc)
    else:
        raise AssertionError(f"expected {expected} norm to fail")

print("E5 normalized-dose math checks passed")
