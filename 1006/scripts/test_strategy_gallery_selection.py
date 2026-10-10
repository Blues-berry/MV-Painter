#!/usr/bin/env python3
"""Check the final gallery's fixed 20-object balance and small-cohort fallback."""
from __future__ import annotations

from generate_strategy_comparison_gallery import final_selected_uids


CONTRASTS = ("C3-GFL", "LLH-C3", "LLH-linear", "C3-linear")


def make_rows(n: int) -> dict[str, list[dict[str, float | str]]]:
    return {
        contrast: [
            {"object_uid": f"uid-{index:03d}",
             "delta_fg_psnr": float(index - n // 2) / (contrast_index + 1),
             "delta_fg_lpips": float((index * 7 + contrast_index) % 19 - 9) / 1000}
            for index in range(n)
        ]
        for contrast_index, contrast in enumerate(CONTRASTS)
    }


def main() -> None:
    rows20 = make_rows(64)
    selected = final_selected_uids(rows20, 64)
    assert len(selected) == 20
    assert len({row["object_uid"] for row in selected}) == 20
    counts = {contrast: sum(row["focal_contrast"] == contrast for row in selected)
              for contrast in CONTRASTS}
    assert counts == {contrast: 5 for contrast in CONTRASTS}, counts
    assert all(row["selection_stratum"] for row in selected)

    rows_small = make_rows(12)
    selected_small = final_selected_uids(rows_small, 12)
    assert len(selected_small) == 12
    assert {row["object_uid"] for row in selected_small} == {
        row["object_uid"] for row in rows_small["C3-GFL"]
    }
    assert all(row["focal_contrast"] == "C3-GFL" for row in selected_small)
    assert all("significance" not in row for row in selected + selected_small)
    print("PASS: 20 unique examples balanced 5 per locked contrast; N<20 shows all objects.")


if __name__ == "__main__":
    main()
