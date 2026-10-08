#!/usr/bin/env python
"""Phase III scientific-validation runner (validation-v3).

Per-object-per-condition code path is a verbatim copy of the frozen
scripts/run_core7_completion_276_20261001.py (protocol
layer-confirmation-strict276-v1, R0 namespace: object_seed = 42 + object_idx,
latent seed 42, unique6 target views [0,15,12,16,13,14], 50 Euler steps,
EulerDiscreteScheduler, metric path geotex.eval_exploration.compute_metrics).

New in v3 (protocol final/round2/scientific_validation_v3/MASTER_PROTOCOL_LOCK.md):
  * condition registry covering experiments A/A3/B/C (see CONDITIONS below)
  * per-object per-condition PNG archival (predictions/<condition>/<object>.png)
  * per-step residual logs persisted (residual_logs/<condition>/<object>.json)
    including requested scale and effective (post-cap) scale per depth group
  * sharded execution for multi-GPU (MVP_SHARD / MVP_NUM_SHARDS)
  * object list parameterized (fresh cohort or dev lists); UIDs recorded

Cone-of-fire rules (MASTER_PROTOCOL_LOCK.md): no schedule selection on the
formal cohort; TRUE-GLOBAL conditions are uncapped causal diagnostics; every
formal run must keep the shared-input integrity abort.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
from omegaconf import OmegaConf
from torchvision.utils import save_image

# cap intra-op threads (multi-shard launches would otherwise thrash 32 cores)
torch.set_num_threads(int(os.environ.get("MVP_NUM_THREADS", "6")))

ROOT = Path("/4T/CXY/MV-Painter")
WORKTREE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "geotex"))
sys.path.insert(0, str(ROOT / "MVPainter"))
# Prefer the isolated diagnostic checkout. Its model/data sources match the
# locked baseline; only explore_contradiction.py adds read-only observations.
sys.path.insert(0, str(WORKTREE_ROOT / "geotex"))
sys.path.insert(0, str(WORKTREE_ROOT / "MVPainter"))
sys.path.insert(0, str(WORKTREE_ROOT))

import geotex.eval_exploration as ee
import geotex.explore_contradiction as exp
from data_utils import collate_batch, prepare_batch
from metrics import compute_edge_mask
from src.utils.train_util import instantiate_from_config

CONFIG = Path("/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml")
CHECKPOINT = ROOT / "mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt"
V3_DIR = ROOT / "final/round2/scientific_validation_v3"
STEPS = 50

# ---------------------------------------------------------------- env
RUN_DIR = Path(os.environ["MVP_RUN_DIR"])
OBJECT_LIST = Path(os.environ["MVP_OBJECT_LIST"])
CONDITION_FILTER = os.environ.get("MVP_CONDITIONS", "")
OBJECT_LIMIT = int(os.environ.get("MVP_OBJECT_LIMIT", "0"))
OBJECT_INDICES = os.environ.get("MVP_OBJECT_INDICES", "")
SHARD = int(os.environ.get("MVP_SHARD", "0"))
NUM_SHARDS = int(os.environ.get("MVP_NUM_SHARDS", "1"))
SAVE_PREDICTED = os.environ.get("MVP_SAVE_PREDICTED", "1") == "1"
SAVE_RESIDUAL = os.environ.get("MVP_SAVE_RESIDUAL", "1") == "1"
RESIDUALS_ONLY = os.environ.get("MVP_RESIDUALS_ONLY", "0") == "1"
A3_SPEC_PATH = Path(os.environ.get(
    "MVP_A3_SPEC", str(V3_DIR / "a3_normalization.json")))

# ---------------------------------------------------------------- constants
LOW = {"deep": 1.25, "middle": 1.25, "shallow": 0.50}
HIGH = {"deep": 2.50, "middle": 2.50, "shallow": 0.75}
LLH_BUDGET = {"deep": 1.675, "middle": 1.675, "shallow": 0.585}  # exact 17/16/17
STAGES = {  # per depth group: (early, middle, late) over 17/16/17 steps
    "llh": {"deep": (1.25, 1.25, 2.50), "middle": (1.25, 1.25, 2.50), "shallow": (0.50, 0.50, 0.75)},
    "lhl": {"deep": (1.25, 2.50, 1.25), "middle": (1.25, 2.50, 1.25), "shallow": (0.50, 0.75, 0.50)},
    "lll": {"deep": (1.25, 1.25, 1.25), "middle": (1.25, 1.25, 1.25), "shallow": (0.50, 0.50, 0.50)},
    "hll": {"deep": (2.50, 1.25, 1.25), "middle": (2.50, 1.25, 1.25), "shallow": (0.75, 0.50, 0.50)},
    "lhh": {"deep": (1.25, 2.50, 2.50), "middle": (1.25, 2.50, 2.50), "shallow": (0.50, 0.75, 0.75)},
}
GEN_SHAPES = {
    "linear": lambda u: u,
    "cosine_bump": lambda u: 0.5 * (1.0 - math.cos(2.0 * math.pi * u)),
    "trapezoid": lambda u: min(3.0 * u, 1.0, 3.0 * (1.0 - u)),
    "gaussian_peak": lambda u: math.exp(-((u - 0.5) ** 2) / (2.0 * (1.0 / 6.0) ** 2)),
}


def stage(progress: float) -> int:
    if progress < 1.0 / 3.0:
        return 0
    if progress < 2.0 / 3.0:
        return 1
    return 2


def make_stage_schedule(spec) -> "callable":
    def fn(progress: float) -> dict:
        s = stage(progress)
        return {g: spec[g][s] for g in ("deep", "middle", "shallow")}
    return fn


def make_window_schedule(layer: str, window: int, base, high_value: float) -> "callable":
    """base dict constant; only `layer` during steps [10*(window-1), 10*window) is high."""
    lo_step = 10 * (window - 1)
    hi_step = 10 * window - 1

    def fn(progress: float) -> dict:
        step_idx = int(round(progress * (STEPS - 1)))
        out = dict(base)
        if lo_step <= step_idx <= hi_step:
            out[layer] = high_value
        return out
    return fn


def make_generic_schedule(shape_name: str, budget_matched: bool) -> "callable":
    shape = GEN_SHAPES[shape_name]

    def fn(progress: float) -> dict:
        u = shape(progress)
        out = {}
        for g in ("deep", "middle", "shallow"):
            lo, hi = LOW[g], HIGH[g]
            s = lo + u * (hi - lo)
            if budget_matched:
                # multiplicative budget match to the LLH per-layer mean budget
                mean_s = sum(lo + shape((k / (STEPS - 1))) * (hi - lo) for k in range(STEPS)) / STEPS
                if mean_s <= 0:
                    raise RuntimeError(f"zero-mean shape {shape_name}; budget matching undefined")
                s = s * (LLH_BUDGET[g] / mean_s)
            out[g] = s
        return out
    return fn


def make_true_global(value: float) -> "callable":
    def fn(progress: float) -> dict:
        return {"deep": value, "middle": value, "shallow": value}
    return fn


def make_boundary_onset_pulse(start_step: int) -> "callable":
    """Native-scale 10-step high pulse at a frozen candidate late-stage onset."""
    def fn(progress: float) -> dict:
        step_idx = int(round(progress * (STEPS - 1)))
        return dict(HIGH if start_step <= step_idx < start_step + 10 else LOW)
    return fn


def load_a3_spec() -> dict:
    if not A3_SPEC_PATH.exists():
        raise RuntimeError(
            f"A3 dose-normalization spec missing: {A3_SPEC_PATH}. "
            "Estimate on probe-24 and freeze a3_normalization.json BEFORE any A3 run."
        )
    spec = json.loads(A3_SPEC_PATH.read_text())
    for layer in ("deep", "middle", "shallow"):
        if layer not in spec.get("high_values", {}):
            raise RuntimeError(f"A3 spec lacks high value for {layer}")
    return spec


A3_SPEC = None  # lazily loaded


def a3_high(layer: str) -> float:
    global A3_SPEC
    if A3_SPEC is None:
        A3_SPEC = load_a3_spec()
    return float(A3_SPEC["high_values"][layer])


# ---------------------------------------------------------------- registry
def build_conditions(include_a3: bool = False) -> dict:
    conds = {}

    def add(name, fn, uncapped=False, adapter=True, spec=None):
        conds[name] = {"fn": fn, "uncapped": uncapped, "adapter": adapter, "spec": spec}

    add("no_adapter", lambda p: 0.0, adapter=False)
    add("native_gfl", lambda p: 1.25, spec={"requested": 1.25})
    add("native_gfh", lambda p: 2.50, spec={"requested": 2.50})
    add("native_gc3", make_stage_schedule(
        {"deep": (1.25, 2.50, 1.25), "middle": (1.25, 2.50, 1.25), "shallow": (1.25, 2.50, 1.25)}))

    # Experiment A: layer x time causal map (native cap semantics)
    add("a_baseline", lambda p: dict(LOW), spec={"base": LOW, "kind": "layer-fixed-low"})
    for layer in ("deep", "middle", "shallow"):
        for w in (1, 2, 3, 4, 5):
            add(f"a_{layer}_W{w}", make_window_schedule(layer, w, LOW, HIGH[layer]),
                spec={"base": LOW, "layer": layer, "window": w, "high": HIGH[layer],
                      "kind": "window-intervention"})

    # Experiment A3: dose-normalized map — registered ONLY when include_a3 is
    # set (i.e., MVP_CONDITIONS names a3_* conditions), which forces the
    # frozen-spec load; the spec must exist and be frozen before any A3 run.
    # The spec decides whether the A3 map runs under native cap semantics or
    # the uncapped injection path (pre-registered in a3_normalization.json).
    if include_a3:
        _ = a3_high("deep")  # force-load the frozen spec before reading flags
        a3_uncapped = bool(A3_SPEC["uncapped"])
        add("a3_baseline", lambda p: dict(LOW), uncapped=a3_uncapped,
            spec={"base": LOW, "kind": "layer-fixed-low", "dose": "a3"})
        for layer in ("deep", "middle", "shallow"):
            for w in (1, 2, 3, 4, 5):
                add(f"a3_{layer}_W{w}", make_window_schedule(layer, w, LOW, a3_high(layer)),
                    uncapped=a3_uncapped,
                    spec={"base": LOW, "layer": layer, "window": w, "high": a3_high(layer),
                          "kind": "window-intervention", "dose": "a3"})

    # Experiment B: budget/cap controls
    for name in ("llh", "lhl", "lll", "hll", "lhh"):
        add(f"layer_{name}", make_stage_schedule(STAGES[name]),
            spec={"stages": STAGES[name], "kind": "three-stage"})
    add("lfm_exact", lambda p: dict(LLH_BUDGET),
        spec={"requested": LLH_BUDGET, "kind": "exact-mean-matched-constant"})
    for v, tag in ((0.80, "0p80"), (1.25, "1p25"), (1.675, "1p675"), (2.50, "2p50")):
        add(f"true_global_{tag}", make_true_global(v), uncapped=True,
            spec={"requested_every_group": v, "cap": "bypassed", "kind": "causal-diagnostic"})

    # Prospective stage-boundary robustness family. Each condition uses the
    # same 10-step native-scale high pulse, anchored at the late-stage onset
    # implied by one frozen candidate partition; this is not an optimum search.
    for partition, start in (("20_60_20", 40), ("30_40_30", 35),
                             ("34_32_34", 33), ("40_20_40", 30)):
        add(f"boundary_late_onset_{partition}", make_boundary_onset_pulse(start),
            spec={"partition_percent": partition.split("_"),
                  "high_pulse_start_step": start, "high_duration_steps": 10,
                  "base": LOW, "high": HIGH,
                  "kind": "fixed-width-boundary-sensitivity-pulse"})

    # Experiment C: generic schedules (frozen shapes; native cap semantics)
    for shape_name in GEN_SHAPES:
        add(f"gen_{shape_name}", make_generic_schedule(shape_name, budget_matched=False),
            spec={"shape": shape_name, "variant": "endpoint-matched",
                  "low": LOW, "high": HIGH})
        add(f"gen_{shape_name}_bm", make_generic_schedule(shape_name, budget_matched=True),
            spec={"shape": shape_name, "variant": "budget-matched",
                  "budget": LLH_BUDGET})
    return conds


_WANTED = [s.strip() for s in CONDITION_FILTER.split(",") if s.strip()] if CONDITION_FILTER else []
CONDITIONS = build_conditions(include_a3=any(s.startswith("a3_") for s in _WANTED))
if CONDITION_FILTER:
    unknown = [s for s in _WANTED if s not in CONDITIONS]
    if unknown:
        raise RuntimeError(f"unknown conditions: {unknown}")
    CONDITIONS = {k: CONDITIONS[k] for k in _WANTED}


# ---------------------------------------------------------------- cap bypass
_ORIGINAL_FORWARD = None


def swap_uncapped() -> None:
    global _ORIGINAL_FORWARD
    from mvpainter.model_unet_geotex import GeoTexResnetWrapper
    if _ORIGINAL_FORWARD is None:
        _ORIGINAL_FORWARD = GeoTexResnetWrapper.forward
    GeoTexResnetWrapper.forward = uncapped_forward


def restore_forward() -> None:
    from mvpainter.model_unet_geotex import GeoTexResnetWrapper
    GeoTexResnetWrapper.forward = _ORIGINAL_FORWARD


def uncapped_forward(self, *args, **kwargs):
    """Forward WITHOUT min(_adapter_scale, _max_scale) cap (precedent
    geotex/explore_cap_ablation.py). Keeps the _skip_correction guard."""
    import torch.nn.functional as F
    from mvpainter.model_unet_geotex import GeoTexResnetWrapper

    hidden_states = self.resnet(*args, **kwargs)
    if GeoTexResnetWrapper._skip_correction:
        return hidden_states
    if self._current_geo_feats is not None:
        geo_feat = self._current_geo_feats.get(self.geo_feat_key)
        if geo_feat is not None:
            if geo_feat.shape[2:] != hidden_states.shape[2:]:
                geo_feat = F.interpolate(geo_feat, size=hidden_states.shape[2:],
                                         mode="bilinear", align_corners=False)
            correction = self.adapter.compute_correction(hidden_states, geo_feat)
            if hasattr(self, "_adapter_scale"):
                correction = correction * self._adapter_scale  # NO cap
            self._last_correction = correction
            self._last_hidden = hidden_states.detach()
            hidden_states = hidden_states + correction
    return hidden_states


# ---------------------------------------------------------------- io helpers
def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


# Capture at import/launch, before model loading or any output work. The old
# end-of-run hash read the live path and could describe a later edited file.
RUNNER_SHA256_AT_START = sha256(Path(__file__).resolve())


def h_tensor(t: torch.Tensor) -> str:
    return hashlib.sha256(t.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def atomic_json(path: Path, payload) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def csv_row(row: dict) -> dict:
    return {k: v for k, v in row.items() if k != "input_hashes"}


def write_condition_csv(rows, condition: str) -> None:
    subset = [csv_row(r) for r in rows if r["condition"] == condition]
    if not subset:
        return
    fields = list(subset[0])
    # shard-suffixed names: multiple shards share RUN_DIR; unsuffixed
    # atomic-replace raced between shards (B1B2 shard0 crash)
    temporary = RUN_DIR / f".{condition}_shard{SHARD}.csv.tmp"
    final = RUN_DIR / f"{condition}_per_object_metrics_shard{SHARD}.csv"
    with temporary.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(subset)
    temporary.replace(final)


def write_combined_csv(rows) -> None:
    if not rows:
        return
    subset = [csv_row(r) for r in rows]
    fields = list(subset[0])
    temporary = RUN_DIR / f".combined_shard{SHARD}.csv.tmp"
    final = RUN_DIR / f"per_object_metrics_shard{SHARD}.csv"
    with temporary.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(subset)
    temporary.replace(final)


def rebuild_csvs_from_ledgers() -> None:
    """Regenerate per-condition and combined CSVs from rows_shard*.json."""
    all_rows = []
    seen = {}
    for shard in range(int(os.environ.get("MVP_NUM_SHARDS", "1"))):
        p = RUN_DIR / f"rows_shard{shard}.json"
        if p.exists():
            for r in json.loads(p.read_text()):
                # cross-shard dedup (shard mappings may differ between runs);
                # identical conditions/seed -> rows are equivalent, keep last
                seen[(r["object_idx"], r["condition"])] = r
    all_rows = list(seen.values())
    if not all_rows:
        return
    conditions = sorted({r["condition"] for r in all_rows})
    for c in conditions:
        subset = [csv_row(r) for r in all_rows if r["condition"] == c]
        if not subset:
            continue
        final = RUN_DIR / f"{c}_per_object_metrics.csv"
        tmp = RUN_DIR / f".{c}_merged.csv.tmp"
        with tmp.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(subset[0]))
            writer.writeheader()
            writer.writerows(subset)
        tmp.replace(final)
    subset = [csv_row(r) for r in all_rows]
    final = RUN_DIR / "per_object_metrics.csv"
    tmp = RUN_DIR / ".combined_merged.csv.tmp"
    with tmp.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(subset[0]))
        writer.writeheader()
        writer.writerows(subset)
    tmp.replace(final)
    print(f"rebuilt CSVs for {len(all_rows)} rows, {len(conditions)} conditions", flush=True)


def condition_scale_trace(fn) -> list:
    """Requested scale trace per step (50 x 3 groups) for the manifest."""
    trace = []
    for k in range(STEPS):
        s = fn(k / (STEPS - 1))
        trace.append({g: float(v) for g, v in (s.items() if isinstance(s, dict) else
                                               zip(("deep", "middle", "shallow"), (s, s, s)))})
    return trace


def protocol_manifest() -> dict:
    configured_roots = list(OmegaConf.load(CONFIG).data.params.validation.params.root_dir_list)
    data_root_override = os.environ.get("MVP_DATA_ROOT")
    effective_roots = ([str(Path(data_root_override).resolve())] if data_root_override
                       else [str(Path(p).resolve()) for p in configured_roots])
    code_sources = {
        "runner": Path(__file__).resolve(),
        "generation_logic": WORKTREE_ROOT / "geotex/explore_contradiction.py",
        "adapter_wrapper": WORKTREE_ROOT / "MVPainter/mvpainter/model_unet_geotex.py",
        "data_utils": WORKTREE_ROOT / "geotex/data_utils.py",
        "metric_implementation": WORKTREE_ROOT / "geotex/eval_exploration.py",
        "train_util_dataset_factory": WORKTREE_ROOT / "MVPainter/src/utils/train_util.py",
        "metric_package": WORKTREE_ROOT / "geotex/metrics/__init__.py",
        "metric_image_functions": WORKTREE_ROOT / "geotex/metrics/image_metrics.py",
        "metric_mask_functions": WORKTREE_ROOT / "geotex/metrics/mask_ops.py",
        "metric_region_functions": WORKTREE_ROOT / "geotex/metrics/region_metrics.py",
        "metric_crop_functions": WORKTREE_ROOT / "geotex/metrics/crop_ops.py",
    }
    return {
        "protocol": "layer-confirmation-strict276-v1 (verbatim per-object code path)",
        "phase": "scientific-validation-v3",
        "task": "Phase III causal evidence closure",
        "realization": "realization0_namespace (object_seed = 42 + object_idx)",
        "reference_seed_policy": (
            "object_seed = 42 + object_idx for python random / numpy / torch "
            "before collate_batch; torch.manual_seed(42) before initial latent and again "
            "immediately before generation (VAE latent sample consumes torch RNG)"
        ),
        "conditions": sorted(CONDITIONS),
        "condition_specs": {
            k: {"spec": v["spec"], "uncapped": v["uncapped"], "adapter": v["adapter"],
                "scale_trace_requested": condition_scale_trace(v["fn"])}
            for k, v in sorted(CONDITIONS.items())
        },
        "scale_semantics": (
            "effective = min(requested, cap deep 3.0 / middle 3.5 / shallow 0.8); "
            "conditions flagged uncapped bypass the cap (causal diagnostics only)"
        ),
        "checkpoint": str(CHECKPOINT),
        "checkpoint_sha256": sha256(CHECKPOINT),
        "config": str(CONFIG),
        "config_sha256": sha256(CONFIG),
        "data_root_override": str(Path(data_root_override).resolve()) if data_root_override else None,
        "effective_data_roots": effective_roots,
        "code_source_sha256": {k: {"path": str(v), "sha256": sha256(v)}
                                for k, v in code_sources.items()},
        "object_list": str(OBJECT_LIST),
        "object_list_sha256": sha256(OBJECT_LIST),
        "target_view_mode": "unique6",
        "target_views": [0, 15, 12, 16, 13, 14],
        "resolution": [256, 256],
        "steps": STEPS,
        "sampler": "EulerDiscreteScheduler",
        "latent_seed": 42,
        "stage_partition": "step/49; early<1/3, middle<2/3 => 17/16/17",
        "window_partition": "W1 steps 0-9, W2 10-19, W3 20-29, W4 30-39, W5 40-49",
        "a3_spec": str(A3_SPEC_PATH),
        "a3_spec_sha256": sha256(A3_SPEC_PATH) if A3_SPEC_PATH.exists() else None,
        "metric_path": "geotex.eval_exploration.compute_metrics",
        "shard": SHARD,
        "num_shards": NUM_SHARDS,
        "runner_script_sha256": RUNNER_SHA256_AT_START,
        "residuals_only": RESIDUALS_ONLY,
        "observer_instrumentation": {
            "feature": "pre-adapter ResNet output, captured by a read-only forward hook",
            "correction_to_feature_rms": "RMS(actual injected correction) / RMS(pre-adapter feature)",
            "anomaly_fraction_threshold": "fraction of correction elements with abs(value) > 0.25 * feature RMS",
            "observer_only": True,
        },
    }


# ---------------------------------------------------------------- main
def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "predictions").mkdir(exist_ok=True)
    (RUN_DIR / "residual_logs").mkdir(exist_ok=True)

    if os.environ.get("MVP_REBUILD_CSVS") == "1":
        rebuild_csvs_from_ledgers()
        return

    rows_path = RUN_DIR / f"rows_shard{SHARD}.json"
    rows = json.loads(rows_path.read_text()) if rows_path.exists() else []
    if RESIDUALS_ONLY:
        completed = {
            (p.stem, p.parent.name)
            for p in (RUN_DIR / "residual_logs").glob("*/*.json")
        }
    else:
        completed = {(int(r["object_idx"]), r["condition"]) for r in rows}

    device = torch.device(os.environ.get("MVP_DEVICE", "cuda:0"))
    dtype = torch.float16
    model = ee.load_model(str(CONFIG), str(CHECKPOINT), device)
    config = OmegaConf.load(CONFIG)
    validation = config.data.params.validation
    validation.params.target_view_mode = "unique6"
    validation.params.object_list_file = str(OBJECT_LIST.resolve())
    data_root = os.environ.get("MVP_DATA_ROOT")
    if data_root:
        validation.params.root_dir_list = [str(Path(data_root).resolve())]
    dataset = instantiate_from_config(validation)
    lpips_fn = None if RESIDUALS_ONLY else ee.get_lpips_fn(device)

    with OBJECT_LIST.open() as f:
        uids = [line.strip() for line in f if line.strip()]
    object_ids = list(uids)
    if len(object_ids) != len(dataset):
        raise RuntimeError(
            f"object list length {len(object_ids)} != dataset length {len(dataset)}")

    if OBJECT_INDICES:
        object_range = [int(x) for x in OBJECT_INDICES.split(",") if x.strip()]
    elif OBJECT_LIMIT > 0:
        object_range = list(range(min(OBJECT_LIMIT, len(object_ids))))
    else:
        object_range = list(range(len(object_ids)))
    object_range = [i for i in object_range if i % NUM_SHARDS == SHARD]

    expected_total = len(object_range) * len(CONDITIONS)
    print(
        f"validation-v3 run: device={device} shard={SHARD}/{NUM_SHARDS} "
        f"conditions={sorted(CONDITIONS)} objects={len(object_range)} "
        f"done={len(completed)}/{expected_total}",
        flush=True,
    )

    for obj_idx in object_range:
        object_id = object_ids[obj_idx]
        completion_key = object_id if RESIDUALS_ONLY else obj_idx
        pending = [c for c in sorted(CONDITIONS) if (completion_key, c) not in completed]
        if not pending:
            continue
        object_seed = 42 + obj_idx
        reference_hashes = None

        for condition in pending:
            cfg = CONDITIONS[condition]
            # --- verbatim per-object block from the frozen confirmation runner ---
            random.seed(object_seed)
            np.random.seed(object_seed)
            torch.manual_seed(object_seed)
            batch = collate_batch(dataset, obj_idx, device)
            _, target, _, real_depth, geo_input, mask = prepare_batch(batch, model.img_size, device)
            geo_clean = torch.nan_to_num(geo_input.float().clamp(0, 1), nan=0.0, posinf=1.0, neginf=0.0)
            geo_feats = model.geo_encoder(geo_clean)
            edge = compute_edge_mask(real_depth.float(), threshold=0.1)

            torch.manual_seed(42)
            latent_h, latent_w = model.img_size * 3 // 8, model.img_size * 2 // 8
            init_latents = torch.randn(1, 4, latent_h, latent_w, device=device, dtype=dtype)
            torch.manual_seed(42)
            started = time.time()
            geo_feats_arg = None if not cfg["adapter"] else geo_feats
            residual_log = {}
            swapped = False
            if cfg["uncapped"]:
                swap_uncapped()
                swapped = True
            try:
                pred = exp.generate_with_schedule(
                    model, batch, device, dtype, geo_feats_arg, cfg["fn"], STEPS,
                    init_latents.clone(), residual_log,
                )
            finally:
                if swapped:
                    restore_forward()
            metrics = ({} if RESIDUALS_ONLY else
                       ee.compute_metrics(pred, target, mask, edge, lpips_fn, device))
            # -------------------------------------------------------------------
            integrity = {
                "cond": h_tensor(batch["cond_imgs"]),
                "target": h_tensor(batch["target_imgs"]),
                "normal": h_tensor(batch["depth_imgs"]),
                "depth": h_tensor(batch["real_depth_imgs"]),
                "global_embeds": h_tensor(batch["global_embeds"]),
                "init_latent": h_tensor(init_latents),
            }
            if reference_hashes is None:
                reference_hashes = integrity
            elif integrity != reference_hashes:
                raise RuntimeError(
                    f"shared-input integrity FAILURE at object_idx={obj_idx} "
                    f"({object_id}) condition={condition}"
                )

            if SAVE_RESIDUAL and residual_log:
                rdir = RUN_DIR / "residual_logs" / condition
                rdir.mkdir(parents=True, exist_ok=True)
                atomic_json(rdir / f"{object_id}.json", residual_log)
            if RESIDUALS_ONLY:
                if not residual_log:
                    raise RuntimeError(f"no residual log for {object_id}/{condition}")
                completed.add((completion_key, condition))
            if SAVE_PREDICTED:
                pdir = RUN_DIR / "predictions" / condition
                pdir.mkdir(parents=True, exist_ok=True)
                save_image(pred, pdir / f"{object_id}.png")

            if not RESIDUALS_ONLY:
                row = {
                    "object": object_id,
                    "object_uid": object_id,
                    "object_idx": obj_idx,
                    "condition": condition,
                    "uncapped": cfg["uncapped"],
                    "seed_base": 42,
                    "elapsed_seconds": time.time() - started,
                    **{k: float(v) for k, v in metrics.items()},
                    "input_hashes": integrity,
                }
                rows.append(row)
                rows.sort(key=lambda item: (int(item["object_idx"]), item["condition"]))
                atomic_json(rows_path, rows)
                # CSV rewrite is O(total rows): throttle to every 16 completions
                # (rows.json is the per-row resume ledger; MVP_REBUILD_CSVS=1
                # regenerates CSVs from ledgers at any time)
                if len(rows) % 16 == 0 or len(rows) <= 4:
                    write_condition_csv(rows, condition)
                    write_combined_csv(rows)
            del pred, batch, target, real_depth, geo_input, mask, geo_feats, edge, init_latents
            torch.cuda.empty_cache()
        done = sum(1 for o in object_range for c in CONDITIONS
                   if (int(o), c) in {(int(r["object_idx"]), r["condition"]) for r in rows})
        print(f"[{done}/{expected_total}] {object_id} device={device}", flush=True)

    atomic_json(
        RUN_DIR / f"run_manifest_shard{SHARD}.json",
        {**protocol_manifest(), "status": "complete", "row_count": len(rows)},
    )
    print(f"saved {len(rows)} rows (conditions={sorted(CONDITIONS)})", flush=True)


if __name__ == "__main__":
    main()
