"""Paired UV-chart boundary color diagnostic, excluding open geometry edges.

This measures chart-boundary color disagreement, not texture fidelity. Production
use still requires a validated glTF sampler and input/UV identity audit.
"""
from __future__ import annotations

import numpy as np


def paired_chart_edges(vertices, faces, uv, tolerance=1e-6):
    vertices, faces, uv = map(np.asarray, (vertices, faces, uv))
    if not np.isfinite(vertices).all() or not np.isfinite(uv).all() or tolerance <= 0:
        raise ValueError("invalid geometry/UV/tolerance")
    if len(vertices) != len(uv) or faces.ndim != 2 or faces.shape[1] != 3:
        raise ValueError("expected triangulated vertex-aligned UV geometry")
    span = max(float(np.ptp(vertices, axis=0).max()), 1e-12)
    welded = np.round(vertices / (span*tolerance)).astype(np.int64)
    edges = {}
    triangles = set()
    for face in faces:
        keys = [tuple(welded[i]) for i in face]
        signature = tuple(sorted(keys))
        if signature in triangles:
            raise ValueError("duplicate coincident triangle; topology is ambiguous")
        triangles.add(signature)
        for a, b in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            ka, kb = tuple(welded[a]), tuple(welded[b])
            if ka == kb:
                raise ValueError("degenerate geometric edge")
            pair = (int(a), int(b)) if ka < kb else (int(b), int(a))
            edges.setdefault(tuple(sorted((ka, kb))), []).append(pair)
    paired, open_edges = [], 0
    for occurrences in edges.values():
        if len(occurrences) == 1:
            open_edges += 1
        elif len(occurrences) != 2:
            raise ValueError("nonmanifold geometric edge; do not silently remove it")
        else:
            a, b = occurrences
            if not np.allclose(uv[list(a)], uv[list(b)], atol=tolerance, rtol=0):
                paired.append((a, b))
    return paired, open_edges


def measure(vertices, faces, uv, sample_color, samples=64):
    pairs, open_edges = paired_chart_edges(vertices, faces, uv)
    t = np.arange(1, samples+1)/(samples+1)
    distances, lengths = [], []
    for a, b in pairs:
        ua = uv[a[0]][None, :]*(1-t[:, None]) + uv[a[1]][None, :]*t[:, None]
        ub = uv[b[0]][None, :]*(1-t[:, None]) + uv[b[1]][None, :]*t[:, None]
        ca, cb = sample_color(ua), sample_color(ub)
        if ca.shape != (samples, 3) or cb.shape != ca.shape or not np.isfinite([ca, cb]).all():
            raise ValueError("sampler must return finite RGB values")
        distances.append(float(np.linalg.norm(ca-cb, axis=1).mean()))
        lengths.append(float(np.linalg.norm(vertices[a[0]]-vertices[a[1]])))
    return {"paired_chart_edges": len(pairs), "open_edges_excluded": open_edges,
            "mean_boundary_rgb_l2": float(np.average(distances, weights=lengths)) if pairs else None,
            "per_edge_disagreement": distances, "scope": "chart-boundary color, not overall 3D fidelity"}
