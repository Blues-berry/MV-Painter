#!/usr/bin/env python3
"""Boundary tests for the frozen Fresh C reserve-pool rule."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare_fresh_c_pool import cohort_status  # noqa: E402


class CohortStatusTests(unittest.TestCase):
    def test_under_target_uses_remaining_frozen_queue(self) -> None:
        for n in (0, 275, 276, 299):
            with self.subTest(n=n):
                self.assertEqual(cohort_status(n, 600), "RESERVE_BLOCK_REQUIRED")

    def test_under_target_continues_until_queue_exhausted(self) -> None:
        self.assertEqual(cohort_status(299, 800), "RESERVE_BLOCK_REQUIRED")

    def test_reduced_cohort_only_after_all_candidates_screened(self) -> None:
        self.assertEqual(
            cohort_status(299, 1000),
            "FROZEN_REDUCED_TECHNICAL_COHORT_PRECISION_TARGET_UNMET",
        )

    def test_below_minimum_blocks_after_all_candidates_screened(self) -> None:
        self.assertEqual(
            cohort_status(275, 1000), "BLOCKED_TECHNICAL_COHORT_BELOW_MINIMUM"
        )

    def test_target_cohort_can_freeze_without_reserve(self) -> None:
        self.assertEqual(cohort_status(300, 600), "FROZEN_FRESH_C_300")
        self.assertEqual(cohort_status(594, 600), "FROZEN_FRESH_C_300")


if __name__ == "__main__":
    unittest.main(verbosity=2)
