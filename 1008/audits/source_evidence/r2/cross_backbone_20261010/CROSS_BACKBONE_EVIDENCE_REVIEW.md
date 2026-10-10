# Cross-backbone evidence review (10 October 2026)

**Source branch:** `codex/next-review-response-20260930`  
**Source commit:** `4f312566ed42a7b56fae9f11d91d4591d71fd1f2`  
**Target manuscript baseline checked:** `mvpainter/main` at `815ab0f70bf408e2d3e2a1b76ce366ec5829c41f`  
**Disposition:** usable as retrospective, interface-specific evidence; not a confirmatory or architecture-matched TCAS replication.

## Evidence chronology and scope

The preserved branch first introduces the MV-Adapter protocol, the generated result files, and the report in the same commit (`4f312566`). Its document calls the protocol pre-registered, but Git history cannot authenticate that it was frozen before outcome inspection. The paper therefore labels this result retrospective and treats all pointwise intervals as descriptive. The same chronology limit applies to the MVDiffusion schedule package in that commit. This does not invalidate the observed output files, but it prevents a prospective/confirmatory label.

The new MV-Adapter code scales four `cond_encoder` feature tensors before they enter the UNet as `down_intrablock_additional_residuals`. GeoTex scales residual corrections inside wrapped ResNet blocks. The algebra and injection surface differ, so these results characterize a related control interface rather than transfer of the exact TCAS mechanism.

## MV-Adapter 76-object panel checks

- The committed SHA-256 manifest contains 19 files; all 19 source hashes matched before import.
- The combined panel has 532 rows: 76 identical object IDs in each of seven conditions, with all six recorded metrics finite. The three new layer-wise conditions each have 76 rows (228 total) and use exact-mesh inputs.
- The 3-object identity audit passes bitwise for the layer-wise wrapper against the existing global runner on 9/9 schedule/object cases and matches the archived PNGs. This validates wrapper identity for those cases; it does not compare the unmodified official pipeline at native scale 1.0 or close the native-default reviewer request.
- In layer-wise versus global contrasts (P1, P2, P4), PSNR, CIEDE2000, and ground-truth-relative texture error favor the layer-wise rows, while FG-/Edge-SSIM favor global rows; FG-LPIPS is not separated. The direction is metric-dependent.
- For temporal placement, L-LLH minus L-FIX has one pointwise 95% interval excluding zero (direction-adjusted CIEDE2000 `+0.072790`, CI `[+0.004371,+0.156696]`); the other five include zero. G-LLH minus G-LHL has one small pointwise interval excluding zero (Edge-SSIM `-0.000261`, CI `[-0.000522,-0.000032]`); the other five include zero. These are unadjusted intervals across the 30 metric/comparison cells; do not claim a consistent temporal winner, equivalence, or family-wise significance.

## MVDiffusion model and interface checks

The 75-object schedule panel used the `sd21_depth_compat` deployment base and 450 new scheduled 12-view generations. A later native-mirror check found 1,552/1,552 loaded tensors bitwise identical after the documented key migration and 12/12 output PNGs identical for one object (obj_0024, seed 42, 50 steps). The panel itself was not rerun on the mirror; paper wording must distinguish the compatibility-base run from this narrow mirror-equivalence check.

The active path scales a correspondence-aware CPBlock output through exact convex interpolation; depth is concatenated into the latent and is not scaled. This remains a partial, interface-specific control, not an independent additive geometry residual. The 75-object outcomes are mixed across structure, color, and texture metrics and are not pooled with other systems.

## Imported files

The MV-Adapter protocol, layerwise source hash manifest, identity audit, 76-object panel, three new per-object CSVs, run configurations, report, and bootstrap records are preserved below `mvadapter_layerwise_76/`. MVDiffusion source reports, native-mirror checks, run configurations, paired panel data, bootstrap summary, and analysis scripts are preserved below `mvdiffusion/`. `SOURCE_SHA256SUMS.txt` covers this complete imported snapshot (excluding itself).
