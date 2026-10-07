# Historical reviewer-closure snapshot — updated 2026-10-06 17:42 UTC

> **Superseded on 2026-10-07.** Current reviewer status is [`REVIEWER_CLOSURE_20261007.md`](REVIEWER_CLOSURE_20261007.md): science evidence is frozen for bounded claims, old 01549 3AFC is retained as C3/TCAS complementary preference evidence, and the uploaded 40-slot study is reported as a confirmatory endpoint analysis with documented execution deviations. Reviewer closure remains PARTIAL and upload remains HOLD. The original table below is retained as a dated snapshot.

This matrix supersedes the pre-rewrite disposition in
`evidence/audits/FINAL_REVIEWER_CLOSURE_MATRIX.md` **for the current candidate
only**. The original review source is preserved at
`review/second_round_reviewer_comments.txt`. The source labels itself
“Initial submission” while discussing a revision; the package records that
ambiguity and does not infer an editor decision or an unprovided review.

| Reviewer issue | Candidate response and evidence | Current disposition |
|---|---|---|
| R1.1 — Visible color shifts/repetition; full objects, fixed/unmodified controls, unseen baked views, seams, practical value | The existing sampler-conformant GLB-native endpoint covers 20 UV-supported objects × 8 stored conditions × 11 unseen views with mixed endpoint effects. Fresh C adds a six-strategy image-space gallery over 300 objects, but no new baking, camera/sampler validation, human answers, seam validation, or full PBR result. Four old GLB objects lack UVs. | **PARTIAL / claim bounded.** The image gallery does not establish perceptual material fidelity or exported 3D quality; unseen base-color and seams remain bounded/open. |
| R1.2 — Same-protocol disjoint main-adapter evaluation, addressing the submitted +0.96 dB claim | The pooled +0.96 dB is retired as independent confirmation. strict-276 GC3−GFL remains a retrospective pair with incomplete legacy provenance; Fresh B's +0.502 dB pair was selected after unblinding. The new Fresh C cohort (N=300) supports its unchanged C3−GFL FG-PSNR primary: +0.522 dB [0.404, 0.641], p=5.70e−16, with 68.7% favorable objects. It is revision-era evidence, not an original-preregistration replication. | **PARTIAL, materially strengthened.** The new cohort closes the frozen image-space run, but does not establish the original submitted estimate, human fidelity, or broader 3D quality. |
| R1.3 — Distinguish texture variation from fidelity | Variation proxies are described as diagnostics only. Author visual review remains descriptive; no human responses exist. LLH human-fidelity claims have been withdrawn. | **CLOSED BY CLAIM REDUCTION, conditional on editorial acceptance.** The manuscript does not infer fidelity from variation metrics. |
| R1.4 — Paired intervals, Edge-SSIM trade-off, no equivalence from zero-crossing CI | Paired intervals and Edge-SSIM are reported. Fresh C's LLH−linear FG-PSNR interval crosses zero with no equivalence margin, while its FG-LPIPS difference favors linear after the six-test Holm correction. No broad non-inferiority/equivalence claim is made. | **SUBSTANTIALLY ADDRESSED.** The named comparisons remain endpoint-specific; historical C3 evidence retains its provenance limits. |
| R1.5 — FAC reproducibility | FAC is omitted from the candidate and contributes no positive or negative evidence to its claims. The response draft states that FAC would need a complete release if reinstated. | **CLOSED BY SCOPE REDUCTION, conditional on acceptance.** No FAC reproducibility claim remains. |
| R2.1 — Novelty beyond manually selected schedules | Candidate cites Scheduled Style Injection and narrows contribution to the tested MVPainter-style residual/cap path, residual measurement, object-level heterogeneity, and bounded texture endpoints. E5's 174-generation development pilot passed numerical realization but found shallow cap exceedance on 30.4% of steps at the smallest tested perturbation; it provides no quality or dose-independent mechanism evidence. | **BLOCKING EDITORIAL JUDGMENT.** Scope correction and technical feasibility do not prove contribution sufficiency. Keep interactions conditional on the named profile/caps; do not use E5 to imply a matched-dose mechanism. |
| R2.2 — CAI may formalize a post-hoc schedule | CAI is not presented as an independently predictive derivation or as the source of an optimum. | **CLOSED BY CLAIM REDUCTION.** |
| R2.3 — Cross-backbone generalization | MV-Adapter (98 evaluable objects) and MVDiffusion (75-object CPBlock interface) are reported separately; no pooled effect or architecture-causal inference. | **CLOSED BY CLAIM REDUCTION for broad transfer claims.** General transfer is not established. |
| R3 — Favorable review | No separate actionable issue is listed in the supplied text. | **No open item recorded.** It does not waive R1/R2 concerns. |

## Overall reviewer disposition

The page/line-mapped response candidate remains a working artifact and is not
rewritten before the scientific evidence freeze. Fresh C and the separately
locked LLH/linear addendum have now passed their own 300-object integrity gates;
the 28-check direction/Holm audit and final comparison gallery also pass. The
results strengthen only bounded image-space comparisons and expose object and
endpoint trade-offs. Human fidelity remains unmeasured, the new 24-object GLB
bake/camera/sampler gate is open, and two existing visual derivatives still
have unresolved source licensing. E5 remains a technical feasibility result;
E6 stopped before Fresh D. SSI remains close prior art, so methodological
contribution adequacy is still a blocking editorial judgment. The compact
clean-checkout rebuild passes, but full historical GPU-output reconstruction
remains partial. Therefore reviewer closure is **PARTIAL**, not closed.

The updated concern→direct-evidence→exact-edit map is maintained separately in
`REVIEWER_CLAIM_IMPACT_MATRIX_20261006.md`; the source-linked Fresh C packet is
indexed in `../evidence/audits/FRESH_C_EVIDENCE_PACKET_INDEX_20261006.md`. The
28-check sign/Holm audit is current and passes. These files do not close the
remaining human, valid new-3D, rights, or R2.1 venue-judgment gates.
