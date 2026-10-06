# Adversarial evidence screen — before manuscript rewrite

Update 2026-10-06: the GLB-native N=20 base-color evaluation has closed the
stored-renderer conformance issue. Its endpoint tradeoff does not establish
a unique 3D winner. The human study, strict N=24 scope, and final post-rewrite
review remain open; the screen below is still preliminary.

**Status: preliminary, not the protocol's final four-persona review.** The
manuscript has not been rewritten because the evidence gate remains open. A
final reviewer/reproducibility audit must follow any authorized rewrite.

**Current provisional narrative:** `NARRATIVE_D`, scoped to measured adapter
scaling and residual allocation. No full dose-independent Layer × Time law,
universal timing signature, or unique schedule winner is supported.

## Objections and disposition

| Skeptical question | Current evidence | Disposition |
|---|---|---|
| Is the 2D interaction established? | A2 is a corrected native-dose discovery map. A3b misses dose balance and has 0/2,250 rows in three-layer common support. | Keep A2 as discovery and A3b as `PARTIAL`; no dose-independent interaction claim. |
| Does B show a practically meaningful timing benefit? | LLH−LFM-EXACT is inside frozen practical margins. HLL−LLL is inconclusive on FG-PSNR and points toward LLL on FG-LPIPS. Realized residual norms differ. | Report contrast-specific effects and CIs; do not claim the full early/late signature. |
| Is LLH the unique winning schedule? | Registered `gen_linear` is not detectably worse on primary FG-PSNR; B generic extension is same-cohort, post-lock sensitivity. | Retire the unique-winner claim. No retuning or FRESH_CONFIRM_C winner search. |
| Do images establish texture fidelity? | Manual review found color/material mismatch in 18/24 panels and detail loss in 21/24. No human responses exist. | Keep C11 open; the locked human study includes the endpoint-matched linear competitor. |
| Does the bake establish practical 3D quality? | Stored GLBs now have a sampler-conformant base-color evaluation for N=20; LLH endpoints are mixed, four no-UV objects remain excluded, and no human answers exist. | P1-9 is closed for the stored N=20/8 outputs. Keep the 3D claim bounded, and do not claim a unique winner, full PBR, or human fidelity. |
| Does MV-Adapter prove architecture-dependent scheduling? | Its corrected global interaction is unsupported in the tested 98/99 cohort. Its intervention geometry differs from the primary backbone. | Preserve it as a bounded boundary finding, consistent with intervention-specific response surfaces; do not present it as a matched causal architecture test. |
| Is the human stop rule vulnerable to interim stopping? | The four-pair package fixes 40 slots, requires 36 valid completions, has no replacement slots, and has no responses. | Protocol-side control is frozen. Do not collect until the recruitment/return channel is arranged; analyze only after all slots resolve. |
| Can all final paper artifacts be reproduced? | One full A2 condition and compact statistics have clean-clone evidence; paper-wide reconstruction and post-rewrite audit remain open. | Keep reproducibility partial until the complete reconstruction passes. |

## Independent technical challenge: UV and GLB rendering

The read-only independent audit confirmed that omitted `wrapS`/`wrapT` means
repeat under glTF 2.0, while the CPU bake and stored renderer clamp UVs. It
also identified that the CPU renderer uses bilinear sampling without
mipmaps, whereas the exported sampler encodes `magFilter=9729` and
`minFilter=9987`. The machine audit checked 160 output GLBs; all had those
filter values and omitted wrap fields. Six source objects have substantial
out-of-unit UVs; two more have minor excursions whose cause is not
established. Counts are per UV pair, not surface area.

The seam generator reproduces its stored CSV and JSON byte-for-byte, but
produces 28 invalid-cast warnings for the extreme-UV object across seven
conditions. Reproducible output does not validate that seam metric. A separate
EGL renderer now evaluates the stored GLBs with their embedded sampler and
passes UV orientation/repeat and geometry-mask checks. Four no-UV objects
remain excluded.

**Current 3D scope:** stored N=20 outputs have sampler-conformant base-color
metrics. The original clamp-based bake was not rerun; keep its generation
process and seam statistics distinct from the new rendering audit. Keep the
four no-UV exclusions and run-summary coverage discrepancy explicit.

## Final review still required

This screen does not satisfy the protocol's post-rewrite adversarial gate.
After evidence closure and manuscript rewrite, run separate Reviewer 1,
Reviewer 2, Reviewer 3, and reproducibility passes. Every resulting issue
must be classified `CLOSED_BY_EVIDENCE`, `CLOSED_BY_CLAIM_REDUCTION`,
`REQUIRES_EXPERIMENT`, or `BLOCKING`; no blocking issue may remain.
