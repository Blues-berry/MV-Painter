# Independent novelty and reviewer-acceptance review

Review date: 2026-09-29 UTC  
Scope: read-only review of `final_round2.tex`, `supplementary_round2.tex`,
`response_letter_round2.md`, and the E0-A/E0-B/E0-D/E1 evidence files.  No GPU,
model inference, metric regeneration, or manuscript edit was performed.

## Executive decision

**Decision: needs targeted revision.**

The evidence package is substantially more honest and auditable than the prior
version, and most of the requested reviewer corrections are present. It is not
yet ready for author review because one active abstract sentence overstates the
LHL result, the R1 failure-case requirement is answered only at aggregate level,
and the reproducibility package still has naming/provenance gaps that are
already documented by E0-B/E0-D but are not fully surfaced in the delivery
documents.

This is not a ``not ready'' judgment on the underlying evidence. It is a
limited, fixable editorial and evidence-boundary revision before author review.

## 1. Innovation and novelty assessment

### TCAS as an algorithmic method: **weak to weak--moderate**

The core operation is a three-stage, training-free residual-scale schedule

\[
(s_e,s_m,s_l)=(1.25,2.50,1.25),
\]

applied to a fixed geometry adapter. This is a concrete and reproducible
implementation, but the current evidence does not establish a new learned
operator, a theoretically derived schedule, a budget-normalized optimum, or a
transferable selector. The manuscript itself acknowledges that the comparison
uses 17/16/17 steps with different scale sums, squared-scale sums, and residual
norms. The LLH follow-up counterexample further weakens any claim that the
low--high--low pattern is uniquely correct.

The related-work framing distinguishes adapter residual scaling from CFG
scheduling, which is useful, but a different injection mechanism alone does not
make the fixed low--high--low heuristic a strong method novelty. The present
method contribution is therefore best described as a simple inference-control
implementation whose usefulness is adapter- and protocol-dependent.

### CAI: **weak as a selector; moderate as a measurement/audit framing**

CAI is correctly presented as an empirical diagnostic rather than a theorem.
The probe-to-holdout nomination and the explicit stage-placement follow-up make
the stage-utility question reproducible. The fixed-GT SSIM decomposition and
the separation of pre-save versus saved-artifact metrics are meaningful
measurement contributions.

However, the second-backbone audit leaves CAI
`undefined_set_valued`, and the main follow-up contains an LLH result that is
better than LHL on all six non-SSIM metrics and on saved-artifact Full-SSIM.
Consequently, CAI is not demonstrated as a unique or portable schedule
selector. The defensible overall novelty is **moderate as a bounded empirical
mechanism/measurement study, but not strong as a new scheduling algorithm**.

## 2. R1 acceptance check: practical quality and real 3D output

### Correctly answered

- **Image quality versus fixed-low:** the strict-276 clean-v2 table is
  accurately reported as non-dominating. C3 is below fixed-low on Full-PSNR
  (14.875 vs. 15.086), FG-PSNR (6.763 vs. 7.030), and FG-SSIM (0.348 vs.
  0.355); it is close on FG-LPIPS (0.201 vs. 0.202) and Edge-SSIM (0.500 vs.
  0.500). The response letter correctly withdraws a practical-superiority
  claim.
- **Complete GLB path:** the 48 object--condition exports and 528 unseen-view
  rows are reported consistently with E0-D. The response and manuscript also
  correctly state that this is an operational, stratified 12-object case
  study, not a 276/300-object 3D generalization result.
- **Real 3D quality conclusion:** the reported baking means correctly show no
  C3 advantage over fixed-low: masked PSNR is 5.638 for C3 versus 6.001 for
  fixed-low, while no-adapter is 11.824. CIEDE2000 and FG-LPIPS likewise do
  not support C3 superiority.
- **Known limitations:** absent generated GT bake, unavailable DISTS,
  source-fusion colour inconsistency, and `obj_0048` Blender reindexing are
  correctly acknowledged.

### Still insufficient for the R1 failure-case request

The package gives aggregate failure evidence but not an object-level failure
case presentation. E0-D identifies concrete cases that should be surfaced in
the paper or supplementary material, including `obj_0078` and `obj_0082` with
very low raw texture coverage, and `obj_0048` where approximately 84.41% of the
final texture coverage is inpainting after raw coverage of about 0.1547. The
report also notes cross-view/source-fusion colour inconsistency and the
object-level C3-versus-fixed-low results: 0/12 wins on masked PSNR, 0/12 on
CIEDE2000, and 2/12 on FG-LPIPS.

At least a compact object-level table or figure with these IDs, coverage,
inpainting fraction, and one representative unseen-view failure is needed.
Without it, the response answers “does the pipeline exist?” and “does the
cohort show a C3 mean advantage?” but only partially answers R1's explicit
request for complete-object quality and failure cases.

## 3. R2 acceptance check: method contribution and controls

### Correctly answered

- **LLH counterexample:** the stage follow-up reports LLH as better than LHL
  on all six non-SSIM metrics. Saved-artifact Full-SSIM is 0.88313 for LLH
  versus 0.88144 for LHL; the C3-minus-LLH interval
  `[-0.00205,-0.00134]` is correctly not interpreted as equivalence.
- **Non-strict budget:** the paper, supplement, and response letter state the
  17/16/17 partition and the distinct means/squared-scale sums. They do not
  call the result a strict equal-budget causal isolation, which is correct.
- **Fixed-GT SSIM:** the decomposition fixes the GT branch and separates the
  large fp16-to-fp32 effect (+0.03198) from prediction PNG quantization
  (-0.00036) and GT PNG serialization (-0.00007). It is correctly described
  as a saved 12-object diagnostic, not a retrofit of the historical 300-object
  table.
- **Second backbone:** the MV-Adapter audit separates high=1.50 from
  high=1.00, reports CAI as undefined/set-valued, and does not assert official
  pretraining UID disjointness. This directly addresses the requested
  generality boundary.
- **Mechanism language:** the active method and conclusion call the stage-role
  explanation a hypothesis and explicitly reject causal identification. This
  is appropriately calibrated.

### Required tightening

The abstract says that “LHL improves over fixed mean and HLL on the reported
metrics.” This is too broad. In the follow-up, LHL's Full-LPIPS is 0.190,
which is worse than fixed mean's 0.188; the defensible wording is “LHL improves
on selected targets over fixed mean and on the listed targets over HLL,” or a
similarly metric-specific statement. The conclusion already uses the safer
“several targets” wording; the abstract should match it.

The response letter and supplement call the MV-Adapter audit an “11-method”
cohort / “11 methods.” E0-B explicitly recommends “11 evaluated
conditions/schedules,” because the rows mix historical conditions and
follow-up diagnostics rather than 11 independent methods. This should be
corrected wherever it appears in the delivery package.

## 4. Active-claim and consistency audit

### Active claims that pass

- The main active results use the strict-276 clean-v2 panel and the separately
  labeled stage follow-up; the repeated C3 outputs are explicitly not pooled.
- The active tables' strict-276, stage, saved Full-SSIM, baking, and MV-Adapter
  values agree with the frozen evidence summarized by E0-A/E0-B/E0-D.
- The active conclusion rejects a unique CAI selector, universal LHL optimum,
  cross-backbone causality, and population-level 3D superiority.
- The old +0.96 dB, CLIP-IQA, and blinded-preference block is enclosed by
  balanced `\iffalse`/`\fi` pairs and is not active in the compiled TeX path.

### Residual consistency/provenance risks

1. **Protocol naming:** E0-B found that the original
   `results/holdout_exact_76/PROTOCOL.json` is absent. The available
   `run_config.json` and `paired_bootstrap_exact.json` provide partial
   traceability, but this gap is not explicitly disclosed in the response
   letter or supplementary provenance section.
2. **Baking smoke scope:** E0-D records GT-to-GT smoke evidence for two
   objects, while the formal 12-object generated batch has no GT bake; the
   delivery text says there is no 12-object GT bake but should also state the
   two-object smoke scope if it is used to support pipeline sanity.
3. **Baking provenance:** E0-D notes blank `source_asset_sha256` fields and
   that the seam scalar lacks a saved seam-pair count. The current text is
   appropriately conservative about seam-free output, but the reproduction
   note should retain these audit limitations.
4. **Source archive risk:** historical claims remain in the `.tex` source
   behind `\iffalse`. They are not active claims after balanced parsing, but
   they should be removed or clearly marked as non-deliverable archive content
   before submission to avoid accidental extraction or reviewer confusion.

## 5. Highest-priority targeted fixes

1. Narrow the abstract's LHL-versus-fixed-mean sentence to a metric-specific
   claim; do not imply an all-metric improvement.
2. Add object-level 3D failure cases to the paper/supplementary package,
   preferably `obj_0078`, `obj_0082`, and `obj_0048`, with raw coverage,
   inpainting fraction, and representative unseen-view evidence.
3. Replace “11 methods” with “11 evaluated conditions/schedules” in the
   response letter and supplement, and use the same terminology in table
   headers/captions where appropriate.
4. Add a short reproducibility note for the missing original holdout
   `PROTOCOL.json`, the available replacement artifacts, and the two-object
   GT-to-GT smoke scope.
5. Perform one final TeX compilation and claim scan after those edits; verify
   that the hidden historical archive is still excluded and that no old
   pooled/preference/CLIP-IQA numbers re-enter the active output.

## Final assessment

The revised work is best positioned as a **moderate empirical and measurement
contribution with weak-to-moderate algorithmic novelty**: it provides a useful
inference-control formulation, an auditable stage-placement protocol, and
important negative boundaries, but it does not establish a novel universal
schedule or a transferable CAI selector. R2 is largely addressed. R1 is
addressed for aggregate image quality and operational GLB tracing, but only
partially for complete-object quality and explicit failure cases. After the
five targeted fixes above, the package should be suitable for author review;
the present version should not yet be treated as the final submission-ready
revision.

## Final re-review after targeted fixes

Review date: 2026-09-29 UTC. This re-review again read the current
`final_round2.tex`, `supplementary_round2.tex`, `response_letter_round2.md`,
and E1 ledger without editing any of those files or starting GPU/model work.

### Fixes verified

- The active abstract now says that LHL improves on **selected targets**
  relative to fixed mean and HLL. It no longer implies an all-metric gain.
- Supplementary S4 now contains the requested object-level failure boundaries:
  `obj_0048`, `obj_0078`, and `obj_0082`, with raw coverage, inpainting
  fraction, fixed-low/C3 metrics, and the two-object GT-to-GT smoke scope.
- The response letter reproduces those failure cases and explicitly states
  that they are boundary examples rather than selected successes.
- The supplementary and response provenance now disclose the missing
  `results/holdout_exact_76/PROTOCOL.json`, the available
  `run_config.json`/`paired_bootstrap_exact.json` alternatives, blank source
  hashes, the missing seam-pair count, and the two-object GT smoke boundary.
- The manuscript, supplementary material, and response letter use
  evaluated-condition/schedule terminology for the MV-Adapter audit.
- Strict-276, stage-placement, saved-artifact Full-SSIM, fixed-GT, baking, and
  MV-Adapter numbers remain mutually consistent with the frozen evidence.
- The active TeX path has balanced `\iffalse`/`\fi` pairs (4/4). A static
  active-content scan finds no old +0.96 dB, CLIP-IQA, blinded-preference, or
  pooled-300-object claim. Both TeX documents compile successfully with
  `pdflatex` in the read-only check environment.

### Residual issues

1. **E1 ledger terminology is not fully synchronized.** The positive-claim
   row for the MV-Adapter audit still says “76-object/11-method frozen
   tables,” even though the supplementary material and response letter now
   correctly say “11 evaluated conditions/schedules.” This is the only
   remaining substantive claim-ledger inconsistency and should be corrected
   before the ledger is frozen for author review.
2. **Typesetting warnings remain.** The successful compilation reports large
   overfull boxes for the supplementary SHA-256/path strings and a roughly
   49pt overfull box around the main baking table. The generated PDF remains
   readable and compilation is not blocked, but the table/path layout should
   receive one final formatting pass before submission.
3. **Historical source archive remains in TeX.** The old pooled/CLIP-IQA/
   preference text is inactive and safely enclosed by balanced conditionals,
   but removing it or keeping it in a separate archive would reduce the risk
   of accidental reactivation or source-level reviewer confusion.

### Final reviewer coverage

R1 is now adequately answered at the evidence-boundary level: the package
reports non-dominance against fixed-low, traces the 48-GLB/528-view path, and
shows concrete low-coverage, heavy-inpainting, and exporter-limitation cases.
It still correctly refuses to claim population-level 3D superiority.

R2 is also adequately answered at the evidence-boundary level: LLH is retained
as a counterexample, 17/16/17 is not treated as equal budget or causal
isolation, fixed-GT SSIM effects are separated, and second-backbone CAI remains
undefined/set-valued with pretraining UID disjointness unverified.

The innovation judgment is unchanged: **weak to weak--moderate algorithmic
novelty**, **moderate empirical/measurement contribution**, and no evidence
for a strong universal schedule-selection method.

### Final status

**Final status: needs targeted revision.**

This is a narrow delivery-cleanup decision, not a request for new experiments.
After synchronizing the single stale E1 “11-method” phrase and performing the
last typesetting cleanup, the package is suitable for author review. No GPU or
model rerun is warranted by this re-review.

## Final confirmation

The final cleanup claims were independently rechecked on the current files.

- E1 now uses “76-object/11 evaluated conditions/schedules”; no stale
  “11-method” wording remains in the reviewed delivery files.
- The supplementary SHA-256 strings are split across lines, the long audit
  path is breakable, and the previous supplementary overfull boxes are gone.
- The main baking table is wrapped in `\resizebox{\columnwidth}{!}{...}` and
  the previous large baking-table overfull box is gone.
- Two read-only `pdflatex` passes completed successfully for both documents.
  No undefined citations or references remain, and no hard compilation error
  occurred. The remaining approximately 0.8--1.0pt frontmatter overfull boxes
  are template-level; the logs also contain ordinary underfull/geometry
  warnings but no material content overflow.
- The active-claim scan remains clean: the old pooled +0.96 dB, CLIP-IQA, and
  blinded-preference claims remain inactive and no new stale claim was found.

The residuals are therefore acceptable for an author-review package. The
innovation assessment is unchanged: **weak to weak--moderate algorithmic
novelty**, **moderate empirical/measurement contribution**, with no evidence
for a strong universal schedule-selection method.

### Final status: ready for author review

No further evidence correction, GPU experiment, or model rerun is required for
this review stage. Submission, camera-ready formatting beyond the accepted
template warnings, and any new experimental claim remain outside this
confirmation.
