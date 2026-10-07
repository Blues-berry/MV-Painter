# Reviewer-gate remediation action log — Fresh C

**As of:** 2026-10-06 08:08 UTC

**Original manuscript:** preserved; no edits made to the submitted 01549 source.
**Fresh C method outputs:** none. Asset rendering and cohort freeze are not
complete.

## Why this work was started

The earlier strict-276 GC3−GFL comparison is retrospective, was not a registered
primary contrast, and lacks a complete legacy input-hash/common-runner chain.
Fresh B is disjoint for its registered LLH contrasts, but its GC3−GFL comparison
was added after unblinding. Neither result closes Reviewer 1.2's request for the
main adapter under the same held-out protocol.

The 508 previously screened local candidates are exhausted by Fresh300 and
Fresh B, so the remedy is a new Objaverse v1 candidate source pinned to a
specific repository revision. The locked protocol is
[`FRESH_C_C3_CONFIRMATION_PROTOCOL_20261006.md`](../protocols/FRESH_C_C3_CONFIRMATION_PROTOCOL_20261006.md).

## Work completed before generation

- Verified two idle RTX 5090 devices and adequate `/4T` capacity.
- Rechecked the frozen Fresh B runner, main adapter wrapper, data utilities,
  generation implementation, metric implementation, checkpoint, and config
  hashes against their recorded values.
- Expanded the historical exclusion union to include non-hexadecimal and
  hyphenated source IDs. The resulting 2,514 normalized exclusions cover the
  previous 2,006-entry audit and include all 508 members of the consumed local
  candidate pool plus all V3 result-ledger UIDs.
- Pinned Objaverse v1 to revision
  `21e4e142159e2153706c23a3a02e55cec5591cea`; froze a random-order queue of 600
  screen candidates and 400 reserve candidates under seed `20261006`.
- Applied an allowlist of `cc0`, `by`, and `by-sa`. The frozen queue contains
  973 BY, 23 BY-SA, and 4 CC0 assets. Attribution data is retained. Raw GLBs and
  rendered object panels are excluded from the public package unless their
  individual redistribution rights are cleared.
- Candidate selection used source IDs and license metadata only. No Fresh C
  method output or comparative image-quality value has been generated or used.

## Input screen update — 2026-10-06

- All 600 frozen screen assets downloaded from the pinned revision; the
  manifest records zero download failures. The first-batch script hash was
  recovered from the pre-outcome package commit because the active process had
  loaded the pre-update source before reserve-batch provenance was added.
- Hash/geometry audit checked 1,965 local historical GLBs: 594/600 new assets
  have valid geometry, six are invalid, and none is byte-identical to the
  historical inventory or another new candidate. The 594 technical candidates
  exceed N=300, so the locked reserve pool is not required so far.
- Rendering 17 views, depth conversion, pixel-level deduplication, foreground
  coverage checks, and final cohort freeze are underway. No inference has
  started. See `FRESH_C_INPUT_SCREEN_20261006.md` for hashes and exact limits.
- A pre-freeze code review found the old cohort selector could stop at N=276–299
  before using the protocol's frozen reserve queue. The selector was corrected
  before cohort freeze or method output: it now requires N=300 or exhaustion of
  all 1,000 candidates before accepting a reduced cohort. Pure boundary tests
  pass for the 275/276/299/300 cases; selection order and the statistical plan
  are unchanged.
- At 07:54 UTC the seven required runner, adapter, data, generation, metric,
  checkpoint, and config hashes were rechecked and matched the Fresh C protocol.
  Two RTX 5090 devices were visible and idle for the later launch; no inference
  started.
- The active input render process started at 07:32:25 UTC using preparation
  script SHA-256 `cfd57c764209dba14c7f16c8eceb7878410d29d1b9e22d17d6beb83ed7239b74`.
  Later edits changed the cohort-freeze branch and added reserve-stage recording;
  they did not alter the already-running render function or its Blender settings.
  `data/fresh_c/FRESH_C_RENDER_STAGE_IDENTITY.json` records the loaded render
  source hash, 594-UID input list, renderer binary/script/HDRI hashes, and start
  time separately from the future cohort-freeze code hash.

## Execution sequence

1. Download the 600 frozen screen assets from the pinned revision. **Complete:**
   600/600 downloaded; 594 pass basic geometry checks.
2. Reject failed GLB loads, invalid geometry, byte-identical historical assets,
   incomplete 17-view renders, coverage failures, and exact decoded-pixel
   duplicates with historical inputs. If fewer than 300 remain, use the next
   locked reserve block without inspecting method outputs.
3. Freeze the selected 276–300 UID cohort, file/pixel hashes, and attribution
   before inference. Stop without method outputs if fewer than 276 survive.
4. Run only `no_adapter`, `native_gfl`, `native_gfh`, and `native_gc3` with the
   unchanged runner, checkpoint, config, cap semantics, six views, scheduler,
   reference construction, and metric implementation.
5. Pass the full row, input-hash, prediction, residual-log, cap-trace, and
   finite-value integrity gate before calculating the preregistered primary
   and Holm-adjusted secondary comparisons.

## Reviewer closure effect and residual blockers

This can close the *new-object evidence* part of R1.2 if the protocol integrity
gate passes; the follow-up remains a revision-era prospective test motivated
by already-seen results, not the original preregistered replication. A negative
or uncertain result will be reported and the general C3 superiority claim
withdrawn.

Fresh C alone does not close R1.1/R1.3 (human fidelity and broad 3D appearance),
R1.5 (portable paper-wide rebuild), or R2.1 (whether the narrowed,
MVPainter-specific empirical contribution is substantial enough after
Scheduled Style Injection). No language change can substitute for those
separate judgments. Human response data remain pending from the user; there has
been no participant contact or distribution.

The final readiness verdict remains HOLD until all remaining gates have a
defensible evidence disposition, the 1006 paper and response are rebuilt only
after scientific freeze, and the final package passes the release checks.
