import numpy as np

from geotex.round2_bake_metrics import (
    cross_view_texel_variance,
    stratified_object_ids,
    uv_seam_color_difference,
)


def test_stratified_selection_covers_all_quartiles():
    values = {f"obj_{i:04d}": float(i) for i in range(12)}
    selected = stratified_object_ids(values, per_quartile=1)
    assert len(selected) == 4
    assert selected == ["obj_0000", "obj_0003", "obj_0006", "obj_0009"]


def test_bake_metrics():
    texture = np.asarray([[0, 0, 0], [1, 0, 0]], dtype=float)
    assert uv_seam_color_difference(texture, np.asarray([[0, 1]])) == 1.0
    colors = np.asarray([[[0, 0, 0]], [[1, 0, 0]]], dtype=float)
    assert cross_view_texel_variance(colors) == 1 / 12
