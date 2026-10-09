# Pre-locked Phase A color readouts from Phase B outputs

Rows: 384 per-view rows across 4 development objects and 16 locked conditions.
The magenta fraction uses the frozen rule Δa* >= +5 and Δb* <= -5 over the target foreground mask >= 0.5. No threshold was selected after viewing outputs.
The robust source condition/GT/output medians use alpha >= 0.75, 3-pixel erosion, and at least 64 pixels; no pixel registration is assumed.

GFL source-view mean magenta-residual fraction: 0.0124.
GFL unseen-view mean magenta-residual fraction: 0.0134.
Per-object GT color errors, Lab residuals, and magenta fractions are in `A_PER_OBJECT_COLOR_SUMMARY.csv`; pixels are not pooled across objects.

Per-view CSV SHA-256: `e860e305b9010d4bfd4f7664f9e9e394df9c6cee6967e0acc997668e66ab9c75`.
Source-statistics CSV SHA-256: `7545dafda7a1760ae79296a2e77db87e8590ebc9ed934e4d50b13a2b9f5a244a`.
Per-object CSV SHA-256: `2f185b27087a411875a975ddf764f8072391bf0adeea3296b9ca74a2d85ecf3e`.
