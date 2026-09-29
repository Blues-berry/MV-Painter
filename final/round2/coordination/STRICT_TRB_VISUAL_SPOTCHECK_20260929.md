# Strict TRB visual spot-check

Two complete six-view panels from the 24-object development pilot were
reviewed qualitatively after the metric gate, using objects `obj_0000` and
`obj_0015` and the saved GT, C3_TCAS, LLH_eq and TRB_TCAS panels.

- `obj_0000`: TRB and C3 are visually close; neither shows a clear reduction
  in the visible texture/edge mismatch relative to the other. This agrees with
  the primary gate rather than suggesting a hidden TRB win.
- `obj_0015`: TRB retains the same localized colour/edge artefacts visible in
  C3, while LLH_eq is visually cleaner on this sample. This is a qualitative
  illustration only, not a claim about all 24 objects.

The source panels are under
`/4T/tmp/mvpainter-adaptive-control/outputs/trb_clean_v2_dev24_seed42_lpips_r1/maps/`.
