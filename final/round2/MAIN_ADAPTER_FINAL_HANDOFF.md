# Main Adapter v1 — Final Handoff Classification

## VERIFIED

- Controlled checkpoint audit, finite weights, hash, step, historical source commit, and config snapshots.
- 300-object × 4-condition inference artifact with complete object-method rows.
- Unique-six target order `[0,15,12,16,13,14]`, 256×256, 50 Euler steps, seed 42.
- Shared per-object initial latents, references, GT tensors, camera mapping, and checkpoint across conditions.
- Object-level paired bootstrap tables regenerated from the per-object CSVs.
- Full-vs-foreground metric implementation documented from source.
- GT-relative texture variation error table, including the adverse HF-energy trend.

## PARTIALLY VERIFIED

- C3 has a useful but conditional shape–texture trade-off: it beats fixed-high on FG-PSNR/FG-SSIM but loses a small amount of Edge-SSIM; against fixed-low it gains Full SSIM/LPIPS while FG-PSNR is lower and FG-SSIM is unresolved.
- Nominal 276 and pooled 300 tables show consistent direction, but neither can be interpreted as an independent generalization test because of training/evaluation UID overlap.
- Five target views can be called unseen relative to the chosen reference view; the six-view target set itself includes the reference view.

## BLOCKED

- Independent strict-holdout claim: 79 nominal holdout UIDs overlap the 1,118-object training list.
- Independent Exact-GLB baking: all 43 nominal-holdout objects with raw GLB, complete render assets, and UVs overlap training.
- DISTS and CIEDE2000 in the current main-adapter result artifact.
- Protocol-safe baking using the existing helper, because it re-unwraps UVs and uses canonical rather than stored camera poses.

## NOT SUPPORTED

- Old `+0.96 dB` claim.
- “Comparable FG-SSIM” as a general statement.
- “Does not sacrifice structure.”
- “Completely preserves texture.”
- “C3 is better than fixed-low/high on all metrics.”
- “11 unseen views.”
- Any claim that the controlled checkpoint is the recovered original v1 checkpoint.

## Evidence locations

- Raw inference: `mvpoutput/reviewer1_main_rerun_20260928/eval300_unique6/`
- Audit JSON: `final/round2/main_adapter_baking/protocol_audit.json`
- Paired statistics: `final/round2/main_adapter_baking/paired_statistics_c3_vs_baselines.json`
- LaTeX tables: `final/round2/main_adapter_baking/main_adapter_nominal_276.tex`, `main_adapter_pooled_300.tex`
- Texture tables: `mvpoutput/reviewer1_main_rerun_20260928/eval300_unique6/tables_main_adapter/TABLES_TEXTURE.md`
- Validity and interpretation summary: `final/round2/main_adapter_baking/TABLE_VALIDITY_AND_RESULTS.md`
- Fresh nominal-276 paired recheck: `final/round2/main_adapter_baking/paired_recheck_nominal_276.json`
