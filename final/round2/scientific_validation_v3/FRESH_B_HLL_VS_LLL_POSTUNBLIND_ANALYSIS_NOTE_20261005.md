# FRESH_CONFIRM_B HLL−LLL analysis note — 2026-10-05

This contrast is requested by the final evidence-closure addendum but was not
part of the frozen four-test H3/B2 family. It is being analyzed after the
other LLH temporal contrasts from B were opened. Therefore report it as a
user-directed, post-unblinding exploratory contrast, not as a preregistered
confirmatory test and not as part of the locked H3 Holm family.

Use `layer_hll − a3_baseline`; the run manifest is the source for verifying
that `a3_baseline` is the all-low LLL profile. Report paired object bootstrap
mean, median, 95% CI, direction-aware favorable-object rate, and bootstrap
p-value for FG-PSNR and FG-LPIPS (10,000 draws, seed 20261002). Holm-adjust
the two endpoint tests together as an exploratory family. The contrast is
needed to assess whether the FRESH_CONFIRM_B directions are compatible with
“early-high hurts / late-high helps”; it cannot strengthen the locked primary
H3 family retrospectively.
