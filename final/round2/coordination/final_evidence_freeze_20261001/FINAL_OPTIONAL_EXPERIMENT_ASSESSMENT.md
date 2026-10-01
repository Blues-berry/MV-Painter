# Final optional-experiment assessment — L-TCAS manuscript audit — 2026-10-01

Scope check performed before the final claim-audit commit. No new inference,
no GPU run, no cohort change was performed or is required. Each candidate
experiment below was assessed against the frozen evidence and the current
manuscript wording; none is blocking for the current claim set.

| Candidate experiment | Reviewer motivation | Expected benefit | Cost | Blocking? |
|---|---|---|---|---|
| Equal-effective-budget strict-276 rerun (exact nominal-budget controls) | "schedules differ in nominal budget" | Would convert the budget caveat into a controlled contrast | Full 276-object inference × several schedules (GPU) | NO — manuscript already discloses non-equal budgets as a limitation; the budget-neutral B′ grouping is indistinguishable on the MV-Adapter deployment, and no claim rests on budget equality |
| MVDiffusion depth-path scaling | "try to make MVDiffusion replicate" | None admissible — depth is injected by latent concat, scaling forbidden by the interface | Interface surgery + rerun; would violate the no-tuning rule | NO — the paper reports it as an interface-boundary experiment, not a failure to be fixed |
| Fourth backbone / third adapter | "more architectures" | Wider boundary map, no change to existing conclusions | Large (deployment + mapping + calibration + holdout) | NO — claims are bounded to "one additional adapter architecture"; the boundary sentence is already architecture-limited |
| Seed / realization expansion beyond R0/R1 | "more randomness coverage" | Marginal: 27/28 STABLE_STRONG already | 276-object reruns per seed | NO — R0/R1 statement is the frozen claim width |
| Human evaluation / preference study | "texture quality is perceptual" | Would support perceptual claims the paper deliberately does not make | IRB-like setup + participants | NO — the paper claims distance-to-GT statistics and explicit non-fidelity of variation proxies, not perceived quality |
| Layer-wise MVDiffusion with alternative projection surface | "give the negative result a second chance" | Only if a reviewer provides an admissible scaling surface | Unknown interface work | NO under current frozen evidence; revisit only under explicit reviewer pressure |
| Full per-object tensor-hash backfill for the five original Core-5 arms | provenance completeness | Closes the disclosed hash-retention gap | Re-inference would be required to regenerate hashes — prohibited | NO — disclosed in Supplementary S1 as a non-blocking limitation; shared-input audits and paired records carry the verification |

## Verdict

```text
OPTIONAL_EXPERIMENTS = NONE_REQUIRED
```

No candidate experiment is required to support any claim currently made in
`final_round2.tex`, `supplementary_round2.tex`, or
`response_letter_round2.md`. All claims are bounded to the frozen evidence
surfaces: Core-7 same-runner matrix, texture GT-distance/CIEDE2000 audits
(two non-pooled surfaces), R0/R1 robustness, MV-Adapter prespecified-mapping
transfer, and the MVDiffusion interface boundary.
