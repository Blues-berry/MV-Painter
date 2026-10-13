#!/usr/bin/env python3
"""Exercise the stored GLB-native EGL sampler using synthetic geometry only."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RENDERER = ROOT / "final/round2/scientific_validation_v3/audit_scripts/render_glb_native_egl.py"
OUT = ROOT / "1006/evidence/audits/NATIVE_SAMPLER_SYNTHETIC_VALIDATION.json"
RESOLUTION = 32
CAMERA = {
    "extrinsic": np.eye(4, dtype=np.float32)[:3],
    "near": 0.0,
    "far": 1.0,
    "camera": "ortho",
}
FILTER = {"NEAREST": 9728, "LINEAR": 9729, "LINEAR_MIPMAP_LINEAR": 9987}
WRAP = {"CLAMP_TO_EDGE": 33071, "MIRRORED_REPEAT": 33648, "REPEAT": 10497}


def renderer_class():
    spec = importlib.util.spec_from_file_location("glb_native_egl_sampler_test", RENDERER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.EGLBaseColorRenderer


def quad(uv_min=(0.0, 0.0), uv_max=(1.0, 1.0), *, constant_uv=None) -> dict:
    positions = np.asarray([
        [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5],
        [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5],
    ], dtype=np.float32)
    if constant_uv is None:
        u0, v0 = uv_min
        u1, v1 = uv_max
        uv = np.asarray([[u0, v0], [u1, v0], [u1, v1], [u0, v1]], dtype=np.float32)
    else:
        uv = np.broadcast_to(np.asarray(constant_uv, dtype=np.float32), (4, 2)).copy()
    return {"positions": positions, "uv": uv, "faces": np.asarray([[0, 1, 2], [0, 2, 3]], dtype=np.uint32)}


def make_asset(mesh: dict, image: np.ndarray, *, wrap_s=WRAP["REPEAT"], wrap_t=WRAP["REPEAT"],
               min_filter=FILTER["NEAREST"], mag_filter=FILTER["NEAREST"], factor=(1, 1, 1, 1)) -> dict:
    return {
        **mesh,
        "image": np.asarray(image, dtype=np.uint8),
        "wrap_s": wrap_s,
        "wrap_t": wrap_t,
        "min_filter": min_filter,
        "mag_filter": mag_filter,
        "base_color_factor": np.asarray(factor, dtype=np.float32),
    }


def pixel(renderer, asset: dict, x: int, y: int) -> list[int]:
    renderer.prepare_asset(asset)
    image = renderer.render(CAMERA)
    return image[y, x].tolist()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()

    Renderer = renderer_class()
    result = {
        "suite": "FRESH_C_NATIVE_GLTF_SAMPLER_SYNTHETIC",
        "scope": "synthetic in-memory triangles/quads through EGLBaseColorRenderer.prepare_asset/render; no paper GLB or method output loaded",
        "resolution": RESOLUTION,
        "cases": [],
    }
    # Each texel is asymmetric so orientation and address-mode errors are visible.
    rgba = np.asarray([
        [[255, 0, 0, 255], [0, 255, 0, 255]],
        [[0, 0, 255, 255], [255, 255, 0, 255]],
    ], dtype=np.uint8)
    checker = np.asarray([[[255, 255, 255, 255] if (x + y) % 2 else [0, 0, 0, 255]
                          for x in range(8)] for y in range(8)], dtype=np.uint8)
    black_white = np.asarray([
        [[0, 0, 0, 255], [255, 255, 255, 255]],
        [[0, 0, 0, 255], [255, 255, 255, 255]],
    ], dtype=np.uint8)
    white = np.full((2, 2, 4), 255, dtype=np.uint8)

    with _renderer_context(Renderer) as r:
        # A. Standard [0,1] sampling and orientation.
        obs = pixel(r, make_asset(quad(), rgba), 4, 4)
        result["cases"].append(_case("A_standard_unit_uv", obs, [255, 0, 0, 255], "nearest sample at uv=(0.140625,0.140625), top-left texel"))
        # B/C. Repeat on either side of the unit square.
        obs = pixel(r, make_asset(quad((1, 0), (2, 1)), rgba), 4, 4)
        result["cases"].append(_case("B_repeat_uv_above_one", obs, [255, 0, 0, 255], "u=1.140625 wraps to 0.140625"))
        obs = pixel(r, make_asset(quad((-1, 0), (0, 1)), rgba), 4, 4)
        result["cases"].append(_case("C_repeat_uv_below_zero", obs, [255, 0, 0, 255], "u=-0.859375 wraps to 0.140625"))
        # D. Odd mirrored-repeat tile reflects horizontal addressing.
        obs = pixel(r, make_asset(quad((1, 0), (2, 1)), rgba, wrap_s=WRAP["MIRRORED_REPEAT"]), 4, 4)
        result["cases"].append(_case("D_mirrored_repeat", obs, [0, 255, 0, 255], "u=1.140625 mirrors to 0.859375"))
        # E. Clamp-to-edge maps both negative and >1 coordinates to the nearest border texel.
        obs = pixel(r, make_asset(quad((-1, 0), (0, 1)), rgba, wrap_s=WRAP["CLAMP_TO_EDGE"]), 4, 4)
        result["cases"].append(_case("E_clamp_to_edge", obs, [255, 0, 0, 255], "negative u clamps to the left edge"))
        # F. Linear sampling exactly on the two opposite texture borders.
        obs0 = pixel(r, make_asset(quad(constant_uv=(0, 0)), rgba, wrap_s=WRAP["CLAMP_TO_EDGE"], wrap_t=WRAP["CLAMP_TO_EDGE"], mag_filter=FILTER["LINEAR"]), 16, 16)
        obs1 = pixel(r, make_asset(quad(constant_uv=(1, 1)), rgba, wrap_s=WRAP["CLAMP_TO_EDGE"], wrap_t=WRAP["CLAMP_TO_EDGE"], mag_filter=FILTER["LINEAR"]), 16, 16)
        result["cases"].append(_case("F_texture_borders", [obs0, obs1], [[255, 0, 0, 255], [255, 255, 0, 255]], "CLAMP_TO_EDGE with linear filter at uv=(0,0) and (1,1)"))
        # G. Nearest magnification resolves a high-frequency checker without blending.
        asset = make_asset(quad(), checker, min_filter=FILTER["NEAREST"], mag_filter=FILTER["NEAREST"])
        g0 = pixel(r, asset, 2, 2)
        g1 = pixel(r, asset, 6, 2)
        result["cases"].append(_case("G_high_frequency_magnification", [g0, g1], [[0, 0, 0, 255], [255, 255, 255, 255]], "8x8 checker, four screen pixels per texel, nearest MAG"))
        # H. Implicit derivatives minify the 8x8 checker to its analytical 50% linear average.
        obs = pixel(r, make_asset(quad((0, 0), (8, 8)), checker, min_filter=FILTER["LINEAR_MIPMAP_LINEAR"], mag_filter=FILTER["LINEAR"]), 16, 16)
        result["cases"].append(_case("H_mipmapped_minification", obs, [188, 188, 188, 255], "8x8 black/white checker spans 8 repeats on 32px; expected 0.5 linear gray encoded to sRGB"))
        # I. Constant intermediate UV forces magnification filtering at the midpoint.
        obs = pixel(r, make_asset(quad(constant_uv=(0.5, 0.25)), black_white, min_filter=FILTER["NEAREST"], mag_filter=FILTER["LINEAR"]), 16, 16)
        result["cases"].append(_case("I_linear_magnification", obs, [188, 188, 188, 255], "linear interpolation halfway between black and white texel centers"))
        # J. Duplicated vertices carry a known UV discontinuity at the vertical mesh boundary.
        pos = np.asarray([
            [-.5, -.5, .5], [0, -.5, .5], [0, .5, .5], [-.5, .5, .5],
            [0, -.5, .5], [.5, -.5, .5], [.5, .5, .5], [0, .5, .5],
        ], dtype=np.float32)
        uv = np.asarray([[.25, .25]] * 4 + [[.75, .25]] * 4, dtype=np.float32)
        faces = np.asarray([[0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7]], dtype=np.uint32)
        seam_mesh = {"positions": pos, "uv": uv, "faces": faces}
        j0 = pixel(r, make_asset(seam_mesh, rgba, mag_filter=FILTER["NEAREST"]), 4, 16)
        j1 = pixel(r, make_asset(seam_mesh, rgba, mag_filter=FILTER["NEAREST"]), 27, 16)
        result["cases"].append(_case("J_known_uv_discontinuity", [j0, j1], [[255, 0, 0, 255], [0, 255, 0, 255]], "two adjacent geometry regions use duplicated vertices with distinct constant UVs"))
        # K/L. BaseColorFactor is multiplied in linear space; OPAQUE alpha is rendered opaque.
        obs = pixel(r, make_asset(quad(), white, factor=(0.25, 0.5, 0.75, 0.2)), 16, 16)
        result["cases"].append(_case("K_base_color_factor_and_opaque_alpha", obs, [137, 188, 225, 255], "factor RGB in linear color; OPAQUE ignores factor alpha for output coverage"))

        result["built_in_orientation_repeat_probe"] = r.sampler_probe

    result["pass_count"] = sum(c["status"] == "PASS" for c in result["cases"])
    result["case_count"] = len(result["cases"])
    result["status"] = "PASS" if result["pass_count"] == result["case_count"] else "FAIL"
    result["scope_limit"] = "This validates EGL sampling on synthetic geometry, not the absent original-UV-preserving view-to-texture baker. Source assets with BLEND alpha mode also require correct alpha compositing before a 24-object output gate can pass."
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


def _case(name, observed, expected, reference):
    obs = np.asarray(observed)
    exp = np.asarray(expected)
    passed = bool(obs.shape == exp.shape and np.max(np.abs(obs.astype(int) - exp.astype(int))) <= 2)
    return {"case": name, "observed_rgba8": observed, "expected_rgba8": expected,
            "tolerance_code_values": 2, "reference": reference, "status": "PASS" if passed else "FAIL"}


class _renderer_context:
    def __init__(self, renderer_cls):
        self.renderer_cls = renderer_cls
        self.value = None
    def __enter__(self):
        self.value = self.renderer_cls(RESOLUTION)
        return self.value
    def __exit__(self, exc_type, exc, tb):
        if self.value is not None:
            self.value.close()


if __name__ == "__main__":
    main()
