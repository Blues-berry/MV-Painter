import unittest

from analyze_fresh_d import CONDITIONS, holm, paired_table


class ProspectiveStatisticsTests(unittest.TestCase):
    def test_holm_restores_original_order_and_monotonicity(self):
        adjusted = holm([.04, .001, .03])
        self.assertAlmostEqual(adjusted[0], .06)
        self.assertAlmostEqual(adjusted[1], .003)
        self.assertAlmostEqual(adjusted[2], .06)

    def rows(self):
        return [{"uid": uid, "condition": c, "latent_seed": 42, "fg_psnr": 20., "fg_lpips": .1,
                 **{f"input_{i}_sha256": "a"*64 for i in range(6)}} for uid in ("a", "b") for c in CONDITIONS]

    def test_full_grid_required_and_no_pseudoreplication(self):
        rows = self.rows()
        self.assertEqual(len(paired_table(rows, ["a", "b"])), 18)
        with self.assertRaises(ValueError):
            paired_table(rows[:-1], ["a", "b"])
        with self.assertRaises(ValueError):
            paired_table(rows + [rows[0]], ["a", "b"])
        rows[0]["latent_seed"] = 43
        with self.assertRaises(ValueError):
            paired_table(rows, ["a", "b"])

    def test_input_mismatch_cannot_be_dropped(self):
        rows = self.rows()
        rows[0]["input_0_sha256"] = "b"*64
        with self.assertRaises(ValueError):
            paired_table(rows, ["a", "b"])


if __name__ == "__main__":
    unittest.main()
