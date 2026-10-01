# Historical Result Exclusion Reason (final_audit_20261001, Phase 1.3)

Decision date: 2026-10-01. Subject: the archived "official layer-LHL" strict-276 record
(`rescued_tmp_20261001/official_lhl_v2_merged/per_object_metrics.csv`, FG-PSNR mean
14.7763).

## Ruling — Case B

> **Historical record removed from active evidence because complete provenance cannot
> be guaranteed.**

Per the audit plan, Case B requires that no root cause be asserted and no explanatory
mechanism be offered for the discrepancy. The record is excluded from every quantitative
claim, table, comparison, and narrative reference. This status does not change any
current paper claim: all Round-2 conclusions were already built exclusively on
same-runner, seeded, paired comparisons, in which the only layer-LHL rows are the frozen
confirmation replica (mean 12.9743, `object_seed = 42+idx`).

## Scope of what the forensics did establish (facts, not cause)

These facts motivated the Case B choice and bound what may be said about the record:

1. The archived record is internally heterogeneous: it is a merge of two concurrent
   processes whose same-object agreement with the frozen protocol differs by +3.23 dB
   (head block) vs +0.38 dB (tail block).
2. Generated-content texture statistics are systematically lower than the frozen
   protocol in both blocks (Laplacian variance 3.3× / 2.1× lower), while GT-side
   statistics are bitwise identical — the divergence is in generation, not evaluation
   targets.
3. Reference-preprocessing randomness is quantitatively excluded as an explanation of
   the mean gap (R0/R1 realization change moves absolute means ≈0.03 dB).
4. Checkpoint, object list, evaluation-kernel code, metric implementation, schedule
   values, steps, seed, and view mode are all hash- or value-identical to the frozen
   protocol.
5. The exact execution state of the archived processes is unreconstructible: the runner
   is an out-of-repo script last modified mid-session; the dataset file carried
   same-day working-tree modifications committed 3 hours later (`78c871f`); no
   per-object realization, scale, or residual log exists.

Points 1–5 are factual audit findings recorded in
`ARCHIVED_LHL_PROVENANCE_AUDIT.md` and `archived_vs_current_runner_diff.md`; none of
them names a mechanism, consistent with Case B.

## Corrections this ruling supersedes

- Earlier wording (EVAL_AUGMENTATION_AUDIT §4, 2026-09-30) attributed the archived
  record's failure to "the UNSEEDED realization". That attribution is retired: unseeded
  realization explains cross-restart irreproducibility (per-object r = 0.66), not the
  mean-level gap. The ruling of that audit (transform = legal inference preprocessing;
  frozen realizations required) is unaffected.

## Standing consequences

1. The archived record may appear in the paper only as provenance/audit history, never
   as a numeric result.
2. The "FG-PSNR ≈14.78" figure must not be compared against, or averaged with, any
   frozen-protocol number.
3. If a reviewer asks about the archived number, the response is the Case B sentence
   above plus the pointer to this audit directory.
4. No rerun of the archived configuration is required or desired; the frozen
   confirmation replica already occupies its evidentiary role.
