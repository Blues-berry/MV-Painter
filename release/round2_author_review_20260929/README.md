# MV-Painter round2 author-review snapshot

This is a curated, immutable snapshot of the completed round2 evidence and
author-review package as of 2026-09-29. It is published separately from the
older `new0529` submission history; no previous manuscript, archive, or
branch is deleted or rewritten.

## Included

- `manuscript/`: the round2 manuscript, supplementary material, source TeX,
  and response letter.
- `coordination/`: the evidence freeze, claim ledger, audit reports, delivery
  acceptance, revision plan, and expert novelty review.
- `evidence/`: compact per-object CSV/JSON summaries for strict-276,
  stage-placement, baking, MV-Adapter, independent metric checks, and the
  fixed-GT SSIM decomposition. Raw model outputs, checkpoints, and full GLB
  collections remain local and are not redistributed.
- `visuals/`: four existing full-object comparison sheets retained as
  qualitative evidence. They document the observed failure boundary; they do
  not claim a C3 visual advantage over fixed-low.
- `protocol/`: the reproducibility protocol, schema, unique6 configuration,
  and frozen object lists.
- The current round2 evaluation/audit scripts under `geotex/`, plus the
  `target_view_mode=unique6` dataset compatibility change and LPIPS device
  handling fix.

## Scientific scope frozen in this snapshot

The package supports a bounded inference-control and measurement study:
stage intervention effects are measurable, but the evidence does not support
a universal CAI selector, a uniformly superior LHL/C3 schedule, or a claim
of improved real 3D texture fidelity. The baking evidence is reported as a
path-validation and failure-boundary result, with coverage, inpainting,
source-fusion, and missing generated-GT limitations explicit.

## Deliberately excluded

The separate new-skeleton/cross-backbone validation work is intentionally not
part of this snapshot. In particular, this commit does not include the
in-progress `mvdiffusion` tree, `CROSS_BACKBONE_VALIDATION.md`, the related
`scripts/cross_backbone_*` and MVDiffusion staging scripts, or their generated
preflight/output files. Those files remain in the original working tree for
the other agent and can be published in a later, independent snapshot.

No current-worktree deletions are included. The source worktree and the old
submission branch therefore remain unchanged by this release preparation.

## Verification

- The final PDFs and response letter are copied from the frozen round2
  author-review directory.
- Evidence files are copied by explicit path from the round2 freeze; no
  ignored raw output directory is committed wholesale.
- The release branch is intended for author review and archival backup, not
  automatic submission.
