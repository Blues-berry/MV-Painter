# Evidence closure audit — selected texture-boundary evidence

## Decision

`codex/evidence-closure-audit-20261005` is `SOURCE_READY` and is integrated
selectively. Its complete history is not merged: it has 161 source-only
commits, about 7.77 GB of unique uncompressed blobs, and a 42,742-path tree
delta that would replace or remove active 1008 and 1009 content. The original
source HEAD remains recoverable from the local archive ref recorded below.

The main evidence matrix already states the Fresh Confirm 300 texture boundary,
but main did not contain the paired per-object inputs for this exact cohort.
The 150-object Fresh Confirm B tables are a different cohort and cannot stand
in for it. This bundle keeps only the 300-row paired metrics and GT-only
descriptors needed to reproduce the boundary. It excludes images, GLBs,
embeddings, checkpoints, caches, residual traces, and the other five B3
conditions.

## Source and pairing checks

- Source branch HEAD: `7e659c7e5695ecc7ea2a0fbd80f2110289b2804a`.
- Local recovery ref: `refs/archive/codex/main-unification-20261009/local/heads/codex/evidence-closure-audit-20261005`.
- Cohort: 300 unique UIDs; the LLH and native GFL tables match the frozen
  `FRESH_CONFIRM_300` UID set exactly, with no disjoint rows.
- Both manifests report the same object-list SHA-256
  `b81bd142c0dbe04b6adaef1260a61c33eb1ef93b85c8a7cf5dba2244710f0673`,
  checkpoint SHA-256
  `0618d6b284ab47aa16d7a89dc447f5ba4455ff6c9d918e5e129478a99e0114c0`,
  runner SHA-256
  `7a46d8710f26666445c3ae6f53a5dbadac1d5e7573cc5f979d21af66e3b422ba`,
  seed 42, 256×256 resolution, 50 steps, six `unique6` views, and the same
  sampler and protocol. The four GT descriptor columns agree row by row across
  the two conditions. The source manifest with machine-absolute file paths is
  not copied; its content hash and relevant provenance are recorded in
  `SOURCE_HASHES.json`.

## Reaggregation and limits

The pairwise LLH−GFL FG-PSNR mean is +1.2877358 dB (95% bootstrap CI
[+0.9382723, +1.6345938]); the source output is reproduced from the selected
rows. The GT HF-energy association is approximately −0.691, and the fixed
Laplacian-variance quartiles reverse from +4.14 dB / 92% LLH wins in Q1 to
negative mean differences in Q3 and Q4. See `analysis_result.json` for the
CPU-only reaggregation.

The old decision report overstates the multiplicity result as all ten tests
rejected. The preserved source JSON has no Holm results and includes an
FG-LPIPS-versus-coverage bootstrap tail estimate of 0.0506. Recalculation with
the locked ten-test Holm family and a plus-one Monte Carlo correction rejects
9/10 tests; the coverage/FG-LPIPS test remains above 0.05. The source script
also called the positive-delta rate a `win_rate` for lower-is-better FG-LPIPS;
the reaggregation names the sign rate explicitly and computes LLH-better rate
using the correct metric direction.

The archived `PRIMARY_HYPOTHESES.md` contains H5 before the archived result
commit. The current main `B_MULTIPLICITY_FAMILY_LOCK.md` separately labels its
family lock retrospective after prior outcome exposure. This timing
classification discrepancy is recorded for later scientific reconciliation;
the old decision report's stronger wording is not imported as current paper
authority. The quantitative association and its cohort scope are retained.

## Paper impact

`PAPER_IMPACT=DIRECT`: the result can affect the failure/applicability
discussion, but the active 1008 manuscript and response letter do not yet state
this specific Fresh Confirm 300 boundary. No TeX, figure, response, or
submission file was changed in this branch audit. Revisit manuscript wording
after the remaining evidence branches are reviewed; do not describe the result
as universal or claim all ten associations passed Holm.

## Validation

Run `python analyze_texture_boundary.py paired_texture_boundary.csv
analysis_result.json` from this directory. The audit verified 300 paired
objects, source-table pairing, GT descriptor equality, the +1.2877358 dB
paired mean, and the quartile pattern. No model inference or GPU work was run.
