# Final color-fix verdict

| Criterion | Verdict | Evidence |
|---|---|---|
| `SOURCE_VIEW_COLOR_PRESERVATION_DIAGNOSED` | YES, on the four-object development cohort | Verified unique6 tile-0 identity, source/condition/output robust color readouts, condition transform and mask overlap; see Phase A CSVs and `A_SOURCE_VIEW_COLOR_AUDIT.md`. |
| `COLOR_CONTROL_CHANNEL_IDENTIFIED` | YES, partial mechanism | Global-embedding-only a* perturbations pass the locked source and unseen-view response rule on 4/4 objects; VAE-only arms fail. This is color control, not correction. |
| `VISIBLE_PINK_CAST_REDUCED` | NO / not established | C1 does not visibly correct both Fig. 4 failures; one case has no clear change, the other gains a cool edge rim and retains mismatch. |
| `UNSEEN_VIEW_COLOR_IMPROVED` | Numeric development signal only | C1 mean paired five-view ΔFG-CIEDE2000 −1.5602 (95% CI [−2.2621, −0.6299], 4/4 wins) on four development objects; independent Fresh B validation was not run. |
| `HIGH_TEXTURE_Q4_NO_MAJOR_REGRESSION` | Not established | One high-texture development object showed no obvious visual detail damage; this is not independent Q4 validation. |
| `STRUCTURE_AND_DETAIL_PRESERVED` | No obvious development damage, not validated | Normal/high-texture manual review passed; the Fig. 4 row 2 edge rim is a visible artifact. |
| `COLOR_FIX_VALIDATED` | **NO** | The pre-registered visual gate failed; method lock closes the holdout. |

## Overall decision

- `COLOR_ROOT_CAUSE_IDENTIFIED = PARTIAL`
- `COLOR_FIX_VALIDATED = NO`
- `REPRODUCIBILITY_CLOSED = NO` — Phase B's runtime and shared-factor identities are closed, but the separate prior Fresh C output discrepancy remains unresolved by this V2 experiment.
- `R1_FIDELITY_EVIDENCE_READY = PARTIAL` for an evidence-based, qualified response; this is not evidence of a successful color repair.

The source-cache discrepancy and global-embedding control route are supported by causal/input-provenance evidence, but the complete color-generation root cause remains unresolved. C1 is a negative visual-gate result despite favorable four-object numeric metrics. Fresh B repair outputs were not opened. Do not present a solved color issue or a validated post-process.

Phase B added 64 GPU diffusion generations (485.1 s measured sampler wall time) with no training. The earlier model-load preflight and failed pre-generation runner attempt each made zero generations. C1 is CPU post-processing and added zero diffusion calls. No C2 experiment was run.
