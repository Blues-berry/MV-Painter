#!/usr/bin/env python3
"""Audit the equal-call Fixed Mean candidate's identity and bake gates."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path("/4T/CXY/MV-Painter/1014_counterfactual_control_research")
ALT = Path("/4T/tmp/MV-Painter-local-excluded-20261013/1014_counterfactual_control_research")
RUN = ALT / "generation_equal_cost_b0_seed43"
BAKE = ALT / "bake_equal_cost_b0_seed43"
UIDS = [
    "1dc2c857f7614caeb6c2aa0559ccf973",
    "21678bd623654182b52c11d013de4e71",
    "238ff3e41c964655b83aa9c8770cc766",
    "2dd9bc8172c6461797947cc7214db399",
    "2f6c94487ee54cb88021f4643409d849",
    "e261c0fe85af46388260e2359a9bfc92",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    original = json.loads((ROOT / "generation/rows_shard0.json").read_text())
    alternate = json.loads((RUN / "rows_shard0.json").read_text())
    orig_rows = {(int(r["object_idx"]), r["condition"]): r for r in original}
    alt_rows = {(int(r["object_idx"]), r["condition"]): r for r in alternate}
    run_manifest = json.loads((RUN / "run_manifest_shard0.json").read_text())
    bake_summary = json.loads((BAKE / "cpu_bake_v3/BAKE_RUN_SUMMARY.json").read_text())
    egl_identity = json.loads((BAKE / "native_egl_unseen_RUN_IDENTITY.json").read_text())
    egl_manifest = json.loads((BAKE / "native_egl_unseen/GLB_NATIVE_EGL_RENDER_MANIFEST.json").read_text())
    original_egl_manifest = json.loads((ROOT / "bake/native_egl_unseen/GLB_NATIVE_EGL_RENDER_MANIFEST.json").read_text())
    original_render_hashes = {
        (r["object"], r["method"], int(r["raw_view"])): r["render_sha256"]
        for r in original_egl_manifest["renders"]
    }
    replayed_render_hashes = []
    for record in egl_manifest["renders"]:
        if record["method"] not in {"gt", "counterfactual_b0"}:
            continue
        key = (record["object"], record["method"], int(record["raw_view"]))
        if record["render_sha256"] != original_render_hashes[key]:
            raise RuntimeError(f"equal-cost EGL identity replay changed: {key}")
        replayed_render_hashes.append(record["render_sha256"])

    objects = []
    for index in (0, 1, 2, 3, 4, 7):
        uid = UIDS[(0, 1, 2, 3, 4, 7).index(index)]
        a = orig_rows[(index, "counterfactual_b0")]
        b = alt_rows[(index, "counterfactual_b0")]
        for key in a["input_hashes"]:
            if key == "init_latent":
                if a["input_hashes"][key] == b["input_hashes"][key]:
                    raise RuntimeError(f"latent seed failed to change for {uid}")
            elif a["input_hashes"][key] != b["input_hashes"][key]:
                raise RuntimeError(f"non-latent input changed for {uid}: {key}")

        trace = json.loads((RUN / "residual_logs/counterfactual_b0" / f"{uid}.json").read_text())
        if len(trace) != 50:
            raise RuntimeError(f"unexpected sampler-step count for {uid}")
        for step in trace.values():
            if len(step) != 9:
                raise RuntimeError(f"unexpected adapter-site count for {uid}")
            for site in step.values():
                expected = 0.8 if site["depth"] == "shallow" else 1.65
                if any(abs(float(s) - expected) > 1e-7 for s in site["applied_scales_by_view"]):
                    raise RuntimeError(f"Fixed Mean applied scale mismatch for {uid}")
                if any(not math.isfinite(float(dose)) for dose in site["realized_l2_by_view"]):
                    raise RuntimeError(f"non-finite realized residual dose for {uid}")

        old_texture = ALT / "bake/counterfactual_b0" / uid / f"{uid}_counterfactual_b0_texture.png"
        replay_texture = BAKE / "cpu_bake_v3/counterfactual_b0" / uid / f"{uid}_counterfactual_b0_texture.png"
        with Image.open(old_texture) as x, Image.open(replay_texture) as y:
            replay_equal = x.size == y.size and ImageChops.difference(x, y).getbbox() is None
        if not replay_equal:
            raise RuntimeError(f"B0 seed42 replay changed UV texture for {uid}")

        records = [r for r in bake_summary["records"] if r["object"] == uid]
        if len(records) != 3 or not all(r["glb_byte_patch_integrity_pass"] for r in records):
            raise RuntimeError(f"bake or GLB patch identity failure for {uid}")
        objects.append({
            "object_idx": index,
            "uid": uid,
            "input_hashes_equal_except_init_latent": True,
            "seed42_latent_sha256": a["input_hashes"]["init_latent"],
            "seed43_latent_sha256": b["input_hashes"]["init_latent"],
            "seed43_panel_sha256": sha256(RUN / "predictions/counterfactual_b0" / f"{uid}.png"),
            "seed42_b0_replay_texture_pixel_identical": replay_equal,
            "bakes_passed": len(records),
        })

    if run_manifest["latent_seed"] != 43 or len(alternate) != 6:
        raise RuntimeError("alternate seed manifest does not match the six-object run")
    if len(bake_summary["records"]) != 18 or egl_manifest["render_count"] != 198:
        raise RuntimeError("equal-cost bake/render count mismatch")
    if egl_identity["status"] != "COMPLETED":
        raise RuntimeError("native EGL identity run did not complete")

    audit = {
        "status": "PASS",
        "objects": objects,
        "latent_seed": run_manifest["latent_seed"],
        "fixed_mean_applied_scales": {"deep": 1.65, "middle": 1.65, "shallow": 0.8},
        "generation_count": len(alternate),
        "bake_count": len(bake_summary["records"]),
        "native_egl_render_count": egl_manifest["render_count"],
        "seed42_and_gt_render_replay_pixel_identical_count": len(replayed_render_hashes),
        "native_egl_sampler_probe": egl_manifest["renderer"]["sampler_probe"],
        "native_egl_renderer_sha256": egl_manifest["renderer_script_sha256"],
        "native_egl_output_resolution": egl_identity["resolution"],
    }
    (ROOT / "equal_cost_phase_a_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps({"status": audit["status"], "objects": len(objects), "bakes": len(bake_summary["records"]), "renders": egl_manifest["render_count"]}, indent=2))


if __name__ == "__main__":
    main()
