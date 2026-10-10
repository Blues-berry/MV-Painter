# Requested-versus-applied scale profile figure — 2026-10-06

`figures/strategy_comparison_gallery/cap_scale_semantics.png` illustrates the
frozen 50-step scale profiles for GFL, GFH, C3, LLH, and endpoint-matched
generic linear across deep, middle, and shallow layer groups. Dashed colored
traces show native-cap-applied scales only where a requested value exceeds the
locked cap; the dotted horizontal line is the cap. Window lengths are
17/16/17 steps. The values are exported row-by-row in
`figures/strategy_comparison_gallery/cap_scale_semantics.csv`.

The figure is an execution-semantics diagram, not an outcome graph. It shows
that shallow GFL (1.25), GFH (2.50), and C3 (1.25/2.50/1.25) are all applied at
0.80 throughout, while LLH's shallow values (0.50/0.50/0.75) and generic
linear's shallow ramp (0.50–0.75) remain below the cap. Deep and middle
requested values remain below their 3.0 and 3.5 caps. This applied scale is
not the measured residual norm, realized dose, or evidence of equal-strength
interventions.

Rebuild with `python 1006/scripts/plot_cap_scale_semantics.py`. This figure
does not use Fresh C outcomes and does not change any registered contrast or
manuscript text.
