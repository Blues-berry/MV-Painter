# Reviewer closure against the 1006 candidate — 2026-10-06

This matrix supersedes the pre-rewrite disposition in
`evidence/audits/FINAL_REVIEWER_CLOSURE_MATRIX.md` **for the current candidate
only**. The original review source is preserved at
`review/second_round_reviewer_comments.txt`. The source labels itself
“Initial submission” while discussing a revision; the package records that
ambiguity and does not infer an editor decision or an unprovided review.

| Reviewer issue | Candidate response and evidence | Current disposition |
|---|---|---|
| R1.1 — Visible color shifts/repetition; full objects, fixed/unmodified controls, unseen baked views, seams, practical value | Supplement has the GT-stratified 24-object visual panel. The sampler-conformant GLB-native endpoint reports 20 UV-supported objects × 8 stored conditions × 11 unseen views and mixed endpoint effects. Four no-UV objects are excluded; no rebake, full PBR, seam validation, or LLH human responses exist. No overall 3D winner is claimed. | **PARTIAL / claim bounded.** Unseen base-color views and controls are shown. Perceptual material fidelity and seams remain unverified; editor may require more. |
| R1.2 — Same-protocol disjoint main-adapter evaluation, addressing the submitted +0.96 dB claim | The pooled +0.96 dB is retired as independent confirmation. strict-276 GC3−GFL is reported as retrospective with seven endpoints and incomplete legacy provenance. On disjoint FRESH_CONFIRM_B, native-GC3−native-GFL FG-PSNR is +0.502 dB [0.342, 0.663], but that pair was selected after B unblinding and was not registered. | **PARTIAL.** Adds independent-object cohort data, but not prospective/registered confirmation. A new confirmatory cohort requires separately sourced assets. |
| R1.3 — Distinguish texture variation from fidelity | Variation proxies are described as diagnostics only. Author visual review remains descriptive; no human responses exist. LLH human-fidelity claims have been withdrawn. | **CLOSED BY CLAIM REDUCTION, conditional on editorial acceptance.** The manuscript does not infer fidelity from variation metrics. |
| R1.4 — Paired intervals, Edge-SSIM trade-off, no equivalence from zero-crossing CI | Paired intervals are reported; strict-276 Edge-SSIM appears for both GFL and GFH contrasts; practical margins are restricted to the prespecified LLH−LFM-exact endpoints. No broad non-inferiority/equivalence claim is made. | **SUBSTANTIALLY ADDRESSED.** The historical C3 comparisons remain nominal retrospective supplements. |
| R1.5 — FAC reproducibility | FAC is omitted from the candidate and contributes no positive or negative evidence to its claims. The response draft states that FAC would need a complete release if reinstated. | **CLOSED BY SCOPE REDUCTION, conditional on acceptance.** No FAC reproducibility claim remains. |
| R2.1 — Novelty beyond manually selected schedules | Candidate cites Scheduled Style Injection and narrows contribution to the tested MVPainter-style residual/cap path, residual measurement, object-level heterogeneity, and bounded texture endpoints. E5's 174-generation development pilot passed numerical realization but found shallow cap exceedance on 30.4% of steps at the smallest tested perturbation; it provides no quality or dose-independent mechanism evidence. | **BLOCKING EDITORIAL JUDGMENT.** Scope correction and technical feasibility do not prove contribution sufficiency. Keep interactions conditional on the named profile/caps; do not use E5 to imply a matched-dose mechanism. |
| R2.2 — CAI may formalize a post-hoc schedule | CAI is not presented as an independently predictive derivation or as the source of an optimum. | **CLOSED BY CLAIM REDUCTION.** |
| R2.3 — Cross-backbone generalization | MV-Adapter (98 evaluable objects) and MVDiffusion (75-object CPBlock interface) are reported separately; no pooled effect or architecture-causal inference. | **CLOSED BY CLAIM REDUCTION for broad transfer claims.** General transfer is not established. |
| R3 — Favorable review | No separate actionable issue is listed in the supplied text. | **No open item recorded.** It does not waive R1/R2 concerns. |

## Overall reviewer disposition

The page/line-mapped response candidate is in
`review/response_to_reviewers_candidate.md`; it is not yet a final editor
letter because the scientific text, asset terms, and submission metadata are
not frozen. The candidate resolves several wording and statistical overclaims and adds a
GLB-native unseen-view endpoint plus a retrospective C3/GFL comparison on a
disjoint object cohort. A separate revision-era Fresh C3/GFL follow-up has
downloaded its 600 locked screen assets; 594 pass basic geometry checks, and
164/594 had complete 17-view image/normal/camera render products at the 09:06
UTC checkpoint. Depth conversion, decoded-pixel deduplication, coverage checks,
and cohort freeze remain in progress. It has generated no method outputs. E5 is a
development-only technical diagnostic. The candidate does not establish human-perceived fidelity,
prospective C3 confirmation, seam consistency, full-PBR quality, or
methodological novelty accepted by the venue. A fresh sparse checkout of the
published 1006 commit passes package checksums and rebuilds the compact
analyses, tables/figures, and LaTeX; omitted historic inference payloads leave
full end-to-end GPU regeneration partial. The source-license recheck still
cannot clear two panel assets (empty license metadata; unavailable endpoint).
The response in
`review/response_to_reviewers_draft.md` remains the earlier working draft.
Therefore the reviewer gate is **PARTIAL**, not closed.
