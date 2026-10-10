import unittest

from analyze_fresh_d import CONDITIONS, INPUT_FIELDS, SECONDARY, analyze_sensitivity, holm, paired_table


class ProspectiveStatisticsTests(unittest.TestCase):
    def test_holm_restores_original_order_and_monotonicity(self):
        adjusted = holm([.04, .001, .03])
        self.assertAlmostEqual(adjusted[0], .06)
        self.assertAlmostEqual(adjusted[1], .003)
        self.assertAlmostEqual(adjusted[2], .06)

    def rows(self):
        return [{"uid": uid, "condition": c, "latent_seed": 42, "fg_psnr": 20., "fg_lpips": .1,
                 **{m: .5 for m in SECONDARY},
                 **{field: "a"*64 for field in INPUT_FIELDS}} for uid in ("a", "b") for c in CONDITIONS]

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
        rows[0][INPUT_FIELDS[0]] = "b"*64
        with self.assertRaises(ValueError):
            paired_table(rows, ["a", "b"])

    def sensitivity_rows(self):
        result = []
        for seed, shift in ((42, 0), (43, 7), (44, -3)):
            for row in self.rows():
                row["latent_seed"] = seed
                row["input_init_latent_sha256"] = format(seed, "064x")
                row["fg_psnr"] += shift
                if row["condition"] == "cap_calibrated":
                    row["fg_psnr"] += 1 if row["uid"] == "a" else 3
                result.append(row)
        return result

    def test_average_seeds_before_object_inference(self):
        result = analyze_sensitivity(self.sensitivity_rows(), ["a", "b"])
        psnr = result["families"]["primary"][0]
        self.assertEqual(psnr["n_objects"], 2)
        self.assertEqual(psnr["mean"], 2)
        self.assertEqual(psnr["median_same_condition_seed_range"], 10)
        self.assertAlmostEqual(psnr["abs_effect_over_median_same_condition_seed_range"], .2)
        self.assertFalse(result["primary_confirmatory"])

    def test_reference_change_between_seeds_fails(self):
        rows = self.sensitivity_rows()
        for row in rows:
            if row["latent_seed"] == 43:
                row[INPUT_FIELDS[0]] = "b"*64
        with self.assertRaises(ValueError):
            analyze_sensitivity(rows, ["a", "b"])

    def test_invalid_secondary_endpoint_is_not_silently_omitted(self):
        rows = self.rows()
        rows[0]["edge_ssim"] = float("nan")
        with self.assertRaises(ValueError):
            paired_table(rows, ["a", "b"])


if __name__ == "__main__":
    unittest.main()
