import numpy as np
import pytest

from geotex.round2_stats import (
    MAIN_HOLDOUT_IDS,
    MAIN_POOLED_IDS,
    MV_ADAPTER_CALIBRATION_IDS,
    MV_ADAPTER_HOLDOUT_IDS,
    MV_ADAPTER_TOTAL_IDS,
    UNIQUE_TARGET_VIEWS,
    aggregate_view_rows,
    bootstrap_mean_ci,
    paired_delta_summary,
    symmetric_log_error,
    validate_fixed_partitions,
    validate_split,
    validate_view_ids,
)


def test_unique_target_views_are_unique_and_fixed():
    assert validate_view_ids(UNIQUE_TARGET_VIEWS) == (0, 15, 12, 16, 13, 14)
    with pytest.raises(ValueError):
        validate_view_ids((0, 15, 12, 15, 13, 14))


def test_main_holdout_has_no_probe_overlap():
    validate_split(MAIN_HOLDOUT_IDS, split="main_holdout")
    assert not set(MAIN_HOLDOUT_IDS).intersection({f"obj_{i:04d}" for i in range(24)})


def test_round2_fixed_partitions_have_expected_sizes_and_no_overlap():
    partitions = validate_fixed_partitions()
    assert len(MAIN_POOLED_IDS) == 300
    assert len(partitions["main_probe"]) == 24
    assert len(partitions["main_holdout"]) == 276
    assert len(MV_ADAPTER_CALIBRATION_IDS) == 24
    assert len(MV_ADAPTER_HOLDOUT_IDS) == 76
    assert len(MV_ADAPTER_TOTAL_IDS) == 100
    assert set(partitions["main_probe"]) | set(partitions["main_holdout"]) == set(MAIN_POOLED_IDS)
    assert set(partitions["mv_adapter_calibration"]) | set(partitions["mv_adapter_holdout"]) == set(
        MV_ADAPTER_TOTAL_IDS
    )


def test_symmetric_log_error_is_zero_for_equal_values():
    assert np.allclose(symmetric_log_error([0.2, 1.0], [0.2, 1.0]), 0)
    assert symmetric_log_error([2.0], [1.0])[0] == pytest.approx(np.log(2.0))


def test_bootstrap_is_reproducible():
    values = np.asarray([-1.0, 0.5, 2.0, 1.5])
    assert bootstrap_mean_ci(values, seed=17) == bootstrap_mean_ci(values, seed=17)


def test_paired_bootstrap_counts_object_wins_and_rejects_nonfinite():
    summary = paired_delta_summary([0.9, 0.2, 0.5], [0.5, 0.2, 0.8], seed=17, n_resamples=100)
    assert summary["n"] == 3
    assert summary["wins"] == 1
    assert summary["ties"] == 1
    assert summary["win_rate"] == pytest.approx(1 / 3)
    with pytest.raises(ValueError, match="NaN"):
        bootstrap_mean_ci([1.0, np.nan])


def test_view_rows_are_aggregated_per_object_in_fixed_order():
    rows = [
        {"object": f"obj_{obj:04d}", "view": str(view), "metric": str(obj + view / 100)}
        for obj in (1, 0)
        for view in (14, 0, 13, 16, 12, 15)
    ]
    aggregated = aggregate_view_rows(
        rows, object_ids=("obj_0000", "obj_0001"), metrics=("metric",)
    )
    assert [row["object"] for row in aggregated] == ["obj_0000", "obj_0001"]
    assert [row["view_count"] for row in aggregated] == ["6", "6"]
    assert float(aggregated[0]["metric"]) == pytest.approx(np.mean([v / 100 for v in (0, 12, 13, 14, 15, 16)]))


def test_view_rows_reject_missing_duplicate_and_unexpected_views():
    rows = [
        {"object": "obj_0000", "view": str(view), "metric": "1"}
        for view in (0, 12, 13, 14, 15)
    ]
    with pytest.raises(ValueError, match="views"):
        aggregate_view_rows(rows, object_ids=("obj_0000",), metrics=("metric",))
    rows.append({"object": "obj_0000", "view": "16", "metric": "1"})
    rows.append({"object": "obj_0000", "view": "16", "metric": "1"})
    with pytest.raises(ValueError, match="duplicate"):
        aggregate_view_rows(rows, object_ids=("obj_0000",), metrics=("metric",))
