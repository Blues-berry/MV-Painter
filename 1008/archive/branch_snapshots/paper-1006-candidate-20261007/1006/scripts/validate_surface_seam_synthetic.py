#!/usr/bin/env python3
"""Synthetic known-color pilot; production glTF integration remains a gate."""
import json
from pathlib import Path

import numpy as np

from surface_seam_diagnostic import measure


def bilinear(image, points):
    xy = points * (np.array(image.shape[:2][::-1])-1)
    lo = np.floor(xy).astype(int)
    hi = np.minimum(lo+1, np.array(image.shape[:2][::-1])-1)
    weight = xy-lo
    x, y = lo.T
    hx, hy = hi.T
    wx, wy = weight.T
    return (image[y,x]*(1-wx[:,None])*(1-wy[:,None]) +
            image[y,hx]*wx[:,None]*(1-wy[:,None]) +
            image[hy,x]*(1-wx[:,None])*wy[:,None] +
            image[hy,hx]*wx[:,None]*wy[:,None])


def main():
    # Two chart triangles meet on a geometric edge but have separated UVs.
    vertices = np.array([[0,0,0],[1,0,0],[0,1,0], [1,0,0],[1,1,0],[0,1,0]], float)
    faces = np.array([[0,1,2],[3,4,5]])
    uv = np.array([[.1,.1],[.3,.1],[.1,.3],[.8,.1],[.8,.3],[.6,.3]])
    yy, xx = np.mgrid[0:512,0:512]/511
    # Each chart stores the same world-surface linear RGB function, not a
    # constant image. The inverse chart maps differ by .5 in atlas U.
    world_x = np.where(xx < .5, (xx-.1)/.2, (xx-.6)/.2)
    world_y = (yy-.1)/.2
    good = np.stack([.2+.1*world_x, .3+.1*world_y, .4+.05*world_x], axis=-1)
    broken = good.copy()
    broken[xx >= .5] += np.array([.2, 0, 0])
    continuous = measure(vertices, faces, uv, lambda p: bilinear(good,p))
    discontinuous = measure(vertices, faces, uv, lambda p: bilinear(broken,p))
    # A detached triangle adds silhouette/occlusion-like open boundaries only.
    v2 = np.concatenate([vertices, [[3,0,0],[4,0,0],[3,1,0]]])
    uv2 = np.concatenate([uv, [[.1,.1],[.3,.1],[.1,.3]]])
    f2 = np.concatenate([faces, [[6,7,8]]])
    open_boundary = measure(v2, f2, uv2, lambda p: bilinear(good,p))
    assert continuous["paired_chart_edges"] == 1 and continuous["mean_boundary_rgb_l2"] < 1e-6
    assert discontinuous["mean_boundary_rgb_l2"] > .19
    assert open_boundary["paired_chart_edges"] == 1
    assert open_boundary["open_edges_excluded"] == continuous["open_edges_excluded"] + 3
    report = {"status": "PASS_SYNTHETIC_NUMERIC_ONLY", "continuous": continuous,
              "discontinuous": discontinuous, "open_boundary": open_boundary,
              "production_metric_frozen": False, "glb_sampler_integration": "NOT_VALIDATED",
              "real_asset_seam_improvement": "NOT_TESTED"}
    path = Path(__file__).resolve().parents[1]/"data/seam_pilot/SYNTHETIC_SEAM_GATE.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
