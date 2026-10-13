# Targeted revision execution status

Updated: 2026-09-29 UTC

## Completed

- Corrected the decision record: the old TRB pilot is exploratory because it
  used legacy duplicate-top views and incomplete RNG control; it is not a
  method rejection.
- Added the reviewer/evidence/gap matrix.
- Audited the strict-276 list: 276 unique UIDs, recorded SHA-256, clean-v2
  `unique6` target views `[0, 15, 12, 16, 13, 14]`.
- Confirmed the formal main and stage-placement entrypoints declare unique6,
  shared initial latent semantics, fixed-GT float32 provenance, and fixed
  checkpoint identity.
- Added Python/NumPy/PyTorch seed control for future formal reruns. Existing
  frozen rows are not relabelled as reruns.
- Dry-ran the 276-object stage protocol successfully.
- Froze the existing MV-Adapter interpretation: implementation transfer and
  within-backbone stage sensitivity only; no cross-backbone benefit transfer.
- Restored/verified full-object comparison assets and generated two stage
  placement grids from the saved predictions for visual review.
- Added a strict TRB development protocol in the independent pilot clone.
- Recompiled the active manuscript source successfully with the repository's
  `cag.sty` path (`/tmp/final_round2.pdf`, 10 pages); only normal underfull box
  warnings remain. The first compile attempt without the template path was
  correctly treated as an environment error, not a paper result.

## Resolved / remaining

- The corrected 24-object TRB development pilot completed outside the sandbox
  on server GPU 0. The initial wrong-working-directory launch exited before
  model loading; the corrected run used the same protocol and completed all
  24 objects.
- The TRB gate failed against C3, so no locked holdout run was authorized.
- MVDiffusion remains with the independent skeleton-validation agent and is
  not modified by this execution.

## Intermediate pilot result

The first strict 24-object run completed with `unique6`, seed 42, 50 steps,
shared object batches/latents, and fixed-low/C3/HLL/LLH/TRB conditions. It is
an intermediate diagnostic because this branch reports probe metrics but not
the pre-specified FG-LPIPS primary metric or explicit calibration wall-clock.
The observed means show TRB below C3 on FG-SSIM and PSNR, while LLH is strong
on PSNR/MAE; no method-promotion decision is made from this run. A separate
LPIPS-enabled run is active and will provide the gate metric and timing.

At the latest external check, the LPIPS-enabled run had completed 9/24
objects and remained active on GPU 0. Its estimated completion window is
approximately 12:15–12:25 UTC on 2026-09-29, subject to per-object runtime.

The LPIPS-enabled run subsequently completed all 24 objects at approximately
12:15:52 UTC. Its gate result is recorded in
`TRB_DEV24_GATE_20260929.md`: TRB improves fixed-low but does not improve C3,
has roughly 2x inference cost because calibration is counted, and is therefore
stopped without a strict-276 holdout run.

## Phase 2

Phase 2 evidence was assembled in
`PHASE2_EVIDENCE_HANDOFF_20260929.md`. The cross-backbone package and R1
complete-object/CPU-bake evidence are ready for controlled manuscript
integration. The next phase is editing the results, supplement and response
letter from these frozen boundaries. That integration has now been performed;
no additional TRB GPU run is pending.

## Phase 3 progress

- Updated the response letter to include the bounded negative TRB pilot and
  its stop decision, while retaining the existing reviewer-facing concessions.
- Added the TRB negative pilot to Supplementary S7.
- Recompiled the manuscript and supplement successfully: 10-page manuscript,
  3-page supplement. No new numerical claim was added to the main results.
- Saved new author-review builds without overwriting the previous PDFs:
  `final_round2_author_review_20260929.pdf` and
  `supplementary_round2_author_review_20260929.pdf`.

## Phase 4

Final QA completed: both documents were recompiled, all PDF pages were
rendered, key pages and figures were visually inspected, and response-letter
numbers were cross-checked against the frozen evidence. The optional
repeat/order perturbation inference was not run because the final claims do
not assert exact repeatability or order invariance; this limitation is
recorded in `PLAN_EXECUTION_AUDIT_20260929.md`.

## Evidence rule

No pending pilot number may enter the manuscript, response letter, or claim
ledger until its run manifest records the object list/hash, unique6 views,
three RNG families, shared batch/latent, budget accounting, and primary
FG-LPIPS decision.

## Author direction — 2026-09-29

Following the CAG-S-26-01549 revision handling, historical dataset/file and
legacy-script imperfections are recorded as provenance limitations but are not
allowed to repeatedly block the new revision. The prior manuscript and its
existing experiments are treated as substantively reliable based on the
multi-party validation already completed; missing local files do not reopen
all historical conclusions.

For newly added experiments, the acceptance bar is narrower and practical:
the comparison must be correctly specified, reproducible enough to audit,
and directly relevant to the reviewer concern. Minor inherited dataset or
pipeline imperfections are logged first and corrected only when they can
change the new comparison's interpretation. The next work therefore proceeds
with the incremental method/cross-backbone evidence rather than another broad
historical provenance audit.
