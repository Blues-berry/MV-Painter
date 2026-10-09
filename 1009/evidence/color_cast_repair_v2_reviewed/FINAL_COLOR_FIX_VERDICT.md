# Final color-fix verdict

| Criterion | Verdict | Evidence |
|---|---|---|
| `SOURCE_VIEW_COLOR_PRESERVATION_DIAGNOSED` | YES, on the four-object development cohort | Verified unique6 tile-0 identity, source/condition/output robust color readouts, condition transform and mask overlap; see Phase A CSVs and `A_SOURCE_VIEW_COLOR_AUDIT.md`. |
| `COLOR_CONTROL_CHANNEL_IDENTIFIED` | YES, partial mechanism | Global-embedding-only a* perturbations pass the locked source and unseen-view response rule on 4/4 objects; VAE-only arms fail. This is color control, not correction. |
| `CACHE_MISMATCH_SUFFICIENT_COLOR_CAUSE` | NO | The locked raw selected-source embedding replacement changed only the global feature but produced 1/4 unseen-view CIEDE2000 wins, mean Δ +0.1729, and no clear Fig. 4 visual correction. |
| `VISIBLE_PINK_CAST_REDUCED` | NO / not established | C1 does not visibly correct both Fig. 4 failures; one case has no clear change, the other gains a cool edge rim and retains mismatch. B2 also shows no clear Fig. 4 correction. |
| `UNSEEN_VIEW_COLOR_IMPROVED` | No stable improvement | C1 had a favorable four-object development mean but failed the visual gate. B2 had mean ΔFG-CIEDE2000 +0.1729 (95% CI [−0.2044, +0.6810], 1/4 wins). Independent Fresh B validation was not run. |
| `HIGH_TEXTURE_Q4_NO_MAJOR_REGRESSION` | Not established | One high-texture development object showed no obvious visual detail damage; this is not independent Q4 validation. |
| `STRUCTURE_AND_DETAIL_PRESERVED` | No obvious development damage, not validated | Normal/high-texture manual review passed; the Fig. 4 row 2 edge rim is a visible artifact. |
| `COLOR_FIX_VALIDATED` | **NO** | The pre-registered visual gate failed; method lock closes the holdout. |

## Overall decision

- `COLOR_ROOT_CAUSE_IDENTIFIED = PARTIAL`
- `COLOR_FIX_VALIDATED = NO`
- `REPRODUCIBILITY_CLOSED = NO` — B2 cached-baseline PNGs byte-match earlier Phase B GFL outputs for these four development objects, but the separate prior 120-object Fresh C output discrepancy remains unresolved by this V2 experiment.
- `R1_FIDELITY_EVIDENCE_READY = PARTIAL` for an evidence-based, qualified response; this is not evidence of a successful color repair.

The source-cache discrepancy and global-embedding control route are supported by causal/input-provenance evidence, but the complete color-generation root cause remains unresolved. C1 failed its visual gate despite favorable four-object numeric metrics; B2 raw selected-source replacement failed its numeric color gate and showed no clear visual correction. Fresh B repair outputs were not opened. Do not present a solved color issue or a validated post-process.

Phase B added 64 GPU diffusion generations (485.1 s measured sampler wall time) with no training. The earlier model-load preflight and failed pre-generation runner attempt each made zero generations. C1 is CPU post-processing and added zero diffusion calls. B2 added 8 GPU diffusion generations in 77.3 s; attempts 01–03 each stopped before generation and remain preserved. No Fresh B repair validation or C2 experiment was run.
