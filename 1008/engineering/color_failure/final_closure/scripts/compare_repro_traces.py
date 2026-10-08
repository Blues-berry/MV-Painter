#!/usr/bin/env python3
"""Compare isolated Fresh-C traces and immutable archived PNG/metric rows."""
from __future__ import annotations

import csv
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REPRO = ROOT / "repro"
ARCHIVE = Path("/4T/CXY/MV-Painter/1006/data/fresh_c/runs/c3_confirmation")
RUNS = {
    "py313_repeat1": REPRO / "python313_trace_repeat1",
    "py313_repeat2": REPRO / "python313_trace_repeat2",
    "py310": REPRO / "python310_trace",
}
OBJECTS = [
    ("freshc_panel_01", "c76ac44df995482185077da81939b306"),
    ("freshc_panel_03", "ca887928bb664bcba121219f0af41293"),
    ("freshc_panel_20", "06fa4974f8cd4d4ea792e98fa1521457"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_trace(run: str, uid: str) -> dict:
    path = RUNS[run] / "traces" / uid / "native_gfl.pt"
    return torch.load(path, map_location="cpu", weights_only=False)


def compare_values(a, b, path: str, rows: list[dict]) -> None:
    if torch.is_tensor(a) and torch.is_tensor(b):
        aa, bb = a.detach().cpu().contiguous(), b.detach().cpu().contiguous()
        if aa.shape != bb.shape:
            rows.append({"tensor": path, "shape_a": str(tuple(aa.shape)),
                         "shape_b": str(tuple(bb.shape)), "dtype_a": str(aa.dtype),
                         "dtype_b": str(bb.dtype), "exact": False, "values_equal": False,
                         "max_abs": "", "rmse": "", "relative_l2": "",
                         "changed_fraction": ""})
            return
        if aa.numel() == 0:
            return
        diff = aa.double() - bb.double()
        absdiff = diff.abs()
        base_norm = float(aa.double().norm())
        rows.append({
            "tensor": path,
            "shape_a": str(tuple(aa.shape)),
            "shape_b": str(tuple(bb.shape)),
            "dtype_a": str(aa.dtype),
            "dtype_b": str(bb.dtype),
            "exact": bool(aa.dtype == bb.dtype and torch.equal(aa, bb)),
            "values_equal": bool(torch.equal(aa.double(), bb.double())),
            "max_abs": float(absdiff.max()),
            "rmse": float(torch.mean(diff.square()).sqrt()),
            "relative_l2": float(diff.norm()) / max(base_norm, 1e-30),
            "changed_fraction": float((aa != bb).float().mean()),
        })
    elif isinstance(a, dict) and isinstance(b, dict):
        keys = sorted(set(a) | set(b), key=str)
        for key in keys:
            if key not in a or key not in b:
                rows.append({"tensor": f"{path}.{key}", "shape_a": "missing" if key not in a else "present",
                             "shape_b": "missing" if key not in b else "present",
                             "dtype_a": "", "dtype_b": "", "exact": False,
                             "values_equal": False,
                             "max_abs": "", "rmse": "", "relative_l2": "",
                             "changed_fraction": ""})
            else:
                compare_values(a[key], b[key], f"{path}.{key}", rows)
    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            rows.append({"tensor": path, "shape_a": str(len(a)), "shape_b": str(len(b)),
                         "dtype_a": type(a).__name__, "dtype_b": type(b).__name__,
                         "exact": False, "values_equal": False,
                         "max_abs": "", "rmse": "",
                         "relative_l2": "", "changed_fraction": ""})
        else:
            for i, (av, bv) in enumerate(zip(a, b)):
                compare_values(av, bv, f"{path}[{i}]", rows)
    else:
        exact = type(a) is type(b) and a == b
        if not exact:
            rows.append({"tensor": path, "shape_a": "", "shape_b": "",
                         "dtype_a": type(a).__name__, "dtype_b": type(b).__name__,
                         "exact": False, "values_equal": False,
                         "max_abs": "", "rmse": "",
                         "relative_l2": "", "changed_fraction": ""})


def compare_trace_pair(label: str, left_name: str, right_name: str, uid: str) -> list[dict]:
    left, right = load_trace(left_name, uid), load_trace(right_name, uid)
    rows: list[dict] = []
    compare_values(left["tensors"], right["tensors"], "tensors", rows)
    left_scheduler = left["metadata"]["scheduler"]
    right_scheduler = right["metadata"]["scheduler"]
    if label == "py313_repeat1_vs_repeat2":
        left_scheduler = copy.deepcopy(left_scheduler)
        right_scheduler = copy.deepcopy(right_scheduler)
        for scheduler in (left_scheduler, right_scheduler):
            config = scheduler.get("config", {})
            if isinstance(config.get("_use_default_values"), list):
                config["_use_default_values"] = sorted(config["_use_default_values"])
    compare_values(left_scheduler, right_scheduler,
                   "scheduler", rows)
    for field in ("scheduler_config_source", "unet_calls", "scheduler_calls", "weight_dtype"):
        compare_values(left["metadata"].get(field), right["metadata"].get(field),
                       f"metadata.{field}", rows)
    for row in rows:
        row["comparison"] = label
        row["uid"] = uid
    return rows


def image_metrics(path_a: Path, path_b: Path) -> dict:
    a = np.asarray(Image.open(path_a).convert("RGB"), dtype=np.int16)
    b = np.asarray(Image.open(path_b).convert("RGB"), dtype=np.int16)
    if a.shape != b.shape:
        return {"shape_a": str(a.shape), "shape_b": str(b.shape), "byte_identical": False}
    d = a.astype(np.float32) - b.astype(np.float32)
    mse = float(np.mean(d * d))
    return {
        "shape_a": str(a.shape), "shape_b": str(b.shape),
        "byte_identical": path_a.read_bytes() == path_b.read_bytes(),
        "pixel_identical": bool(np.array_equal(a, b)),
        "mae_0_255": float(np.abs(d).mean()),
        "rmse_0_255": float(np.sqrt(mse)),
        "max_abs_0_255": int(np.abs(d).max()),
        "changed_pixel_fraction": float(np.any(d != 0, axis=2).mean()),
        "pixel_psnr_db": float("inf") if mse == 0 else float(10 * np.log10(255.0**2 / mse)),
        "sha_a": sha256(path_a), "sha_b": sha256(path_b),
    }


def load_rows(path: Path) -> dict:
    data = json.loads(path.read_text())
    return {(r["object_uid"], r["condition"]): r for r in data}


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    tensor_rows = []
    output_rows = []
    native_rows = {name: load_rows(root / "run/rows_shard0.json")
                   for name, root in RUNS.items()}
    old_rows = load_rows(ARCHIVE / "rows_shard0.json")
    observer_rows = {
        (row["uid"], row["condition"]): row
        for row in csv.DictReader((ROOT.parent / "logs/FRESHC_OBSERVER_OUTPUT_IDENTITY.csv").open())
    }

    for sample_id, uid in OBJECTS:
        for label, left, right in (("py313_repeat1_vs_repeat2", "py313_repeat1", "py313_repeat2"),
                                   ("py313_vs_py310", "py313_repeat1", "py310")):
            tensor_rows.extend(compare_trace_pair(label, left, right, uid))

        archived_png = ARCHIVE / "predictions/native_gfl" / f"{uid}.png"
        py313_png = RUNS["py313_repeat1"] / "run/predictions/native_gfl" / f"{uid}.png"
        py313b_png = RUNS["py313_repeat2"] / "run/predictions/native_gfl" / f"{uid}.png"
        py310_png = RUNS["py310"] / "run/predictions/native_gfl" / f"{uid}.png"
        for label, left, right, tag_a, tag_b in (
            ("archive_vs_py313", archived_png, py313_png, "archive", "py313"),
            ("py313_repeat1_vs_repeat2", py313_png, py313b_png, "py313_repeat1", "py313_repeat2"),
            ("archive_vs_py310", archived_png, py310_png, "archive", "py310"),
        ):
            row = {"comparison": label, "sample_id": sample_id, "uid": uid,
                   "image_a": str(left), "image_b": str(right), **image_metrics(left, right)}
            observer = observer_rows.get((uid, "native_gfl"), {})
            row["historical_gallery_sha256"] = observer.get("source_sha256", "")
            row["prior_observer_sha256"] = observer.get("observer_sha256", "")
            row["py310_trace_matches_prior_observer"] = (
                row["sha_b"] == observer.get("observer_sha256") if tag_b == "py310" else ""
            )
            key = (uid, "native_gfl")
            arow = old_rows[key] if tag_a == "archive" else native_rows[
                "py313_repeat1" if tag_a == "py313" else tag_a
            ][key]
            brow = old_rows[key] if tag_b == "archive" else native_rows[
                "py313_repeat1" if tag_b == "py313" else tag_b
            ][key]
            metric_keys = sorted(k for k, v in arow.items()
                                 if isinstance(v, (int, float)) and k in brow
                                 and isinstance(brow[k], (int, float))
                                 and k not in {"object_idx", "seed_base", "elapsed_seconds"})
            for metric in metric_keys:
                row[f"metric_{metric}_a"] = arow[metric]
                row[f"metric_{metric}_b"] = brow[metric]
                row[f"metric_{metric}_delta_b_minus_a"] = brow[metric] - arow[metric]
            output_rows.append(row)

    write_csv(ROOT / "P0_TENSOR_DIFFERENCE_TABLE.csv", tensor_rows)
    write_csv(ROOT / "P0_OUTPUT_DIFFERENCE_TABLE.csv", output_rows)

    first_rows = []
    for comparison in ("py313_repeat1_vs_repeat2", "py313_vs_py310"):
        for sample_id, uid in OBJECTS:
            group = [r for r in tensor_rows
                     if r["comparison"] == comparison and r["uid"] == uid]
            def get(name):
                return next((r for r in group if r["tensor"] == name), None)
            candidates = [r for r in group if r["tensor"].startswith("tensors.")
                          and r["values_equal"] is False]
            first = min(candidates, key=lambda r: (
                0 if r["tensor"].startswith("tensors.batch_") else
                1 if r["tensor"] == "tensors.initial_latent" else
                2 if r["tensor"].startswith("tensors.geo_feats") else
                3 if r["tensor"].startswith("tensors.unet_cross_attention_kwargs") else
                4 if r["tensor"].startswith("tensors.unet_encoder_hidden_states") else
                5 if r["tensor"].startswith("tensors.unet_added_cond_kwargs") else
                6 if r["tensor"].startswith("tensors.scheduler_input_latent_step") else
                7 if r["tensor"].startswith("tensors.unet_input_step") else 8,
                r["tensor"],
            ), default=None)
            batch_fields = [r for r in group if r["tensor"].startswith("tensors.batch_")]
            geo_fields = [r for r in group if r["tensor"].startswith("tensors.geo_feats.")]
            cond_fields = [r for r in group if r["tensor"].startswith("tensors.unet_cross_attention_kwargs_cond_lat")]
            prompt_fields = [r for r in group if r["tensor"].startswith("tensors.unet_encoder_hidden_states")]
            first_rows.append({
                "comparison": comparison, "sample_id": sample_id, "uid": uid,
                "all_batch_inputs_exact": all(r["exact"] for r in batch_fields) if batch_fields else "not_saved",
                "geo_encoder_features_exact": all(r["exact"] for r in geo_fields) if geo_fields else "not_saved",
                "initial_latent_exact": bool(get("tensors.initial_latent")["exact"])
                    if get("tensors.initial_latent") else "not_saved",
                "condition_vae_latent_exact": all(r["exact"] for r in cond_fields) if cond_fields else "not_saved",
                "prompt_embedding_exact": all(r["exact"] for r in prompt_fields) if prompt_fields else "not_saved",
                "first_value_divergence": "none" if first is None else first["tensor"],
                "first_divergence_max_abs": "" if first is None else first["max_abs"],
                "first_divergence_rmse": "" if first is None else first["rmse"],
                "first_divergence_changed_fraction": "" if first is None else first["changed_fraction"],
                "interpretation": "all traced values are exact" if first is None else
                    "first numerical change after multiplying the shared initial FP16 latent by scheduler init_noise_sigma"
                    if first["tensor"] == "tensors.scheduler_input_latent_step00" else
                    "see per-tensor table for first changed event",
            })
    write_csv(ROOT / "P0_FIRST_DIVERGENCE.csv", first_rows)

    env_rows = []
    for name, root in RUNS.items():
        env = json.loads((root / "environment.json").read_text())
        row = {"run": name, **{k: v for k, v in env.items() if k != "model_details"}}
        row["model_details_json"] = json.dumps(env.get("model_details", {}), sort_keys=True)
        env_rows.append(row)
    write_csv(ROOT / "P0_RUNTIME_ENVIRONMENTS.csv", env_rows)
    print(f"wrote {len(tensor_rows)} tensor/config comparisons and {len(output_rows)} PNG/metric comparisons")


if __name__ == "__main__":
    main()
