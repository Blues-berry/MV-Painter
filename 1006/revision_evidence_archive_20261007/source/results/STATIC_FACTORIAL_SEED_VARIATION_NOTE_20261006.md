# Static-factor effects relative to fixed-seed variation

This is a descriptive supplement derived from the audited
`STATIC_FACTORIAL_OBJECT_EFFECTS.csv` (SHA256
`6df73678116edf5615a43236d85d374c24c66a19f2915f4dac0842b5afe43119`). For
each factor and object, the seed range is the maximum minus minimum of its
paired factor contrast across generation seeds 42, 43, and 44. The ratio is
the absolute mean seed-averaged object effect divided by the median of those
48 object-specific seed ranges.

| Metric | Factor | Mean effect | Median within-object seed range | Ratio |
|---|---|---:|---:|---:|
| FG-LPIPS | Deep+middle | −0.00666 | 0.00444 | 1.50 |
| FG-LPIPS | Shallow | +0.00584 | 0.00645 | 0.91 |
| FG-LPIPS | Factor interaction | −0.000147 | 0.00425 | 0.03 |
| FG-PSNR (dB) | Deep+middle | +0.544 | 0.616 | 0.88 |
| FG-PSNR (dB) | Shallow | −0.116 | 1.209 | 0.10 |
| FG-PSNR (dB) | Factor interaction | +0.365 | 0.427 | 0.85 |

These ratios describe this selected 48-object subset and these three fixed
seeds. They do not test a random-seed population effect, do not replace the
object bootstrap intervals or Holm-adjusted tests, and are not equivalence or
acceptance thresholds. The metric-specific PSNR interaction is close in size
to the typical within-object seed range; the LPIPS interaction is much smaller
than that range.
