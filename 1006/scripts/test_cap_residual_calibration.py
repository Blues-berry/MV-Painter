"""Meaningful bounds and execution-path tests for the candidate intervention."""
import math
import unittest

from cap_residual_calibration import install_hooks, scale_for_target, temporal_factor


class CalibrationTests(unittest.TestCase):
    def test_target_and_cap(self):
        self.assertEqual(scale_for_target(10, 2, .1, .8), (.5, .5, "unsaturated"))
        self.assertEqual(scale_for_target(10, 2, .5, .8), (2.5, .8, "saturated"))

    def test_zero_is_not_infinite_scale(self):
        for hidden, raw in ((0, 1), (1, 0), (0, 0)):
            self.assertEqual(scale_for_target(hidden, raw, .1, .8), (0, 0, "zero_norm"))

    def test_invalid_inputs_fail(self):
        for value in (math.nan, math.inf, -1):
            with self.assertRaises(ValueError):
                scale_for_target(value, 1, .1, .8)

    def test_c3_mean_and_windows(self):
        factors = [temporal_factor(step) for step in range(50)]
        self.assertAlmostEqual(sum(factors) / 50, 1.0)
        self.assertEqual(sum(x > 1 for x in factors), 16)
        with self.assertRaises(ValueError):
            temporal_factor(50)

    def test_read_write_noop_and_joint_scale(self):
        import torch
        from types import SimpleNamespace

        class Adapter(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.calls = 0

            def compute_correction(self, hidden, geo):
                self.calls += 1
                return geo

        class Wrapper(torch.nn.Module):
            _skip_correction = False

            def __init__(self, group, index):
                super().__init__()
                self.adapter = Adapter()
                self.depth_group, self.adapter_idx = group, index
                self._max_scale = .8
                self._adapter_scale = .5
                self._correction_controller = None

            def forward(self, hidden, geo):
                if self._skip_correction:
                    return hidden
                raw = self.adapter.compute_correction(hidden, geo)
                return hidden + raw * min(self._adapter_scale, self._max_scale)

        wrappers = torch.nn.ModuleList([Wrapper(g, i) for i, g in enumerate(("deep", "middle", "shallow"))])
        model = SimpleNamespace(pipeline=SimpleNamespace(unet=wrappers))
        hidden = torch.ones(1, 1, 3, 2)  # Six packed views, unequal corrections.
        raw = torch.arange(1., 7.).reshape_as(hidden)
        baseline = wrappers[0](hidden, raw)
        state = {"step": 0, "traces": []}
        remove = install_hooks(model, Wrapper, state, "observe")
        self.assertTrue(torch.equal(wrappers[0](hidden, raw), baseline))
        remove()
        self.assertNotIn("compute_correction", wrappers[0].adapter.__dict__)
        before = wrappers[0].adapter.calls
        remove = install_hooks(model, Wrapper, state, "calibrated", {g: .1 for g in ("deep", "middle", "shallow")})
        output = wrappers[0](hidden, raw)
        self.assertEqual(wrappers[0].adapter.calls, before + 1)
        scale = state["traces"][-1]["applied_scale"]
        self.assertTrue(torch.allclose(output, hidden + raw * scale))
        Wrapper._skip_correction = True
        try:
            self.assertTrue(torch.equal(wrappers[0](hidden, raw), hidden))
            self.assertEqual(wrappers[0].adapter.calls, before + 1)
        finally:
            Wrapper._skip_correction = False
            remove()


if __name__ == "__main__":
    unittest.main()
