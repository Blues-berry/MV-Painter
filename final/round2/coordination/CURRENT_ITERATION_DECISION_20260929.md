# Current iteration decision and paper-edit route

Date: 2026-09-29 UTC

This record consolidates the frozen round2 evidence and the later independent
residual-budget pilot. It is a decision record, not a submission authorization.

## Executive decision

Do not spend another large GPU budget trying to recover the unavailable
historical experiment or to force a new controller into the paper. The old
`+0.96 dB`, CLIP-IQA, and blinded-preference results cannot be used as clean-v2
evidence. The new residual-budget pilot does not establish a stable method
advantage either.

The highest-return route is an incremental revision that:

1. keeps TCAS as a concrete, training-free stage-control implementation;
2. weakens the contribution from “new/general schedule optimizer” to a bounded
   adapter-scoped stage-utility and failure-mode study;
3. uses the current strict-276, cross-backbone, and baking evidence with their
   exact limitations;
4. adds only targeted evidence needed for reviewer-facing gaps; and
5. removes every claim that depends on the unavailable historical data.

## Evidence inventory

### Keep as current paper evidence

- Clean-v2 main-adapter strict-276 panel: complete four-condition records,
  fixed protocol, paired statistics, and explicit pre-save versus saved-artifact
  Full-SSIM provenance.
- Stage-placement follow-up: fixed mean, HLL, LHL/C3, and LLH on the same
  object IDs. It supports that stage placement changes outputs, but LLH is a
  direct counterexample to a unique LHL optimum and the 17/16/17 partition is
  not strictly equal-effective-budget.
- Fixed-GT SSIM decomposition: fp16-to-fp32, prediction PNG, and GT
  serialization effects are separated on saved tensors. This is a credibility
  audit, not a new quality gain.
- MV-Adapter 76-object audit: useful as bounded within-backbone evidence;
  report the undefined/set-valued CAI result and the unknown official
  pretraining UID disjointness.
- Twelve-object Exact-GLB bake: useful for demonstrating that the GLB and
  unseen-view path runs. It is a stratified case study, not a population-level
  3D advantage; DISTS and a 12-object generated GT bake are unavailable.
- FAC controlled re-examination: negative extension evidence, best kept in the
  supplement or as a limitation rather than a main contribution.

### Keep only as internal negative evidence

- RB-TCAS unrestricted residual normalization: 12-object FG-SSIM improves, but
  visual outputs are visibly over-smoothed and LapVar collapses to 0.00845.
- TRB-TCAS trust-region pilot: 12-object results are plausible but not decisive
  and are not equal-budget against C3. In the equal-budget follow-up, HLL-eq
  has higher mean SSIM and LLH-eq has higher PSNR/lower MAE than TRB.

The pilot is preserved for reproducibility, but should not be added to the
paper as a claimed method improvement. It is a failed/unfinished design branch
that motivates future work on genuinely equal effective-budget control.

### Do not use as current evidence

- Historical pooled `+0.96 dB` claim.
- Historical human-preference and CLIP-IQA blocks whose exact checkpoint,
  cohort, or saved artifacts do not match the current clean-v2 evidence.
- Any statement that C3/LHL dominates fixed-low, LLH, or all texture metrics.
- Any statement that CAI uniquely predicts or selects LHL.
- Any population-level claim about real 3D texture quality from the 12-object
  bake.

## What the reviewers actually require

R1 is primarily a practical-quality request: whole-object visual comparisons,
fixed-low and no-adapter baselines, unseen-view baking, seams/coverage, and a
clear distinction between texture variation and texture fidelity. The current
package answers the operational path and aggregate limitations, but the paper
must visibly show the failure objects and must not turn the bake into a
superiority claim.

R2 is primarily a contribution/generalization request: explain why TCAS is more
than a hand-picked schedule and test whether the interpretation survives a
different backbone. The current evidence supports a reproducible stage
intervention and bounded within-backbone replication, but not a universal
algorithm or transferable selector. Claim reduction is therefore part of the
answer, not a substitute hidden behind stronger prose.

## Recommended paper route

### 1. Abstract and title-level positioning

Use “training-free inference-time adapter control” or “stage-utility study”
language. State that the evidence is adapter- and protocol-dependent. Do not
say that C3 is the best schedule, improves practical 3D quality, or generalizes
across backbones.

The abstract should say that the strict-276 audit finds stage sensitivity and a
shape--texture trade-off, while LLH and fixed-low are counterexamples to a
universal LHL advantage. The 12-object bake should be described as operational
feasibility only.

### 2. Introduction and contributions

Retain three defensible contributions:

- a concrete residual-scaling intervention that is simple and reproducible;
- a controlled stage-placement/metric-provenance audit exposing both gains and
  counterexamples; and
- a practical boundary analysis covering a different backbone and an actual
  GLB/unseen-view path.

Do not present CAI as the central algorithmic novelty. Present it as an
empirical diagnostic whose unique selection rule is undefined in the
cross-backbone audit.

### 3. Results and figures

Make the strict-276 panel the main numerical result. Keep the stage follow-up
as a separate panel and explicitly state that its nominal budgets differ.
Restore/retain full-object comparison figures with no-adapter, fixed-low,
fixed-high, C3, and LLH where available. Add the existing failure boundaries
`obj_0048`, `obj_0078`, and `obj_0082` with raw coverage/inpainting and unseen
views in the supplement.

Use the bake section to answer “does the real pipeline run?” rather than “does
TCAS improve 3D quality?” Report missing DISTS, absent generated GT bake,
source-fusion colour inconsistency, exporter reindexing, and stratified cohort
selection directly in the figure caption or paragraph.

### 4. Method and discussion

Keep the scale equation and exact discrete 17/16/17 boundaries. Replace
causal-sounding language with “consistent with” or “hypothesis.” State that
the current method has no learned parameters, no universal selector, and no
strict equal-effective-budget isolation.

Move the negative FAC result and residual-budget pilot to a limitations/future
work discussion. They show that a learned or normalized controller is not
automatically better, but they do not create a positive novelty claim.

### 5. Response letter

Answer R1 with the existing full-object/failure/bake evidence and explicitly
concede that fixed-low remains competitive. Answer R2 by separating:

- what is demonstrated: stage placement changes outputs under frozen protocols;
- what is not demonstrated: universal LHL optimality, CAI portability, and
  population-level 3D superiority; and
- what was changed: claim scope, provenance tables, failure cases, and
  cross-backbone caveats.

Do not argue that “adapter-dependent” by itself proves novelty. Explain that the
paper's contribution is the controlled, reproducible analysis and the explicit
failure boundary, then let the venue judge whether that empirical contribution
fits its scope.

## Minimal additional work worth doing

Only these targeted additions have a favorable cost/risk ratio:

1. synchronize the active manuscript, supplement, response letter, and claim
   ledger; remove inactive historical prose from the submission source rather
   than relying only on `\\iffalse` blocks;
2. add the existing object-level failure figure/table and full-object
   comparison grid;
3. freeze one compact cross-backbone table using the existing 76-object audit,
   with “evaluated conditions/schedules” terminology and all provenance limits;
4. run one final compile, table-number scan, hash/path scan, and active-claim
   scan.

A new dataset, a new large-scale controller sweep, or a new strict-276 TRB run
is not justified until a revised method has a pre-registered equal effective
budget and a clear acceptance criterion. The current pilot fails that gate.

## Current status

- Main worktree: preserved; the skeleton-validation agent's files/processes were
  not modified.
- Previous round2 GitHub snapshot: preserved.
- Pilot branch: `codex/adaptive-control-pilot-20260929`, containing commits
  `179b8ac` and `1b38679`; it is an experimental branch, not the paper branch.
- Pilot report: `/4T/tmp/mvpainter-adaptive-control/TRB_PILOT_REVIEW_20260929.md`.
- Current paper source has not yet been edited in this iteration. Editing should
  begin only after this claim route is accepted, in the order: Results/protocol
  → Method boundaries → figures/supplement → abstract/conclusion → response.

## Execution correction — 2026-09-29

The preceding route was too conservative about the residual-budget pilot. A
source audit found that the pilot used the legacy `test_objects_300.txt`
configuration and the dataset default `legacy_duplicate_top` view mode. It
also fixed the PyTorch seed but did not fix all Python/NumPy dataset-side
randomness. Consequently, its numerical rows are **exploratory and
non-strict**; they cannot be used either to reject TRB-TCAS or to claim a
method gain. This does not invalidate the clean-v2 evidence.

The user has explicitly authorized a two-week revision window with one finite
method-improvement attempt. The active route is therefore corrected to:

1. preserve TCAS as the mainline method and audit the formal clean-v2 entry
   points before changing paper claims;
2. complete the evidence matrix, deterministic-pairing checks, fixed-GT/colour
   diagnosis, and MV-Adapter provenance audit;
3. run a strict, pre-specified 24-object development pilot only after the
   protocol check passes, with unique6 views, fixed Python/NumPy/PyTorch seeds,
   shared batch and initial latent, explicit effective-budget accounting, and
   FG-LPIPS as the primary practical metric;
4. use the strict-276 holdout only for a locked confirmation if the development
   gate is passed; otherwise keep the pilot exploratory and do not merge it;
5. revise the paper around bounded, evidence-backed claims, retaining the
   negative cases and the fact that LHL is not uniformly best.

This correction supersedes the earlier statement that no new GPU experiment
was justified. It does not authorize a broad sweep: at most one finite TRB
revision is allowed, and the independent MVDiffusion validation agent remains
out of scope for this worktree.

## Scope adjustment — author instruction, 2026-09-29

Historical dataset and legacy-script imperfections are now treated as recorded
limitations in the spirit of the CAG-S-26-01549 revision handling. They are not
grounds for repeatedly reopening already validated prior results. Only a
defect that can change the interpretation of a **new** comparison should stop
that comparison. The execution priority is consequently new, reviewer-facing
evidence and a clearer method framing; provenance notes are logged once and
then left out of the critical path.
