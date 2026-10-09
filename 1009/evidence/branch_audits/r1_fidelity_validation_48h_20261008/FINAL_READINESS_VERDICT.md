# Final readiness verdict

## Required adjudications

| Field | Verdict | Basis |
|---|---|---|
| `PROTOCOL_COMPARABILITY` | **PARTIAL** | Fresh C/B GFL/LLH are UID-paired and all six logged inputs match, but inference package versions are omitted from campaign run manifests; diagnostic-26 inference runtime is incompletely pinned; strict-276 lacks RGB/CIEDE and some per-object hashes/UID crosswalk. |
| `LLH_GFL_CONTRADICTION_EXPLAINED` | **PARTIAL** | Average benefit and independent high-texture failure boundary are reproduced; diagnostic selection and prediction-instance/runtime drift explain why cohorts cannot be directly pooled, but their relative contribution to the old 26-object estimate is not identified. |
| `COLOR_CONDITION_CAUSE_IDENTIFIED` | **PARTIAL** | No identity/preprocessing bug is found; single-view appearance conditioning is a plausible information limit; stage and VAE controls narrow possibilities but no unique generation mechanism is proved. |
| `INDEPENDENT_VALIDATION_COMPLETE` | **YES** | Frozen disjoint Fresh B `n=150` was audited, its PNG/source metrics were identity checked, the GT texture fields were reconstructed against all 150 official values, and the locked object-paired analysis was completed. |
| `COLOR_FIX_VALIDATED` | **NO** | The causal gate found no justified candidate; Phase D was skipped. No repair or recoloring is claimed. |
| `R1_FIDELITY_RESPONSE_READY` | **YES** | Response draft, numeric authority map, image candidates/captions, negative findings, and limitations are prepared for the color/detail portion of R1. |
| `MANUSCRIPT_EVIDENCE_INTEGRATION_READY` | **PARTIAL** | Color/detail claim edits and figures are specified, but this packet does not supply the reviewer-requested baked unseen-view/seam evidence and must not be represented as closing those issues. |
| `GITHUB_DELIVERY_COMPLETE` | **YES** | The 64-file evidence package and the final verdict/checksum update were pushed to the authorized independent branch; each remote ref matched its local commit SHA. The report's measured elapsed-time line is included in the final closeout commit. |

## Fresh C reproducibility adjudication

**Representative trace: closed to the first observed divergence. Full 120-output cause: partial.** Three objects were locked and traced on the prior evidence branch: Python 3.13 repeat captures and final RGB matched; Python 3.10 reproduced the observer RGB; cross-stack inputs were elementwise equal until `initial_latent × init_noise_sigma`, after which the first scheduler/UNet tensors and downstream latents, VAE tensors, and RGB differed. The trace confirms a stack-dependent output lineage and rules out input hashes alone as a complete reproducibility proof. Multiple Python/torch/torchvision/Diffusers/Transformers versions change together, so no unique library/kernel is identified. Only 3/120 changed outputs received full tensor-level tracing; do not claim the entire population's root cause is uniquely isolated.

## Phase D stop decision

`COLOR_FIX_VALIDATED = NO`. There is no reproducible input identity bug or isolated color-space fault to correct. A new scale/Gate/timestep search would be result-driven schedule tuning, and target-GT recoloring is prohibited. The no-go is the correct completed phase outcome, not an unfinished experiment.

## Paper decision

**B — narrow some LLH/color-texture claims while retaining supported schedule and cohort-average facts.** Put the Fresh B high-texture boundary beside any average improvement; describe texture metrics as proxies or GT-relative errors; retain the original Fig. 4/6 only as local illustrations with clarified captions; state that pre-bake RGB color shifts are confirmed while their complete generation cause and any validated repair remain unresolved. Keep residual-gating as a negative result. Use other identity-linked evidence for unseen baked views and seam/cross-view consistency before claiming those reviewer concerns are closed.

## Delivery fields to complete after remote verification

- Remote: `origin` (`https://github.com/Blues-berry/MV-Painter.git`)
- Branch: `codex/r1-fidelity-validation-48h-20261008`
- Evidence package commit SHA: `8f6de4b959fb1b34151df4d02a0c8d577010fea1`.
- Verdict/checksum commit SHA: `3425b2b5159e5b19790c80425c8e0fea96b4cb47`.
- Final elapsed-time closeout commit SHA: report the verified remote HEAD in the completion message.
- Unuploaded large source files: raw cohort RGB/run trees and the 2 GB-class tensor trace remain in their original worktrees; summary tables, manifests, row-wise SHA identities, and selected images are delivered.
