# Linear-schedule direction erratum — 2026-10-06

## Controlling correction

The 300-object Experiment C pairwise analysis defines each estimate as
`layer_llh − gen_linear`; its LLH rows came from the sibling `campaign_B1B2`
run and its linear rows came from `campaign_C`. A source-row reconstruction
confirmed identical UID sets, object indices, per-object seeds, and all six
shared-input hashes for **300/300 objects**. The two run manifests also agree
on object-list hash, runner hash, checkpoint, target views, sampler, latent
seed, and step count. Both older manifests have a null config hash, so the
legacy configuration identity is not cryptographically complete. See
`CAMPAIGN_C_LLH_LINEAR_DIRECTION_AUDIT_20261006.md`.

The raw result is **+0.001226 FG-LPIPS** (95%
object-bootstrap CI **[+0.000692, +0.001816]**, positive-delta fraction
54.7%); the registered 16-test
Holm family gives **p=0.0016**. Because LPIPS is lower-is-better, the positive
contrast favors endpoint-matched generic linear, not LLH. On FG-PSNR the same
contrast is +0.0049 dB (95% CI [−0.0350, +0.0469], Holm p=0.8148): no LLH
advantage is established, and no equivalence margin was specified.

The pairwise JSON, C Holm family, source rows, and reconstruction audit are
the numeric authorities. Compact copies of both upstream campaigns and
file-level hashes for all original prediction/residual payloads are in
`data/campaign_B1B2_prior/` and `data/campaign_C_prior/`. The 1006 copy of the
older narrative is preserved unchanged at
`evidence/audits/superseded/AUTHORITATIVE_GENERIC_SCHEDULE_REPORT_AS_RECEIVED.md`.

## Superseded prose and downstream handling

The older `final/round2/scientific_validation_v3/AUTHORITATIVE_GENERIC_SCHEDULE_REPORT.md`
uses a negative LPIPS sign while declaring LLH-minus-schedule contrasts and
describes LLH as “slightly better” except for this comparator. That sign and
interpretation are superseded here; the historical file is preserved to keep
the audit trail intact. Do not cite that prose for the registered C
LLH-versus-linear direction.

The existing B extension report, negative-result ledger, and current 1006
candidate's B paragraph already use the correct direction for B: its
post-lock 150-object same-cohort sensitivity also favors linear on FG-LPIPS
(LLH−linear +0.0011, 95% CI [+0.0004, +0.0019], Holm p=0.0024). B remains
post-lock and is not pooled with C. The reviewer-response candidate does not
currently state the C generic comparison; it must be updated from the frozen
Fresh C/addendum analysis before delivery. No submitted manuscript or
reviewer-response source is edited by this erratum.

## Correction scope

- **Corrected now:** evidence authority and the current interpretation of the
  registered C and post-lock B numeric results.
- **Already directionally correct:** `NEGATIVE_RESULT_LEDGER.md`,
  `FINAL_GENERIC_SCHEDULE_COMPARISON.md`, and the B discussion in
  `1006/manuscript/main_1006.tex`.
- **Must be populated after Fresh C:** the current candidate manuscript,
  comparison figure/table, and reviewer response must include the C
  contrast, preserve the B cohort label, and use lower-is-better LPIPS signs.
- **No claim allowed:** LLH is equivalent to linear, either schedule is a
  universal winner, or the small LPIPS difference establishes perceptual
  fidelity.
