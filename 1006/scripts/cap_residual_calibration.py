"""Development candidate: joint-mosaic residual calibration within native caps.

No model source is changed. One scalar is shared by the complete object mosaic
at each wrapper/step; this is not a spatial consistency constraint or equal dose.
"""
from __future__ import annotations

import math
from types import MethodType

GROUPS = ("deep", "middle", "shallow")
MULTIPLIERS = (0.75, 1.0, 1.25)


def scale_for_target(hidden_norm, raw_norm, target_ratio, cap):
    values = (hidden_norm, raw_norm, target_ratio, cap)
    if any(not math.isfinite(x) or x < 0 for x in values):
        raise ValueError("norms, target and cap must be finite and nonnegative")
    if hidden_norm == 0 or raw_norm == 0:
        return 0.0, 0.0, "zero_norm"
    requested = target_ratio * hidden_norm / raw_norm
    applied = min(requested, cap)
    return requested, applied, "saturated" if requested > cap else "unsaturated"


def temporal_factor(step):
    if not 0 <= step < 50:
        raise ValueError("expected a frozen 50-step trajectory")
    # Native C3 uses progress=step/49: windows contain 17/16/17 steps.
    return (2.5 if 17 <= step < 33 else 1.25) / 1.65


def install_hooks(model, wrapper_type, state, mode, references=None, multiplier=1.0):
    """Observe raw corrections once, or replace only the target-read injection.

    The original adapter calculation is called once. Reference-write calls and
    observer/no-op outputs are returned verbatim. Removal restores methods even
    if generation fails. Controller combinations are deliberately unsupported.
    """
    import torch

    if mode not in {"observe", "calibrated", "pooled", "static", "fixed"}:
        raise ValueError(f"unsupported mode: {mode}")
    if multiplier not in MULTIPLIERS:
        raise ValueError("multiplier outside the frozen development grid")
    handles, restorations = [], []
    wrappers = [m for m in model.pipeline.unet.modules() if isinstance(m, wrapper_type)]
    if not wrappers or {m.depth_group for m in wrappers} != set(GROUPS):
        raise RuntimeError("expected all three native additive residual groups")
    for wrapper in wrappers:
        if wrapper._correction_controller is not None:
            raise RuntimeError("existing correction controller must be disabled")
        adapter = wrapper.adapter
        original = adapter.compute_correction
        had_instance_method = "compute_correction" in adapter.__dict__
        capture = {}

        def observe_raw(self, hidden, geo, original=original, capture=capture):
            raw = original(hidden, geo)
            capture.update(hidden=hidden, raw=raw)
            return raw

        adapter.compute_correction = MethodType(observe_raw, adapter)
        restorations.append((adapter, original, had_instance_method))

        def apply(wrapper, inputs, output, capture=capture):
            identity = {"step": state["step"], "group": wrapper.depth_group,
                        "adapter_idx": int(wrapper.adapter_idx)}
            if wrapper_type._skip_correction:
                state["traces"].append({**identity, "status": "reference_write_unchanged"})
                capture.clear()
                return output
            if "raw" not in capture:
                raise RuntimeError("target-read wrapper has no captured raw correction")
            hidden, raw = capture.pop("hidden"), capture.pop("raw")
            hn = float(hidden.detach().float().norm().item())
            rn = float(raw.detach().float().norm().item())
            if not math.isfinite(hn) or not math.isfinite(rn):
                raise RuntimeError("nonfinite hidden or raw correction")
            cap = float(wrapper._max_scale)
            native = min(float(wrapper._adapter_scale), cap)
            record = {**identity, "hidden_norm": hn, "raw_norm": rn,
                      "raw_over_hidden": rn / hn if hn else None,
                      "native_scale": native, "cap": cap,
                      "dtype": str(output.dtype), "mosaic_shape": list(hidden.shape)}
            changed = output
            if mode == "observe":
                record.update(status="observed_unchanged", applied_scale=native)
            else:
                group = wrapper.depth_group
                q = float(references["pooled"] if mode == "pooled" else references[group])
                target = multiplier * q * (1.0 if mode == "static" else temporal_factor(state["step"]))
                requested, applied, status = scale_for_target(hn, rn, target, cap)
                if mode == "fixed":
                    applied = min(float(references["fixed_scales"][group][str(state["step"])]), cap)
                    requested, status = applied, "fixed_scale"
                correction = raw * applied
                changed = hidden + correction
                wrapper._last_correction = correction
                realized = float((changed.detach().float() - hidden.detach().float()).norm().item())
                bounded_target = applied * rn
                record.update(status=status, requested_scale=requested, applied_scale=applied,
                              requested_target_ratio=target,
                              realized_ratio=realized / hn if hn else 0.0,
                              target_gap_ratio=max(0.0, target - realized / hn) if hn else target,
                              relative_rounding_error=abs(realized - bounded_target) / bounded_target
                              if bounded_target else 0.0)
            state["traces"].append(record)
            return changed

        handles.append(wrapper.register_forward_hook(apply))

    def remove():
        for handle in handles:
            handle.remove()
        for adapter, original, had_instance_method in restorations:
            if had_instance_method:
                adapter.compute_correction = original
            else:
                del adapter.compute_correction

    return remove
